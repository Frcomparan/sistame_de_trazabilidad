# Estructura de URLs - Sistema de Trazabilidad

## 📋 Organización General

El sistema separa claramente las URLs entre **interfaces web** (HTML/templates) y **API REST** (JSON).

---

## 🌐 RUTAS WEB (Interfaces HTML)

### Autenticación
- `GET /` → Redirige a `/login/`
- `GET /login/` → Formulario de inicio de sesión
- `POST /login/` → Procesar inicio de sesión
- `POST /logout/` → Cerrar sesión

### Panel de Administración
- `GET /admin/` → Panel de administración Django

### Dashboard
- `GET /dashboard/` → Dashboard principal del usuario

### Catálogos
- **Campos (Fields)**
  - `GET /catalogs/fields/` → Lista de campos
  - `GET /catalogs/fields/create/` → Formulario crear campo
  - `POST /catalogs/fields/create/` → Guardar nuevo campo
  - `GET /catalogs/fields/<uuid>/edit/` → Formulario editar campo
  - `POST /catalogs/fields/<uuid>/edit/` → Guardar cambios
  - `GET /catalogs/fields/<uuid>/delete/` → Confirmación eliminar
  - `POST /catalogs/fields/<uuid>/delete/` → Eliminar campo

- **Campañas (Campaigns)**
  - `GET /catalogs/campaigns/` → Lista de campañas
  - `GET /catalogs/campaigns/create/` → Formulario crear campaña
  - `POST /catalogs/campaigns/create/` → Guardar nueva campaña
  - `GET /catalogs/campaigns/<uuid>/edit/` → Formulario editar campaña
  - `POST /catalogs/campaigns/<uuid>/edit/` → Guardar cambios
  - `GET /catalogs/campaigns/<uuid>/delete/` → Confirmación eliminar
  - `POST /catalogs/campaigns/<uuid>/delete/` → Eliminar campaña

### Eventos (TODO)
- `GET /events/` → Lista de eventos (pendiente)
- `GET /events/create/` → Crear evento (pendiente)
- etc.

### Reportes (TODO)
- `GET /reports/` → Dashboard de reportes (pendiente)
- etc.

---

## 🔌 RUTAS API REST (JSON)

### Documentación API
- `GET /api/schema/` → OpenAPI Schema (JSON)
- `GET /api/docs/` → Swagger UI (documentación interactiva)

### Autenticación (JWT)
- `POST /api/v1/auth/token/` → Obtener token JWT
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```
- `POST /api/v1/auth/token/refresh/` → Refrescar token
  ```json
  {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
  ```

### Catálogos
- **Fields**
  - `GET /api/v1/catalogs/fields/` → Listar campos (JSON)
  
- **Campaigns**
  - `GET /api/v1/catalogs/campaigns/` → Listar campañas (JSON)

### Eventos
- `GET /api/v1/events/` → Listar eventos (JSON)

### Reportes
- `GET /api/v1/reports/health/` → Health check del sistema

---

## 📁 Estructura de Archivos

Cada app tiene dos archivos de URLs separados:

```
apps/
├── core/
│   ├── urls.py       # Rutas web (dashboard)
│   └── api_urls.py   # Rutas API (JWT tokens)
├── catalogs/
│   ├── urls.py       # Rutas web (CRUD de campos y campañas)
│   └── api_urls.py   # Rutas API (endpoints JSON)
├── events/
│   ├── urls.py       # Rutas web (TODO: implementar)
│   └── api_urls.py   # Rutas API (listado de eventos)
└── reports/
    ├── urls.py       # Rutas web (TODO: implementar)
    └── api_urls.py   # Rutas API (health check)
```

---

## 🎯 Convenciones

### URLs Web (Templates)
- **Propósito**: Interfaces HTML para usuarios humanos
- **Respuesta**: HTML renderizado con templates Django
- **Autenticación**: Django sessions (`@login_required`)
- **Patrón**: `/modulo/entidad/accion/`
- **Ejemplos**:
  - `/catalogs/fields/` → Lista HTML
  - `/catalogs/campaigns/create/` → Formulario HTML

### URLs API (REST)
- **Propósito**: Endpoints para consumo programático (móvil, SPA, integraciones)
- **Respuesta**: JSON
- **Autenticación**: JWT Bearer tokens
- **Patrón**: `/api/v1/modulo/entidad/`
- **Ejemplos**:
  - `/api/v1/catalogs/fields/` → JSON array
  - `/api/v1/auth/token/` → JWT token

---

## 🔒 Autenticación

### Interfaces Web
- Usa **Django Sessions**
- Login en `/login/`
- Cookie de sesión automática
- Decorador `@login_required`

### API REST
- Usa **JWT (JSON Web Tokens)**
- Obtener token en `/api/v1/auth/token/`
- Header: `Authorization: Bearer <token>`
- Token expira en 1 hora (configurable)

---

## 📊 Resumen de Endpoints Principales

| URL | Tipo | Propósito |
|-----|------|-----------|
| `/` | Web | Página inicial (→ login) |
| `/dashboard/` | Web | Dashboard usuario |
| `/catalogs/fields/` | Web | Gestión de campos |
| `/catalogs/campaigns/` | Web | Gestión de campañas |
| `/admin/` | Web | Panel administración |
| `/api/docs/` | Web | Documentación API |
| `/api/v1/auth/token/` | API | Obtener JWT |
| `/api/v1/catalogs/fields/` | API | Datos de campos (JSON) |
| `/api/v1/catalogs/campaigns/` | API | Datos de campañas (JSON) |
| `/api/v1/events/` | API | Datos de eventos (JSON) |
| `/api/v1/reports/health/` | API | Health check (JSON) |

---

## 🚀 Próximos Pasos

1. **Implementar CRUD completo en APIs** (POST, PUT, DELETE)
2. **Crear interfaces web para Events** (`/events/`)
3. **Crear interfaces web para Reports** (`/reports/`)
4. **Agregar paginación a APIs**
5. **Agregar filtros y búsqueda a APIs**
6. **Implementar permisos granulares**
