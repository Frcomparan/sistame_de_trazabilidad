# Módulo de Eventos

## Descripción

El módulo de eventos permite registrar actividades de trazabilidad agrícola. El sistema incluye 10 tipos de eventos predefinidos, cada uno con campos específicos definidos mediante modelos Django.

## Características

- **Modelos Específicos**: Cada tipo de evento tiene su propio modelo con campos tipados
- **Validación Robusta**: Validaciones Django nativas (MinValueValidator, MaxValueValidator, etc.)
- **Campos Opcionales**: Campos opcionales funcionan correctamente sin requerir valores
- **Autocálculo**: Campos calculados automáticamente (ej: costo_total en mano de obra)
- **Tipos Predefinidos**: 10 tipos de eventos fijos que cubren las principales actividades

## Tipos de Eventos Incluidos

1. **Aplicación de Riego** (`irrigation`)
   - Método, duración, fuente de agua, volumen, presión, CE, pH

2. **Aplicación de Fertilizante** (`fertilization`)
   - Producto, método de aplicación, dosis, NPK, volumen de caldo

3. **Aplicación Fitosanitaria** (`phytosanitary`)
   - Producto, tipo, objetivo, método, dosis, intervalo de seguridad, eficacia

4. **Labores de Cultivo** (`maintenance`)
   - Actividad, horas-hombre, herramientas, número de jornales

5. **Monitoreo de Plagas** (`monitoring`)
   - Plaga/enfermedad, método de muestreo, incidencia, severidad

6. **Brote de Plaga/Enfermedad** (`outbreak`)
   - Tipo de problema, severidad, área afectada, acción inmediata

7. **Condiciones Climáticas** (`climate`)
   - Temperaturas, humedad, precipitación, viento, radiación solar

8. **Cosecha** (`harvest`)
   - Variedad, volumen, rendimiento, calidad, trabajadores

9. **Almacenamiento Poscosecha** (`postharvest`)
   - Producto, cantidad, temperatura, humedad, condiciones

10. **Mano de Obra y Costos** (`labor_cost`)
    - Actividad, trabajadores, horas, costo (con autocálculo)

## Uso

### Cargar Tipos de Eventos

```bash
python manage.py setup_event_types
```

Este comando crea los 10 tipos de eventos predefinidos en la base de datos.

### Crear un Evento (Web)

1. Navegar a `/events/create/`
2. Seleccionar el tipo de evento de la lista
3. El formulario mostrará los campos específicos del tipo seleccionado
4. Completar la información (los campos opcionales pueden dejarse vacíos)
5. Enviar el formulario

### Crear un Evento (API)

```bash
POST /api/v1/events/create/
Content-Type: application/json

{
  "event_type": 1,
  "field": "abc-123-...",
  "campaign": 3,
  "timestamp": "2024-01-15T14:30:00-06:00",
  "metodo": "Goteo",
  "duracion_minutos": 120,
  "fuente_agua": "Pozo",
  "volumen_m3": 45.5,
  "observations": "Riego normal, sin incidencias"
}
```

**Nota**: Los campos específicos dependen del tipo de evento seleccionado.

## Modelos

### EventType

Define los tipos de eventos disponibles en el sistema (10 tipos predefinidos).

**Campos principales:**
- `name`: Nombre del tipo de evento
- `description`: Descripción detallada
- `category`: Categoría (irrigation, fertilization, etc.)
- `icon`: Icono de Bootstrap Icons
- `color`: Color hexadecimal
- `is_active`: Si el tipo está disponible

### Event (Modelo Base)

Modelo base con campos comunes a todos los eventos.

**Campos principales:**
- `id`: UUID único
- `event_type`: Tipo de evento (FK a EventType)
- `field`: Campo donde ocurrió (FK a Field)
- `campaign`: Campaña asociada (FK a Campaign, opcional)
- `timestamp`: Fecha y hora del evento
- `observations`: Notas adicionales (texto)
- `created_by`: Usuario que registró el evento
- `created_at` / `updated_at`: Timestamps de auditoría

### Modelos Específicos

Cada tipo de evento tiene su propio modelo que hereda de `Event`:

- `IrrigationEvent`: Campos específicos de riego
- `FertilizationEvent`: Campos específicos de fertilización
- `PhytosanitaryEvent`: Campos específicos de fitosanitarios
- `MaintenanceEvent`: Campos específicos de labores
- `MonitoringEvent`: Campos específicos de monitoreo
- `OutbreakEvent`: Campos específicos de brotes
- `ClimateEvent`: Campos específicos de clima
- `HarvestEvent`: Campos específicos de cosecha
- `PostHarvestEvent`: Campos específicos de poscosecha
- `LaborCostEvent`: Campos específicos de mano de obra (con autocálculo)

### Attachment

Permite adjuntar archivos a los eventos (fotos, documentos).

**Campos principales:**
- `event`: Evento asociado (FK a Event)
- `file`: Archivo adjunto
- `file_name`: Nombre original del archivo
- `file_size`: Tamaño en bytes
- `mime_type`: Tipo MIME del archivo

## Endpoints API

### GET /api/v1/events/

Lista todos los eventos con paginación y filtros.

**Query Parameters:**
- `event_type`: Filtrar por tipo de evento (ID)
- `field`: Filtrar por campo (UUID)
- `campaign`: Filtrar por campaña (ID)
- `date_from`: Fecha inicio (ISO 8601)
- `date_to`: Fecha fin (ISO 8601)

### POST /api/v1/events/create/

Crea un nuevo evento. Los campos requeridos dependen del tipo de evento.

**Ejemplo para Riego:**
```json
{
  "event_type": 1,
  "field": "abc-123-...",
  "timestamp": "2024-01-15T14:30:00-06:00",
  "metodo": "Goteo",
  "duracion_minutos": 120,
  "fuente_agua": "Pozo"
}
```

### GET /api/v1/event-types/

Lista los tipos de eventos disponibles.

**Query Parameters:**
- `category`: Filtrar por categoría
- `is_active`: Filtrar por estado activo

### GET /api/v1/events/{id}/

Obtiene los detalles de un evento específico. Retorna los campos específicos según el tipo de evento.

## Rutas Web

| URL | Vista | Descripción |
|-----|-------|-------------|
| `/events/` | event_list | Lista de eventos con filtros |
| `/events/create/` | event_create | Formulario de creación (con selector de tipo) |
| `/events/<uuid>/` | event_detail | Detalle de un evento |
| `/events/api/event-type/<id>/info/` | get_event_type_info | API AJAX para obtener info del tipo |

## Formularios

Cada tipo de evento tiene su propio formulario Django:

- `IrrigationEventForm`
- `FertilizationEventForm`
- `PhytosanitaryEventForm`
- `MaintenanceEventForm`
- `MonitoringEventForm`
- `OutbreakEventForm`
- `ClimateEventForm`
- `HarvestEventForm`
- `PostHarvestEventForm`
- `LaborCostEventForm`

Los formularios incluyen:
- Validaciones de tipo de datos
- Validaciones de rangos (min/max)
- Campos opcionales correctamente configurados
- Autocálculo en `LaborCostEventForm` (costo_total)

## Validación

La validación se realiza en múltiples niveles:

1. **Formulario Django**: Validación de tipos y campos requeridos
2. **Modelo Django**: Validaciones con validators (MinValueValidator, etc.)
3. **Método clean()**: Validaciones personalizadas (ej: temperatura_max >= temperatura_min)

## Características Especiales

### Autocálculo de Costos

En `LaborCostEvent`, el campo `costo_total` se calcula automáticamente si se proporcionan:
- `horas_trabajo`
- `costo_hora`
- `numero_trabajadores`

Fórmula: `costo_total = horas_trabajo * costo_hora * numero_trabajadores`

### Campos Opcionales

Todos los campos marcados como opcionales (`null=True, blank=True`) pueden dejarse vacíos sin causar errores de validación.

## Seguridad

- Autenticación requerida para todas las operaciones
- Solo usuarios autenticados pueden crear eventos
- Los eventos registran automáticamente el usuario creador
- Validación estricta de tipos de datos

## Reportes y Análisis

Los eventos pueden ser consultados y filtrados para generar reportes:
- Por tipo de evento
- Por campo
- Por campaña
- Por rango de fechas
- Por usuario

## Extensión

Para agregar un nuevo tipo de evento en el futuro:

1. Crear el modelo específico heredando de `Event`
2. Crear el formulario correspondiente
3. Crear el serializer correspondiente
4. Agregar al mapeo en `event_models.py`
5. Actualizar el comando `setup_event_types.py`
6. Crear migración

## Futuras Mejoras

- [ ] Edición de eventos existentes
- [ ] Eliminación con soft-delete
- [ ] Adjuntar fotos y documentos
- [ ] Exportar eventos a Excel/CSV
- [ ] Gráficos y estadísticas
- [ ] Notificaciones automáticas
- [ ] Integración con dispositivos IoT
