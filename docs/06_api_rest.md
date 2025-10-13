# Especificación de API REST

[← Volver al índice](../README.md) | [← Base de Datos](./05_base_datos.md) | [Eventos Dinámicos →](./07_eventos_dinamicos.md)

## 1. Introducción

API REST para acceso programático al sistema de trazabilidad. Construida con Django REST Framework, sigue principios RESTful y está documentada con OpenAPI 3.0.

## 2. Características Generales

### 2.1 Base URL

```
Desarrollo:  http://localhost:8000/api/v1/
Producción:  https://traceability.example.com/api/v1/
```

### 2.2 Formato de Datos

- **Request**: JSON (`Content-Type: application/json`)
- **Response**: JSON
- **Encoding**: UTF-8
- **Fechas**: ISO 8601 (`2025-10-13T08:30:00-06:00`)

### 2.3 Autenticación

**JWT (JSON Web Tokens)**

```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "username": "usuario",
  "password": "contraseña"
}
```

**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 5,
    "username": "usuario",
    "email": "usuario@example.com",
    "role": "FIELD_TECH",
    "full_name": "Juan Pérez"
  }
}
```

**Uso del Token**:
```http
GET /api/v1/events/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Refresh Token**:
```http
POST /api/v1/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2.4 Paginación

Todas las listas están paginadas:

```http
GET /api/v1/events/?page=2&page_size=50
```

**Response**:
```json
{
  "count": 235,
  "next": "http://localhost:8000/api/v1/events/?page=3",
  "previous": "http://localhost:8000/api/v1/events/?page=1",
  "results": [...]
}
```

### 2.5 Filtros

Filtros query string estándar:

```http
GET /api/v1/events/?field_id=abc-123&event_type_id=5&from=2025-01-01&to=2025-12-31
```

### 2.6 Ordenamiento

```http
GET /api/v1/events/?ordering=-timestamp
GET /api/v1/events/?ordering=field__name,timestamp
```

### 2.7 Rate Limiting

- **Usuarios autenticados**: 100 req/min
- **API keys**: 1000 req/min
- **Anónimos**: 10 req/min

### 2.8 Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado |
| 204 | No Content - Eliminación exitosa |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - No autenticado |
| 403 | Forbidden - Sin permisos |
| 404 | Not Found - Recurso no existe |
| 422 | Unprocessable Entity - Validación fallida |
| 429 | Too Many Requests - Rate limit excedido |
| 500 | Internal Server Error |

## 3. Endpoints

### 3.1 Autenticación

#### POST /auth/login/
Autenticar usuario y obtener tokens JWT.

#### POST /auth/refresh/
Refrescar access token.

#### POST /auth/logout/
Invalidar refresh token.

### 3.2 Lotes (Fields)

#### GET /fields/
Listar todos los lotes.

**Query Params**:
- `search`: Búsqueda por nombre o código
- `is_active`: Filtrar por estado
- `ordering`: Ordenar (-name, surface_ha, etc.)

**Response**:
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "abc-123-...",
      "name": "Parcela 5A",
      "code": "P5A",
      "surface_ha": "12.5000",
      "location": "Sector Norte",
      "latitude": "20.123456",
      "longitude": "-103.456789",
      "is_active": true,
      "created_at": "2025-01-15T10:00:00-06:00"
    }
  ]
}
```

#### POST /fields/
Crear nuevo lote.

**Request**:
```json
{
  "name": "Parcela 7B",
  "code": "P7B",
  "surface_ha": 8.3,
  "location": "Sector Sur",
  "latitude": 20.123456,
  "longitude": -103.456789
}
```

#### GET /fields/{id}/
Detalle de un lote.

#### PUT /fields/{id}/
Actualizar lote completo.

#### PATCH /fields/{id}/
Actualizar parcialmente.

#### DELETE /fields/{id}/
Eliminar (soft delete si tiene eventos).

### 3.3 Campañas (Campaigns)

#### GET /campaigns/
Listar campañas.

**Query Params**:
- `is_active`: true/false
- `season`: Filtrar por temporada
- `ordering`: -start_date, name, etc.

**Response**:
```json
{
  "count": 5,
  "results": [
    {
      "id": 3,
      "name": "2025 - Temporada Alta",
      "season": "Verano",
      "variety": "Limón Persa",
      "start_date": "2025-05-01",
      "end_date": "2025-10-31",
      "is_active": true,
      "event_count": 45
    }
  ]
}
```

#### POST /campaigns/
Crear campaña.

#### GET /campaigns/{id}/
Detalle.

#### PUT/PATCH /campaigns/{id}/
Actualizar.

#### DELETE /campaigns/{id}/
Eliminar.

### 3.4 Estaciones (Stations)

#### GET /stations/
Listar estaciones.

**Query Params**:
- `field_id`: Filtrar por lote
- `is_operational`: true/false
- `station_type`: clima/suelo/multivariable

#### POST /stations/
Crear estación.

**Request**:
```json
{
  "name": "Estación Norte 1",
  "field_id": "abc-123-...",
  "station_type": "multivariable",
  "latitude": 20.123456,
  "longitude": -103.456789,
  "installed_at": "2025-01-10"
}
```

#### GET /stations/{id}/
Detalle.

#### GET /stations/{id}/latest-readings/
Últimas lecturas de variables (24h).

**Response**:
```json
{
  "station": {
    "id": 1,
    "name": "Estación Norte 1"
  },
  "readings": [
    {
      "variable_type": "soil_moisture",
      "value": "32.5",
      "unit": "%",
      "timestamp": "2025-10-13T09:15:00-06:00"
    },
    {
      "variable_type": "air_temp",
      "value": "28.3",
      "unit": "°C",
      "timestamp": "2025-10-13T09:15:00-06:00"
    }
  ]
}
```

### 3.5 Tipos de Evento (Event Types)

#### GET /event-types/
Listar tipos de evento disponibles.

**Query Params**:
- `category`: Filtrar por categoría
- `is_active`: Solo activos

**Response**:
```json
{
  "count": 12,
  "results": [
    {
      "id": 1,
      "name": "Riego",
      "category": "riego",
      "description": "Evento de aplicación de riego",
      "version": 1,
      "is_active": true,
      "icon": "fas fa-tint",
      "color": "#007bff",
      "schema": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {...},
        "required": ["metodo", "duracion_min"]
      }
    }
  ]
}
```

#### POST /event-types/
Crear nuevo tipo de evento (solo ADMIN).

**Request**:
```json
{
  "name": "Análisis de Suelo",
  "category": "otro",
  "description": "Análisis químico del suelo",
  "icon": "fas fa-flask",
  "color": "#6c757d",
  "schema": {
    "type": "object",
    "properties": {
      "laboratorio": {
        "type": "string",
        "title": "Laboratorio"
      },
      "ph": {
        "type": "number",
        "minimum": 4,
        "maximum": 9,
        "title": "pH"
      },
      "materia_organica": {
        "type": "number",
        "minimum": 0,
        "maximum": 100,
        "title": "Materia Orgánica (%)",
        "unit": "%"
      },
      "nitrogeno_ppm": {
        "type": "number",
        "minimum": 0,
        "title": "Nitrógeno (ppm)",
        "unit": "ppm"
      }
    },
    "required": ["laboratorio", "ph"]
  }
}
```

#### GET /event-types/{id}/
Detalle del tipo.

#### PUT/PATCH /event-types/{id}/
Actualizar (crea nueva versión si es_active=true).

#### DELETE /event-types/{id}/
Desactivar (no eliminar físicamente).

### 3.6 Eventos (Events)

#### GET /events/
Listar eventos con filtros avanzados.

**Query Params**:
- `field_id`: UUID del lote
- `campaign_id`: ID de campaña
- `event_type_id`: ID del tipo de evento
- `from`: Fecha inicio (ISO 8601)
- `to`: Fecha fin (ISO 8601)
- `created_by_id`: ID del usuario
- `search`: Búsqueda en observations
- `ordering`: -timestamp, field__name, etc.

**Response**:
```json
{
  "count": 120,
  "next": "...",
  "previous": null,
  "results": [
    {
      "id": "def-456-...",
      "event_type": {
        "id": 1,
        "name": "Riego",
        "category": "riego",
        "color": "#007bff"
      },
      "field": {
        "id": "abc-123-...",
        "name": "Parcela 5A",
        "code": "P5A"
      },
      "campaign": {
        "id": 3,
        "name": "2025 - Temporada Alta"
      },
      "timestamp": "2025-10-13T08:30:00-06:00",
      "payload": {
        "metodo": "goteo",
        "duracion_min": 90,
        "volumen_m3": 45.5,
        "presion_bar": 1.8,
        "ce_uScm": 850,
        "ph": 6.7
      },
      "observations": "Riego matutino, presión estable",
      "created_by": {
        "id": 5,
        "username": "jperez",
        "full_name": "Juan Pérez"
      },
      "created_at": "2025-10-13T09:00:00-06:00",
      "attachment_count": 2
    }
  ]
}
```

#### POST /events/
Registrar nuevo evento.

**Request**:
```json
{
  "event_type_id": 1,
  "field_id": "abc-123-...",
  "campaign_id": 3,
  "timestamp": "2025-10-13T08:30:00-06:00",
  "payload": {
    "metodo": "goteo",
    "duracion_min": 90,
    "volumen_m3": 45.5,
    "presion_bar": 1.8,
    "ce_uScm": 850,
    "ph": 6.7
  },
  "observations": "Riego matutino, presión estable"
}
```

**Validaciones**:
- `payload` debe pasar validación contra `event_type.schema`
- `timestamp` no puede ser futuro (> now + 1h)
- `field_id` y `campaign_id` deben existir

**Response 201**:
```json
{
  "id": "def-456-...",
  "event_type": {...},
  "field": {...},
  "campaign": {...},
  "timestamp": "2025-10-13T08:30:00-06:00",
  "payload": {...},
  "observations": "Riego matutino, presión estable",
  "created_by": {...},
  "created_at": "2025-10-13T09:00:15-06:00"
}
```

**Error 422** (validación fallida):
```json
{
  "error": "Validation failed",
  "details": {
    "payload": {
      "duracion_min": ["Este campo es requerido."],
      "ph": ["Debe estar entre 0 y 14."]
    }
  }
}
```

#### GET /events/{id}/
Detalle del evento.

#### PUT/PATCH /events/{id}/
Actualizar evento (solo si creado < 24h y por mismo usuario o admin).

#### DELETE /events/{id}/
Eliminar (solo admin, se registra en auditoría).

### 3.7 Adjuntos (Attachments)

#### POST /events/{event_id}/attachments/
Subir archivo adjunto.

**Request** (multipart/form-data):
```
Content-Type: multipart/form-data

file: (binary)
```

**Response 201**:
```json
{
  "id": 15,
  "event_id": "def-456-...",
  "file_name": "medidor_riego.jpg",
  "file_size": 2456789,
  "mime_type": "image/jpeg",
  "url": "https://traceability.example.com/media/events/def-456.../medidor_riego_abc123.jpg",
  "uploaded_by": {
    "id": 5,
    "username": "jperez"
  },
  "uploaded_at": "2025-10-13T09:05:00-06:00"
}
```

#### GET /events/{event_id}/attachments/
Listar adjuntos del evento.

#### DELETE /attachments/{id}/
Eliminar adjunto (solo admin o creador).

### 3.8 Variables

#### GET /variables/
Listar variables con filtros.

**Query Params**:
- `station_id`: ID de estación
- `field_id`: ID de lote
- `variable_type`: Tipo (soil_moisture, air_temp, etc.)
- `from`: Fecha inicio
- `to`: Fecha fin
- `source`: manual/automatic
- `ordering`: -timestamp, variable_type, etc.

**Response**:
```json
{
  "count": 1250,
  "results": [
    {
      "id": 12345,
      "station": {
        "id": 1,
        "name": "Estación Norte 1"
      },
      "field": {
        "id": "abc-123-...",
        "name": "Parcela 5A"
      },
      "timestamp": "2025-10-13T09:00:00-06:00",
      "variable_type": "soil_moisture",
      "value": "32.5",
      "unit": "%",
      "source": "automatic"
    }
  ]
}
```

#### POST /variables/
Registrar variable individual.

**Request**:
```json
{
  "station_id": 1,
  "timestamp": "2025-10-13T09:00:00-06:00",
  "variable_type": "soil_moisture",
  "value": 32.5,
  "unit": "%",
  "source": "manual"
}
```

#### POST /variables/bulk/
Ingesta masiva (IoT).

**Request**:
```json
{
  "station_id": 1,
  "readings": [
    {
      "timestamp": "2025-10-13T09:00:00-06:00",
      "variable_type": "soil_moisture",
      "value": 32.5,
      "unit": "%"
    },
    {
      "timestamp": "2025-10-13T09:00:00-06:00",
      "variable_type": "air_temp",
      "value": 28.3,
      "unit": "°C"
    }
  ]
}
```

**Response 201**:
```json
{
  "created": 2,
  "failed": 0
}
```

### 3.9 Reportes y KPIs

#### GET /reports/traceability/
Reporte de trazabilidad por lote.

**Query Params**:
- `field_id`: Requerido
- `from`: Fecha inicio
- `to`: Fecha fin
- `format`: json/csv/excel/pdf

**Response** (json):
```json
{
  "field": {
    "id": "abc-123-...",
    "name": "Parcela 5A"
  },
  "period": {
    "from": "2025-01-01",
    "to": "2025-12-31"
  },
  "summary": {
    "total_events": 120,
    "by_category": {
      "riego": 45,
      "fertilizacion": 20,
      "fitosanitarios": 15,
      "labores": 25,
      "cosecha": 10,
      "otros": 5
    }
  },
  "events": [...]
}
```

#### GET /reports/kpis/
KPIs calculados.

**Query Params**:
- `field_id`: Opcional
- `campaign_id`: Opcional
- `from`, `to`: Rango de fechas

**Response**:
```json
{
  "irrigation_efficiency": {
    "total_volume_m3": 2500,
    "total_duration_hours": 450,
    "avg_soil_moisture_increase_pct": 12.5
  },
  "fertilization_impact": {
    "total_kg_applied": 1200,
    "avg_ndre_increase": 0.08
  },
  "pest_incidents": 8,
  "harvest_yield_kg_ha": 35000
}
```

### 3.10 Auditoría

#### GET /audit-logs/
Consultar logs de auditoría (solo ADMIN).

**Query Params**:
- `user_id`: Filtrar por usuario
- `action`: Tipo de acción
- `entity`: Tipo de entidad
- `from`, `to`: Rango de fechas

**Response**:
```json
{
  "count": 350,
  "results": [
    {
      "id": 12345,
      "user": {
        "id": 5,
        "username": "jperez"
      },
      "action": "CREATE_EVENT",
      "entity": "Event",
      "entity_id": "def-456-...",
      "timestamp": "2025-10-13T09:00:15-06:00",
      "ip_address": "192.168.1.100"
    }
  ]
}
```

## 4. Códigos de Error

```json
{
  "error": "Validation Error",
  "code": "VALIDATION_ERROR",
  "details": {
    "field_name": ["Error message"]
  }
}
```

**Códigos Comunes**:
- `VALIDATION_ERROR`: Datos inválidos
- `AUTHENTICATION_REQUIRED`: No autenticado
- `PERMISSION_DENIED`: Sin permisos
- `NOT_FOUND`: Recurso no existe
- `RATE_LIMIT_EXCEEDED`: Límite excedido
- `SCHEMA_VALIDATION_FAILED`: Payload no válido contra esquema

## 5. Documentación Interactiva

### Swagger UI
```
http://localhost:8000/api/docs/
```

### ReDoc
```
http://localhost:8000/api/redoc/
```

### OpenAPI Schema (JSON)
```
http://localhost:8000/api/schema/
```

---

**Siguiente**: [Sistema de Eventos Dinámicos →](./07_eventos_dinamicos.md)

[← Volver al índice](../README.md)
