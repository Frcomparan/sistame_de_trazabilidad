# Sistema de Eventos Dinámicos

[← Volver al índice](../README.md) | [← API REST](./06_api_rest.md) | [Cronograma →](./08_cronograma.md)

## 1. Introducción

El **Sistema de Eventos Dinámicos** es el núcleo del sistema de trazabilidad. Permite crear y configurar nuevos tipos de eventos sin modificar código, proporcionando flexibilidad máxima para adaptar el sistema a nuevas necesidades.

## 2. Concepto y Arquitectura

### 2.1 Separación de Definición e Instancia

```
┌──────────────────────────────────────────────┐
│          EventType (Definición)              │
│  - Define QUÉ campos tiene el evento         │
│  - Schema de validación (JSON Schema)        │
│  - Metadata (nombre, categoría, icono)       │
└──────────────────┬───────────────────────────┘
                   │ 1:N
                   ↓
┌──────────────────────────────────────────────┐
│            Event (Instancia)                 │
│  - Datos reales capturados                   │
│  - Payload en JSONB (validado contra schema) │
│  - Metadata (cuándo, dónde, quién)           │
└──────────────────────────────────────────────┘
```

### 2.2 Flujo de Trabajo

```
┌─────────────┐
│ ADMIN crea  │
│ EventType   │──┐
└─────────────┘  │
                 │ Define schema
                 ↓
┌──────────────────────────────────┐
│ Sistema genera formulario        │
│ dinámicamente desde schema       │
└──────────────┬───────────────────┘
               │
               │ Técnico captura
               ↓
┌──────────────────────────────────┐
│ Sistema valida payload contra    │
│ schema antes de guardar          │
└──────────────┬───────────────────┘
               │
               │ Si válido
               ↓
┌──────────────────────────────────┐
│ Event guardado en BD (JSONB)     │
└──────────────────────────────────┘
```

## 3. Componentes Principales

### 3.1 EventType (Modelo)

```python
# events/models.py
from django.db import models
import jsonschema

class EventType(models.Model):
    CATEGORIES = [
        ('riego', 'Riego'),
        ('fertilizacion', 'Fertilización'),
        ('fitosanitarios', 'Fitosanitarios'),
        ('labores', 'Labores Culturales'),
        ('monitoreo', 'Monitoreo'),
        ('brotes', 'Brotes'),
        ('clima', 'Clima'),
        ('cosecha', 'Cosecha'),
        ('poscosecha', 'Poscosecha'),
        ('mano_obra', 'Mano de Obra'),
        ('otro', 'Otro'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORIES)
    description = models.TextField(blank=True)
    schema = models.JSONField()  # JSON Schema
    version = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        """Valida que el schema sea JSON Schema válido"""
        try:
            # Validar sintaxis JSON Schema
            jsonschema.Draft7Validator.check_schema(self.schema)
        except jsonschema.SchemaError as e:
            raise ValidationError(f'Schema inválido: {e.message}')
    
    def validate_payload(self, payload):
        """Valida un payload contra este schema"""
        try:
            jsonschema.validate(payload, self.schema)
            return True
        except jsonschema.ValidationError as e:
            raise ValidationError(f'Payload inválido: {e.message}')
    
    def __str__(self):
        return f"{self.name} (v{self.version})"
```

### 3.2 Event (Modelo)

```python
# events/models.py
class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    event_type = models.ForeignKey(EventType, on_delete=models.PROTECT)
    field = models.ForeignKey('fields.Field', on_delete=models.CASCADE)
    campaign = models.ForeignKey('fields.Campaign', on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField()
    payload = models.JSONField()  # Datos según schema
    observations = models.TextField(blank=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        """Validación antes de guardar"""
        # Validar payload contra schema del EventType
        if self.event_type:
            self.event_type.validate_payload(self.payload)
        
        # Validar timestamp no futuro
        if self.timestamp > timezone.now() + timedelta(hours=1):
            raise ValidationError('El timestamp no puede ser futuro')
    
    def get_summary(self):
        """Genera resumen legible del evento"""
        # Lógica para generar resumen basado en payload
        return f"{self.event_type.name} - {self.field.name}"
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['field', '-timestamp']),
            models.Index(fields=['event_type']),
            GinIndex(fields=['payload']),
        ]
```

### 3.3 Schema Validator (Servicio)

```python
# events/validators/schema_validator.py
import jsonschema
from typing import Dict, Any, List

class SchemaValidator:
    """Validador de payloads contra JSON Schema"""
    
    @staticmethod
    def validate(payload: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """
        Valida payload contra schema.
        Lanza ValidationError si falla.
        """
        try:
            jsonschema.validate(payload, schema)
        except jsonschema.ValidationError as e:
            raise ValidationError({
                'field': e.path[-1] if e.path else '__all__',
                'message': e.message
            })
    
    @staticmethod
    def get_validation_errors(payload: Dict[str, Any], schema: Dict[str, Any]) -> List[Dict]:
        """
        Retorna lista de errores sin lanzar excepción.
        Útil para previsualización.
        """
        validator = jsonschema.Draft7Validator(schema)
        errors = []
        for error in validator.iter_errors(payload):
            errors.append({
                'field': '.'.join(str(p) for p in error.path),
                'message': error.message
            })
        return errors
```

### 3.4 Form Renderer (Generador de Formularios)

```python
# events/services/form_renderer.py
from django import forms

class DynamicFormRenderer:
    """Genera formularios Django desde JSON Schema"""
    
    @staticmethod
    def render_form(schema: Dict[str, Any]) -> forms.Form:
        """Genera clase de formulario dinámicamente"""
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        form_fields = {}
        
        for field_name, field_schema in properties.items():
            field_type = field_schema.get('type')
            field_title = field_schema.get('title', field_name)
            is_required = field_name in required
            
            # Crear campo según tipo
            if field_type == 'string':
                if 'enum' in field_schema:
                    choices = [(v, v) for v in field_schema['enum']]
                    form_fields[field_name] = forms.ChoiceField(
                        label=field_title,
                        choices=choices,
                        required=is_required
                    )
                else:
                    form_fields[field_name] = forms.CharField(
                        label=field_title,
                        required=is_required,
                        max_length=field_schema.get('maxLength', 255)
                    )
            
            elif field_type == 'number':
                form_fields[field_name] = forms.DecimalField(
                    label=field_title,
                    required=is_required,
                    min_value=field_schema.get('minimum'),
                    max_value=field_schema.get('maximum')
                )
            
            elif field_type == 'integer':
                form_fields[field_name] = forms.IntegerField(
                    label=field_title,
                    required=is_required,
                    min_value=field_schema.get('minimum'),
                    max_value=field_schema.get('maximum')
                )
            
            elif field_type == 'boolean':
                form_fields[field_name] = forms.BooleanField(
                    label=field_title,
                    required=is_required
                )
            
            # Agregar help_text si existe description
            if 'description' in field_schema:
                form_fields[field_name].help_text = field_schema['description']
            
            # Agregar widget attrs para unidades
            if 'unit' in field_schema:
                if 'widget' not in dir(form_fields[field_name]):
                    form_fields[field_name].widget = forms.TextInput()
                form_fields[field_name].widget.attrs['data-unit'] = field_schema['unit']
        
        # Crear clase de formulario dinámicamente
        DynamicForm = type('DynamicForm', (forms.Form,), form_fields)
        return DynamicForm
```

### 3.5 Event Service (Lógica de Negocio)

```python
# events/services/event_service.py
from django.db import transaction
from ..models import Event, EventType
from ..validators import SchemaValidator

class EventService:
    """Servicio para operaciones de eventos"""
    
    @staticmethod
    @transaction.atomic
    def create_event(event_type_id, field_id, campaign_id, timestamp, 
                     payload, observations, user):
        """
        Crea un nuevo evento con validación completa.
        """
        # 1. Obtener EventType
        event_type = EventType.objects.get(id=event_type_id, is_active=True)
        
        # 2. Validar payload contra schema
        SchemaValidator.validate(payload, event_type.schema)
        
        # 3. Crear evento
        event = Event.objects.create(
            event_type=event_type,
            field_id=field_id,
            campaign_id=campaign_id,
            timestamp=timestamp,
            payload=payload,
            observations=observations,
            created_by=user
        )
        
        # 4. Registrar en auditoría
        AuditLog.objects.create(
            user=user,
            action='CREATE_EVENT',
            entity='Event',
            entity_id=str(event.id),
            diff={'payload': payload}
        )
        
        return event
    
    @staticmethod
    def get_events_for_traceability(field_id, date_from=None, date_to=None, 
                                     event_type_id=None):
        """
        Consulta eventos para trazabilidad.
        """
        queryset = Event.objects.filter(field_id=field_id)
        
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        if event_type_id:
            queryset = queryset.filter(event_type_id=event_type_id)
        
        return queryset.select_related('event_type', 'field', 'campaign', 'created_by')
```

## 4. Esquemas Base Predefinidos

### 4.1 Riego

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Riego",
  "properties": {
    "metodo": {
      "type": "string",
      "enum": ["goteo", "microaspersion", "gravedad", "aspersion"],
      "title": "Método de Riego"
    },
    "duracion_min": {
      "type": "number",
      "minimum": 0,
      "maximum": 1440,
      "title": "Duración (min)"
    },
    "volumen_m3": {
      "type": "number",
      "minimum": 0,
      "title": "Volumen (m³)",
      "unit": "m³"
    },
    "presion_bar": {
      "type": "number",
      "minimum": 0,
      "maximum": 10,
      "title": "Presión (bar)",
      "unit": "bar"
    },
    "ce_uScm": {
      "type": "number",
      "minimum": 0,
      "title": "Conductividad Eléctrica (µS/cm)",
      "unit": "µS/cm"
    },
    "ph": {
      "type": "number",
      "minimum": 0,
      "maximum": 14,
      "title": "pH"
    }
  },
  "required": ["metodo", "duracion_min"]
}
```

### 4.2 Fertilización

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Fertilización",
  "properties": {
    "tipo": {
      "type": "string",
      "enum": ["foliar", "fertirriego", "edafica"],
      "title": "Tipo de Aplicación"
    },
    "producto": {
      "type": "string",
      "title": "Producto Aplicado"
    },
    "dosis_kg_ha": {
      "type": "number",
      "minimum": 0,
      "title": "Dosis (kg/ha)",
      "unit": "kg/ha"
    },
    "n_porcentaje": {
      "type": "number",
      "minimum": 0,
      "maximum": 100,
      "title": "Nitrógeno (%)",
      "unit": "%"
    },
    "p_porcentaje": {
      "type": "number",
      "minimum": 0,
      "maximum": 100,
      "title": "Fósforo (%)",
      "unit": "%"
    },
    "k_porcentaje": {
      "type": "number",
      "minimum": 0,
      "maximum": 100,
      "title": "Potasio (%)",
      "unit": "%"
    }
  },
  "required": ["tipo", "producto", "dosis_kg_ha"]
}
```

### 4.3 Cosecha

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Cosecha",
  "properties": {
    "fecha_inicio": {
      "type": "string",
      "format": "date",
      "title": "Fecha Inicio"
    },
    "fecha_fin": {
      "type": "string",
      "format": "date",
      "title": "Fecha Fin"
    },
    "rendimiento_kg": {
      "type": "number",
      "minimum": 0,
      "title": "Rendimiento Total (kg)",
      "unit": "kg"
    },
    "rendimiento_kg_ha": {
      "type": "number",
      "minimum": 0,
      "title": "Rendimiento por Hectárea (kg/ha)",
      "unit": "kg/ha"
    },
    "calidad": {
      "type": "string",
      "enum": ["exportacion", "primera", "segunda", "tercera"],
      "title": "Calidad"
    },
    "num_trabajadores": {
      "type": "integer",
      "minimum": 1,
      "title": "Número de Trabajadores"
    }
  },
  "required": ["fecha_inicio", "rendimiento_kg"]
}
```

## 5. Interfaz de Administración

### 5.1 Vista de Creación de EventType

Template Django para crear tipos de evento:

```html
<!-- events/templates/event_type_form.html -->
<form method="post" id="event-type-form">
  {% csrf_token %}
  
  <div class="form-group">
    <label>Nombre del Evento</label>
    <input type="text" name="name" class="form-control" required>
  </div>
  
  <div class="form-group">
    <label>Categoría</label>
    <select name="category" class="form-control">
      <option value="riego">Riego</option>
      <option value="fertilizacion">Fertilización</option>
      <option value="otro">Otro</option>
    </select>
  </div>
  
  <div class="form-group">
    <label>Descripción</label>
    <textarea name="description" class="form-control"></textarea>
  </div>
  
  <hr>
  <h4>Definir Campos</h4>
  
  <div id="fields-container">
    <!-- Campos dinámicos -->
  </div>
  
  <button type="button" class="btn btn-secondary" onclick="addField()">
    + Agregar Campo
  </button>
  
  <hr>
  <h4>Previsualización</h4>
  <div id="preview"></div>
  
  <button type="submit" class="btn btn-primary">Guardar Tipo de Evento</button>
</form>

<script>
function addField() {
  const container = document.getElementById('fields-container');
  const fieldHtml = `
    <div class="field-definition card mb-2 p-3">
      <div class="row">
        <div class="col-md-3">
          <label>Nombre del Campo</label>
          <input type="text" class="form-control field-name" required>
        </div>
        <div class="col-md-2">
          <label>Tipo</label>
          <select class="form-control field-type">
            <option value="string">Texto</option>
            <option value="number">Número</option>
            <option value="integer">Entero</option>
            <option value="boolean">Sí/No</option>
            <option value="date">Fecha</option>
          </select>
        </div>
        <div class="col-md-2">
          <label>Requerido</label>
          <input type="checkbox" class="field-required">
        </div>
        <div class="col-md-2">
          <label>Unidad</label>
          <input type="text" class="form-control field-unit" placeholder="kg, m³, etc.">
        </div>
        <div class="col-md-3">
          <label>&nbsp;</label><br>
          <button type="button" class="btn btn-danger btn-sm" onclick="this.closest('.field-definition').remove()">
            Eliminar
          </button>
        </div>
      </div>
    </div>
  `;
  container.insertAdjacentHTML('beforeend', fieldHtml);
}

// Generar schema JSON y enviarlo
document.getElementById('event-type-form').addEventListener('submit', function(e) {
  e.preventDefault();
  
  const schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {},
    "required": []
  };
  
  document.querySelectorAll('.field-definition').forEach(field => {
    const name = field.querySelector('.field-name').value;
    const type = field.querySelector('.field-type').value;
    const required = field.querySelector('.field-required').checked;
    const unit = field.querySelector('.field-unit').value;
    
    schema.properties[name] = {
      type: type,
      title: name
    };
    
    if (unit) {
      schema.properties[name].unit = unit;
    }
    
    if (required) {
      schema.required.push(name);
    }
  });
  
  // Agregar schema al formulario
  const schemaInput = document.createElement('input');
  schemaInput.type = 'hidden';
  schemaInput.name = 'schema';
  schemaInput.value = JSON.stringify(schema);
  this.appendChild(schemaInput);
  
  this.submit();
});
</script>
```

## 6. Versionado de Esquemas

Cuando un administrador modifica un `EventType` activo:

1. Se crea un **nuevo registro** con `version` incrementado
2. Los eventos antiguos mantienen referencia a la versión anterior
3. Nuevos eventos usan la nueva versión
4. La aplicación puede leer ambas versiones

```python
def update_event_type_schema(event_type_id, new_schema):
    """Crea nueva versión del EventType"""
    old_type = EventType.objects.get(id=event_type_id)
    
    # Desactivar versión antigua
    old_type.is_active = False
    old_type.save()
    
    # Crear nueva versión
    new_type = EventType.objects.create(
        name=old_type.name,
        category=old_type.category,
        description=old_type.description,
        schema=new_schema,
        version=old_type.version + 1,
        is_active=True,
        icon=old_type.icon,
        color=old_type.color
    )
    
    return new_type
```

---

**Siguiente**: [Plan de Desarrollo →](./08_cronograma.md)

[← Volver al índice](../README.md)
