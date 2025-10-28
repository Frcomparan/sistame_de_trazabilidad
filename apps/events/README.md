# Módulo de Eventos Dinámicos

## Descripción

El módulo de eventos permite registrar actividades de trazabilidad agrícola de forma dinámica. Cada tipo de evento define su propio esquema JSON que determina qué campos adicionales se requieren al crear un evento.

## Características

- **Registro Dinámico**: Los formularios se generan automáticamente basados en JSON Schema
- **Validación en Tiempo Real**: Los datos se validan contra el esquema tanto en cliente como servidor
- **Tipos de Eventos Predefinidos**: Incluye tipos comunes de eventos agrícolas
- **Extensible**: Fácil agregar nuevos tipos de eventos mediante el admin

## Tipos de Eventos Incluidos

1. **Riego por Goteo** (`irrigation`)
   - Duración, caudal, presión, fuente de agua

2. **Fertilización Foliar** (`fertilization`)
   - Producto, dosis, concentración, método de aplicación

3. **Aplicación Fitosanitaria** (`phytosanitary`)
   - Producto, tipo, principio activo, plaga objetivo, plazo de seguridad

4. **Cosecha** (`harvest`)
   - Cantidad, calidad, calibre, destino, equipo

5. **Poda** (`pruning`)
   - Tipo de poda, número de árboles, intensidad, herramientas

6. **Monitoreo de Plagas** (`monitoring`)
   - Plaga monitoreada, nivel de incidencia, método, árboles afectados

7. **Análisis de Suelo** (`analysis`)
   - Tipo de análisis, muestras, profundidad, resultados

## Uso

### Cargar Tipos de Eventos de Ejemplo

```bash
python manage.py loaddata apps/events/fixtures/event_types.json
```

### Crear un Evento (Web)

1. Navegar a `/events/create/`
2. Seleccionar el tipo de evento
3. El formulario se adaptará automáticamente con los campos requeridos
4. Completar la información y enviar

### Crear un Evento (API)

```bash
POST /api/v1/events/create/
Content-Type: application/json

{
  "event_type": 1,
  "field": 1,
  "campaign": 1,
  "timestamp": "2024-01-15T14:30:00Z",
  "payload": {
    "duracion_horas": 2.5,
    "caudal_l_h": 150,
    "presion_bar": 1.5,
    "fuente_agua": "Pozo"
  },
  "observations": "Riego normal, sin incidencias"
}
```

### Estructura del JSON Schema

Los esquemas de tipos de eventos siguen el estándar JSON Schema Draft 7:

```json
{
  "type": "object",
  "title": "Título del esquema",
  "required": ["campo_obligatorio1", "campo_obligatorio2"],
  "properties": {
    "campo_texto": {
      "type": "string",
      "title": "Etiqueta del campo",
      "description": "Descripción del campo",
      "maxLength": 200,
      "example": "Valor de ejemplo"
    },
    "campo_numero": {
      "type": "number",
      "title": "Campo Numérico",
      "minimum": 0,
      "maximum": 100,
      "example": 50
    },
    "campo_entero": {
      "type": "integer",
      "title": "Campo Entero",
      "example": 10
    },
    "campo_booleano": {
      "type": "boolean",
      "title": "Campo Sí/No",
      "example": true
    },
    "campo_seleccion": {
      "type": "string",
      "title": "Selección",
      "enum": ["Opción 1", "Opción 2", "Opción 3"],
      "example": "Opción 1"
    }
  }
}
```

### Tipos de Campos Soportados

| Tipo JSON Schema | HTML Input | Descripción |
|-----------------|------------|-------------|
| `string` | `<input type="text">` | Texto libre |
| `string` + `enum` | `<select>` | Lista de opciones |
| `number` | `<input type="number">` | Número decimal |
| `integer` | `<input type="number">` | Número entero |
| `boolean` | `<input type="checkbox">` | Verdadero/Falso |
| `array` | `<textarea>` | Array JSON |
| `object` | `<textarea>` | Objeto JSON |

### Validaciones Soportadas

- `required`: Campos obligatorios
- `minimum` / `maximum`: Rangos numéricos
- `minLength` / `maxLength`: Longitud de texto
- `enum`: Lista de valores permitidos
- `pattern`: Expresiones regulares (regex)

## Modelos

### EventType

Define los tipos de eventos disponibles en el sistema.

**Campos principales:**
- `name`: Nombre del tipo de evento
- `description`: Descripción detallada
- `category`: Categoría (irrigation, fertilization, etc.)
- `icon`: Icono de Bootstrap Icons
- `color`: Color hexadecimal
- `schema`: JSON Schema que define los campos dinámicos
- `is_active`: Si el tipo está disponible

### Event

Representa una instancia de evento registrado.

**Campos principales:**
- `id`: UUID único
- `event_type`: Tipo de evento (FK a EventType)
- `field`: Campo donde ocurrió (FK a Field)
- `campaign`: Campaña asociada (FK a Campaign, opcional)
- `timestamp`: Fecha y hora del evento
- `payload`: Datos dinámicos en formato JSON (JSONB)
- `observations`: Notas adicionales (texto)
- `created_by`: Usuario que registró el evento
- `created_at` / `updated_at`: Timestamps de auditoría

### Attachment

Permite adjuntar archivos a los eventos (fotos, documentos).

**Campos principales:**
- `event`: Evento asociado (FK a Event)
- `file`: Archivo adjunto
- `description`: Descripción del archivo
- `file_type`: Tipo de archivo

## Endpoints API

### GET /api/v1/events/

Lista todos los eventos con paginación y filtros.

**Query Parameters:**
- `event_type`: Filtrar por tipo de evento (ID)
- `field`: Filtrar por campo (ID)
- `campaign`: Filtrar por campaña (ID)
- `date_from`: Fecha inicio (ISO 8601)
- `date_to`: Fecha fin (ISO 8601)

### POST /api/v1/events/create/

Crea un nuevo evento con validación de schema.

### GET /api/v1/events/types/

Lista los tipos de eventos disponibles.

**Query Parameters:**
- `category`: Filtrar por categoría
- `is_active`: Filtrar por estado activo

### GET /api/v1/events/{id}/

Obtiene los detalles de un evento específico.

## Rutas Web

| URL | Vista | Descripción |
|-----|-------|-------------|
| `/events/` | event_list | Lista de eventos con filtros |
| `/events/create/` | event_create | Formulario de creación |
| `/events/<uuid>/` | event_detail | Detalle de un evento |
| `/events/api/event-type/<id>/schema/` | get_event_type_schema | API AJAX para obtener schema |

## Personalización

### Agregar un Nuevo Tipo de Evento

1. Ir al admin de Django: `/admin/events/eventtype/`
2. Crear un nuevo EventType
3. Definir el JSON Schema en el campo `schema`
4. Asignar icono y color
5. Guardar

### Ejemplo de Schema Personalizado

```json
{
  "type": "object",
  "title": "Control de Temperatura",
  "required": ["temperatura", "humedad"],
  "properties": {
    "temperatura": {
      "type": "number",
      "title": "Temperatura (°C)",
      "minimum": -10,
      "maximum": 50,
      "example": 25
    },
    "humedad": {
      "type": "number",
      "title": "Humedad Relativa (%)",
      "minimum": 0,
      "maximum": 100,
      "example": 65
    },
    "presion_atmosferica": {
      "type": "number",
      "title": "Presión (hPa)",
      "example": 1013
    }
  }
}
```

## Validación

La validación se realiza en dos niveles:

1. **Cliente (JavaScript)**: Validación básica antes de enviar el formulario
2. **Servidor (Python)**: Validación completa usando `jsonschema` library

Si la validación falla, se muestra un mensaje de error detallado.

## Seguridad

- Autenticación requerida para todas las operaciones
- Solo usuarios autenticados pueden crear eventos
- Los eventos registran automáticamente el usuario creador
- Validación estricta de esquemas para prevenir inyección de datos

## Reportes y Análisis

Los eventos pueden ser consultados y filtrados para generar reportes:
- Por tipo de evento
- Por campo
- Por campaña
- Por rango de fechas
- Por usuario

## Futuras Mejoras

- [ ] Edición de eventos existentes
- [ ] Eliminación con soft-delete
- [ ] Adjuntar fotos y documentos
- [ ] Exportar eventos a Excel/CSV
- [ ] Gráficos y estadísticas
- [ ] Notificaciones automáticas
- [ ] Integración con dispositivos IoT
