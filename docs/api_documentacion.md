# Documentación de la API - Guía Rápida

## 📚 Acceso a la Documentación Interactiva

La API REST del Sistema de Trazabilidad Agrícola está completamente documentada usando **OpenAPI 3.0** (anteriormente Swagger).

### URLs de Documentación

- **Swagger UI (Interactiva)**: http://localhost:8000/api/docs/
- **Schema OpenAPI (JSON)**: http://localhost:8000/api/schema/

La documentación interactiva en `/api/docs/` permite:
- ✅ Explorar todos los endpoints disponibles
- ✅ Ver descripciones detalladas de cada operación
- ✅ Conocer los parámetros requeridos y opcionales
- ✅ Ver ejemplos de peticiones y respuestas
- ✅ Probar los endpoints directamente desde el navegador
- ✅ Autenticar y ejecutar peticiones reales

---

## 🔐 Autenticación

La API utiliza **JWT (JSON Web Tokens)** para autenticación.

### Obtener Token

**Endpoint**: `POST /api/v1/auth/token/`

```json
// Request
{
  "username": "admin",
  "password": "admin123"
}

// Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Administrador",
    "is_staff": true,
    "is_superuser": true
  }
}
```

### Usar Token

Incluir en el header de todas las peticiones protegidas:

```
Authorization: Bearer {access_token}
```

### Refrescar Token

**Endpoint**: `POST /api/v1/auth/token/refresh/`

```json
// Request
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

// Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Duración de tokens:**
- Access Token: 60 minutos
- Refresh Token: 24 horas

---

## 🌾 Módulos de la API

### 1. Catálogos - Campos (Fields)

Gestión de parcelas o terrenos de cultivo.

#### Listar Campos
**GET** `/api/v1/catalogs/fields/`

**Query Parameters:**
- `is_active` (boolean): Filtrar por estado (true/false)

**Ejemplo de Respuesta:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "code": "FIELD-001",
    "name": "Parcela Norte",
    "surface_ha": 2.50,
    "is_active": true
  }
]
```

**Casos de uso:**
- Consultar campos disponibles para asignar a campañas
- Obtener información de superficie total cultivada
- Filtrar campos por estado

---

### 2. Catálogos - Campañas (Campaigns)

Gestión de ciclos productivos o temporadas de cultivo.

#### Listar Campañas
**GET** `/api/v1/catalogs/campaigns/`

**Query Parameters:**
- `is_active` (boolean): Filtrar por estado (true/false)
- `season` (string): Filtrar por temporada

**Ejemplo de Respuesta:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Campaña Verano 2024",
    "season": "Verano 2024",
    "variety": "Eureka",
    "start_date": "2024-01-15",
    "end_date": null,
    "is_active": true
  }
]
```

**Casos de uso:**
- Consultar campañas disponibles para registro de eventos
- Obtener información de ciclos productivos por temporada
- Filtrar campañas activas o finalizadas

---

### 3. Eventos de Trazabilidad

Registro y consulta de eventos durante el ciclo de cultivo.

#### Listar Eventos
**GET** `/api/v1/events/`

**Query Parameters:**
- `event_type` (UUID): Filtrar por tipo de evento
- `date_from` (date): Fecha inicial (YYYY-MM-DD)
- `date_to` (date): Fecha final (YYYY-MM-DD)

**Ejemplo de Respuesta:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440010",
    "event_type": "550e8400-e29b-41d4-a716-446655440020",
    "event_type_name": "Riego",
    "field": "550e8400-e29b-41d4-a716-446655440000",
    "field_name": "Parcela Norte",
    "timestamp": "2024-10-27T10:30:00Z",
    "observations": "Riego por goteo - 2 horas"
  }
]
```

#### Listar Tipos de Eventos
**GET** `/api/v1/events/types/`

**Query Parameters:**
- `category` (string): Filtrar por categoría
- `is_active` (boolean): Filtrar por estado

**Casos de uso:**
- Consultar historial de actividades
- Auditar trazabilidad de productos
- Generar reportes de actividades
- Análisis de prácticas agrícolas

---

### 4. Sistema - Reportes

Endpoints de sistema y monitoreo.

#### Health Check
**GET** `/api/v1/reports/health/`

**Respuesta:**
```json
{
  "status": "ok",
  "service": "Sistema de Trazabilidad Agrícola",
  "version": "1.0.0"
}
```

**Casos de uso:**
- Monitoreo de disponibilidad del servicio
- Validación en balanceadores de carga
- Pruebas de conectividad

---

## 📋 Características de la Documentación

### Por Endpoint

Cada endpoint incluye:

1. **Resumen**: Descripción breve de la funcionalidad
2. **Descripción Detallada**: Explicación completa con contexto
3. **Casos de Uso**: Ejemplos de cuándo usar el endpoint
4. **Parámetros**: Query params, path params y body params
5. **Respuestas**: Códigos HTTP y estructura de datos
6. **Ejemplos**: Request y response samples

### Organización por Tags

Los endpoints están organizados en categorías:

- 🔐 **Autenticación**: JWT tokens
- 🌾 **Catálogos - Campos**: Gestión de parcelas
- 📅 **Catálogos - Campañas**: Ciclos productivos
- 📋 **Eventos de Trazabilidad**: Registro de actividades
- 📊 **Sistema - Reportes**: Monitoreo y reportes

### Información del Proyecto

La documentación incluye:
- Descripción general del sistema
- Módulos principales
- Flujo de autenticación
- Versionado de la API
- Contacto y soporte

---

## 🚀 Probando la API

### Usando Swagger UI

1. Abre http://localhost:8000/api/docs/
2. Haz clic en el endpoint que quieres probar
3. Haz clic en "Try it out"
4. Completa los parámetros necesarios
5. Haz clic en "Execute"
6. Revisa la respuesta

### Autenticación en Swagger

1. Obtén un token desde `/api/v1/auth/token/`
2. Haz clic en el botón "Authorize" en la parte superior
3. Ingresa: `Bearer {tu_access_token}`
4. Ahora puedes probar endpoints protegidos

### Usando curl

```bash
# Obtener token
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Usar token
curl http://localhost:8000/api/v1/catalogs/fields/ \
  -H "Authorization: Bearer {access_token}"
```

### Usando Python

```python
import requests

# Obtener token
response = requests.post(
    'http://localhost:8000/api/v1/auth/token/',
    json={'username': 'admin', 'password': 'admin123'}
)
tokens = response.json()
access_token = tokens['access']

# Hacer petición autenticada
headers = {'Authorization': f'Bearer {access_token}'}
fields = requests.get(
    'http://localhost:8000/api/v1/catalogs/fields/',
    headers=headers
).json()
```

---

## 📊 Formato de Respuestas

### Respuestas Exitosas

- **200 OK**: Petición exitosa
- **201 Created**: Recurso creado exitosamente
- **204 No Content**: Operación exitosa sin contenido

### Errores

- **400 Bad Request**: Datos inválidos
- **401 Unauthorized**: No autenticado
- **403 Forbidden**: Sin permisos
- **404 Not Found**: Recurso no encontrado
- **500 Internal Server Error**: Error del servidor

### Estructura de Errores

```json
{
  "detail": "Mensaje de error descriptivo",
  "field_name": ["Error específico del campo"]
}
```

---

## 🔄 Versionado

- **Versión Actual**: v1
- **Base URL**: `/api/v1/`
- **Formato**: Todas las rutas incluyen el prefijo de versión

Cuando se lance v2, la v1 seguirá disponible para compatibilidad hacia atrás.

---

## 📝 Notas Importantes

1. **IDs son UUIDs**: Todos los recursos usan UUIDs en lugar de enteros
2. **Fechas en ISO 8601**: Formato YYYY-MM-DD o YYYY-MM-DDTHH:MM:SSZ
3. **JSON únicamente**: Content-Type debe ser `application/json`
4. **UTF-8**: Codificación de caracteres UTF-8
5. **CORS**: Configurado para desarrollo (localhost)

---

## 🛠️ Tecnologías

- **Framework**: Django REST Framework
- **Documentación**: drf-spectacular (OpenAPI 3.0)
- **Autenticación**: Simple JWT
- **Base de Datos**: PostgreSQL
- **Servidor**: Django Development Server / Gunicorn

---

## 📞 Soporte

- **Documentación Completa**: Ver carpeta `/docs`
- **Código Fuente**: https://github.com/Frcomparan/sistame_de_trazabilidad
- **Swagger UI**: http://localhost:8000/api/docs/

---

**Última actualización**: 27 de octubre de 2025  
**Versión de la API**: 1.0.0
