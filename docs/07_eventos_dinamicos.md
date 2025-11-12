# Sistema de Eventos

[← Volver al índice](../README.md) | [← API REST](./06_api_rest.md) | [Cronograma →](./08_cronograma.md)

## 1. Introducción

El **Sistema de Eventos** es el núcleo del sistema de trazabilidad. El sistema incluye 10 tipos de eventos predefinidos que cubren las principales actividades agrícolas. Estos eventos están configurados con esquemas JSON que definen los campos requeridos y sus validaciones.

> **Nota MVP**: Para simplificar el sistema y reducir la complejidad, los tipos de eventos son **fijos y predefinidos**. No se permite la creación dinámica de nuevos tipos de eventos por parte de los administradores. Si se requiere un nuevo tipo de evento, debe ser agregado mediante código y migración.

## 2. Concepto y Arquitectura

### 2.1 Separación de Definición e Instancia

```
┌──────────────────────────────────────────────┐
│          EventType (Definición)              │
│  - Define QUÉ campos tiene el evento         │
│  - Schema de validación (JSON Schema)        │
│  - Metadata (nombre, categoría, icono)       │
│  - PREDEFINIDO (10 tipos fijos)              │
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
│ Sistema     │
│ inicializa  │──┐
│ 10 eventos  │  │ Eventos predefinidos
└─────────────┘  │ cargados al inicio
                 ↓
┌──────────────────────────────────┐
│ Sistema muestra formulario        │
│ según tipo de evento seleccionado │
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

## 3. Tipos de Eventos Predefinidos

El sistema incluye los siguientes 10 tipos de eventos:

1. **Aplicación de Riego** - Registro de aplicaciones de riego con diferentes métodos
2. **Aplicación de Fertilizante** - Fertilización al suelo o foliar
3. **Aplicación Fitosanitaria** - Aplicación de fungicidas, insecticidas, herbicidas
4. **Labores de Cultivo** - Actividades de mantenimiento (poda, deshierbe, etc.)
5. **Monitoreo de Plagas** - Inspección y monitoreo preventivo
6. **Brote de Plaga/Enfermedad** - Registro de brotes severos
7. **Condiciones Climáticas** - Registro de variables meteorológicas
8. **Cosecha** - Actividades de recolección y clasificación
9. **Almacenamiento Poscosecha** - Control de almacenamiento del producto
10. **Mano de Obra y Costos** - Registro de recursos humanos y costos

Estos eventos se crean automáticamente al ejecutar el comando `setup_event_types` (ver [documentación del comando](./comando_setup_event_types.md)).

## 4. Componentes Principales

### 4.1 EventType (Modelo)

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
        return self.name
```

> **Nota**: Se eliminó el campo `version` ya que los eventos son fijos y no requieren versionado dinámico.

### 4.2 Event (Modelo)

```python
# events/models.py
class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    event_type = models.ForeignKey(EventType, on_delete=models.PROTECT)
    field = models.ForeignKey('catalogs.Field', on_delete=models.CASCADE)
    campaign = models.ForeignKey('catalogs.Campaign', on_delete=models.SET_NULL, null=True)
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
        return f"{self.event_type.name} - {self.field.name}"
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['field', '-timestamp']),
            models.Index(fields=['event_type']),
            GinIndex(fields=['payload']),
        ]
```

### 4.3 Schema Validator (Servicio)

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

### 4.4 Event Service (Lógica de Negocio)

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

## 5. Esquemas de Eventos Predefinidos

Cada uno de los 10 eventos tiene un esquema JSON Schema que define sus campos. A continuación se muestran ejemplos de algunos esquemas:

### 5.1 Aplicación de Riego

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Datos de Aplicación de Riego",
  "properties": {
    "metodo": {
      "type": "string",
      "enum": ["Aspersión", "Goteo", "Surco", "Pivote", "Manual"],
      "title": "Método de Riego"
    },
    "duracion_minutos": {
      "type": "integer",
      "minimum": 1,
      "title": "Duración (minutos)"
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
  "required": ["metodo", "duracion_minutos"]
}
```

### 5.2 Aplicación de Fertilizante

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Datos de Aplicación de Fertilizante",
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

### 5.3 Cosecha

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Datos de Cosecha",
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

Para ver todos los esquemas completos, consulta el código fuente del comando `setup_event_types` o ejecuta el comando y revisa los tipos creados en la base de datos.

## 6. Inicialización del Sistema

### 6.1 Carga de Eventos Predefinidos

Los 10 tipos de eventos se cargan al sistema mediante el comando de Django:

```bash
python manage.py setup_event_types
```

Este comando:
- Crea los 10 tipos de eventos si no existen
- Define sus esquemas JSON Schema
- Configura iconos, colores y categorías
- Establece los campos requeridos y validaciones

Para más detalles, consulta la [documentación del comando](./comando_setup_event_types.md).

### 6.2 Modificación de Eventos Existentes

Aunque los eventos son predefinidos, los administradores pueden:

- **Modificar esquemas**: Ajustar campos, validaciones o requerimientos mediante el admin de Django
- **Desactivar eventos**: Marcar como inactivos si no se utilizan
- **Cambiar metadata**: Modificar iconos, colores o descripciones

> **Importante**: Las modificaciones a esquemas deben hacerse con cuidado, ya que pueden afectar eventos ya registrados. Se recomienda hacer cambios solo durante el desarrollo o con migración de datos.

## 7. Interfaz de Usuario

### 7.1 Formulario de Creación de Evento

El formulario de creación de eventos se genera dinámicamente basándose en el esquema del tipo de evento seleccionado:

1. El usuario selecciona un tipo de evento de la lista de 10 predefinidos
2. El sistema carga el esquema JSON del tipo seleccionado
3. Se renderizan los campos del formulario según el esquema
4. Se aplican validaciones en tiempo real
5. Al guardar, se valida el payload completo contra el schema

### 7.2 Validación en Formularios

La validación se realiza en dos niveles:

1. **Frontend**: Validación básica de tipos y campos requeridos
2. **Backend**: Validación completa contra JSON Schema antes de guardar

Esto garantiza la integridad de los datos y previene errores de captura.

## 8. Ventajas del Enfoque de Eventos Fijos

### 8.1 Simplicidad

- **Menor complejidad**: No requiere interfaz de creación de tipos de eventos
- **Validación más simple**: Los esquemas son conocidos y probados
- **Menos errores**: No hay riesgo de crear esquemas inválidos

### 8.2 Mantenibilidad

- **Código más claro**: Los tipos de eventos están definidos en código
- **Mejor testing**: Es más fácil probar tipos conocidos
- **Versionado controlado**: Los cambios pasan por revisión de código

### 8.3 Rendimiento

- **Menos consultas**: No necesita cargar definiciones dinámicas
- **Caché más efectivo**: Los esquemas son estáticos
- **Validación más rápida**: No requiere procesamiento dinámico

## 9. Extensión Futura

Si en el futuro se requiere agregar nuevos tipos de eventos:

1. **Modificar el comando**: Agregar el nuevo tipo en `setup_event_types.py`
2. **Crear migración**: Si es necesario modificar el modelo
3. **Actualizar documentación**: Documentar el nuevo tipo de evento
4. **Ejecutar comando**: Cargar el nuevo tipo en la base de datos

Este proceso garantiza que los nuevos tipos sigan el mismo estándar de calidad y validación que los predefinidos.

---

**Siguiente**: [Plan de Desarrollo →](./08_cronograma.md)

[← Volver al índice](../README.md)
