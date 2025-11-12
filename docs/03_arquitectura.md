# Arquitectura del Sistema

[← Volver al índice](../README.md) | [← Requerimientos](./02_requerimientos.md) | [Modelo de Dominio →](./04_modelo_dominio.md)

## 1. Visión de Arquitectura

### 1.1 Estilo Arquitectónico

El sistema adopta una **arquitectura en capas** con separación clara de responsabilidades, manteniendo la máxima simplicidad para un MVP:

- **Capa de Presentación**: Interfaz web (Django Templates + HTMX/Alpine.js)
- **Capa de API**: Django REST Framework
- **Capa de Lógica de Negocio**: Servicios y validadores Django
- **Capa de Acceso a Datos**: Django ORM + PostgreSQL
- **Capa de Persistencia**: PostgreSQL con JSONB

> **Nota MVP**: El sistema está diseñado para minimizar complejidad y maximizar velocidad de implementación. Los tipos de eventos son fijos y predefinidos (10 tipos), lo que simplifica significativamente la implementación y reduce errores de validación.

### 1.2 Diagrama de Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                      │
├──────────────────────────┬──────────────────────────────────┤
│   Interfaz Web (HTML)    │    Aplicaciones Externas         │
│   Django Templates       │    Móviles / IoT                 │
│   HTMX + Alpine.js       │    Integraciones                 │
└──────────────────────────┴──────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      CAPA DE API                             │
│                Django REST Framework                         │
│    ┌──────────┬──────────┬──────────┬──────────────┐       │
│    │  Auth    │ Catalogs │  Events  │  Variables   │       │
│    │  JWT     │  API     │  API     │  API         │       │
│    └──────────┴──────────┴──────────┴──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   CAPA DE LÓGICA DE NEGOCIO                  │
│                                                               │
│  ┌───────────┐  ┌──────────────┐  ┌─────────────┐          │
│  │  Servicios│  │  Validadores │  │  Eventos    │          │
│  │  Negocio  │  │  JSON Schema │  │  (Fijos)    │          │
│  └───────────┘  └──────────────┘  └─────────────┘          │
│                                                               │
│  ┌───────────┐  ┌──────────────┐  ┌─────────────┐          │
│  │  KPIs &   │  │  Auditoría   │  │  Gestión    │          │
│  │  Reportes │  │  Logging     │  │  Archivos   │          │
│  └───────────┘  └──────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   CAPA DE ACCESO A DATOS                     │
│                      Django ORM                              │
│                                                               │
│  ┌──────┐  ┌────────┐  ┌───────┐  ┌──────────┐            │
│  │Field │  │Campaign│  │Station│  │EventType │            │
│  │Model │  │ Model  │  │ Model │  │  Model   │            │
│  └──────┘  └────────┘  └───────┘  └──────────┘            │
│                                                               │
│  ┌──────┐  ┌─────────┐  ┌───────────┐  ┌─────────┐        │
│  │Event │  │Variable │  │Attachment │  │AuditLog │        │
│  │Model │  │  Model  │  │   Model   │  │  Model  │        │
│  └──────┘  └─────────┘  └───────────┘  └─────────┘        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   CAPA DE PERSISTENCIA                       │
│                      PostgreSQL 15+                          │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐        │
│  │  Tablas     │  │  JSONB para  │  │  PostGIS    │        │
│  │  Normales   │  │  Eventos     │  │  (opcional) │        │
│  └─────────────┘  └──────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 2. Componentes Principales

### 2.1 Módulo Core (Núcleo)

**Responsabilidades**:
- Gestión de usuarios y autenticación
- Roles y permisos (RBAC)
- Auditoría centralizada
- Utilidades comunes
- Middleware personalizado

**Componentes**:
```
core/
├── models.py          # User, Role, Permission, AuditLog
├── auth/
│   ├── jwt_auth.py    # Autenticación JWT
│   ├── permissions.py # Permisos personalizados
├── middleware/
│   ├── audit.py       # Middleware de auditoría
│   ├── timezone.py    # Manejo de zona horaria
├── utils/
│   ├── validators.py
│   ├── helpers.py
```

### 2.2 Módulo Fields (Infraestructura Agrícola)

**Responsabilidades**:
- CRUD de Lotes/Parcelas
- Gestión de Campañas
- Gestión de Estaciones de monitoreo

**Componentes**:
```
fields/
├── models.py          # Field, Campaign, Station
├── views.py
├── serializers.py     # DRF serializers
├── admin.py           # Django admin
├── services/
│   ├── field_service.py
│   ├── campaign_service.py
```

### 2.3 Módulo Events (Sistema de Eventos)

**Responsabilidades**:
- Gestión de tipos de evento predefinidos (10 tipos fijos)
- Validación de esquemas JSON
- CRUD de eventos (Event)
- Gestión de adjuntos
- Renderizado de formularios según esquema

**Componentes**:
```
events/
├── models.py          # EventType, Event, Attachment
├── views.py
├── serializers.py
├── validators/
│   ├── schema_validator.py    # Validación JSON Schema
│   ├── event_validator.py
├── services/
│   ├── event_service.py
│   ├── attachment_service.py
├── management/
│   └── commands/
│       └── setup_event_types.py  # Comando para cargar 10 eventos
├── templates/
│   ├── event_form.html        # Formulario según esquema
```

### 2.4 Módulo Variables

**Responsabilidades**:
- Registro de variables ambientales
- Ingesta manual y automática (IoT)
- Consultas optimizadas por fecha/tipo
- Exportación de datos

**Componentes**:
```
variables/
├── models.py          # Variable
├── views.py
├── serializers.py
├── services/
│   ├── variable_service.py
│   ├── iot_ingestion_service.py
├── exporters/
│   ├── csv_exporter.py
```

### 2.5 Módulo Reports (Reportes y KPIs)

**Responsabilidades**:
- Generación de KPIs
- Reportes personalizados
- Exportación (CSV, Excel, PDF)
- Correlaciones básicas

**Componentes**:
```
reports/
├── views.py
├── services/
│   ├── kpi_calculator.py
│   ├── report_generator.py
├── exporters/
│   ├── excel_exporter.py
│   ├── pdf_exporter.py
├── templates/
│   ├── dashboard.html
│   ├── report_template.html
```

### 2.6 Módulo API

**Responsabilidades**:
- Routers DRF
- Autenticación y permisos API
- Paginación y filtros
- Rate limiting
- Documentación Swagger

**Componentes**:
```
api/
├── v1/
│   ├── routers.py
│   ├── auth.py
│   ├── permissions.py
│   ├── pagination.py
│   ├── filters.py
│   ├── throttling.py
├── docs/
│   ├── swagger_config.py
```

### 2.7 Módulo UI (Interfaz Web)

**Responsabilidades**:
- Vistas web para usuarios
- Dashboard
- Formularios de captura
- Consultas y visualizaciones

**Componentes**:
```
ui/
├── views/
│   ├── dashboard.py
│   ├── events.py
│   ├── traceability.py
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── event_create.html
│   ├── traceability.html
├── static/
│   ├── css/
│   ├── js/
│   ├── img/
```

## 3. Decisiones Arquitectónicas Clave

### 3.1 Sistema de Eventos con JSONB

**Decisión**: Usar campo JSONB de PostgreSQL para almacenar payloads de eventos.

**Alternativas Consideradas**:
1. **Modelo EAV (Entity-Attribute-Value)**: Cada campo en una fila separada
2. **Tablas por tipo de evento**: Una tabla por cada tipo
3. **JSON en texto**: Almacenar como TEXT
4. **JSONB en PostgreSQL**: ✅ Seleccionado

**Justificación**:
- ✅ Flexibilidad para diferentes campos por tipo de evento
- ✅ Validación mediante JSON Schema
- ✅ Consultas eficientes con índices GIN
- ✅ No requiere migraciones por cambios en esquemas
- ✅ Balance entre estructura y flexibilidad
- ✅ Tipos de eventos predefinidos reducen complejidad
- ⚠️ Desventaja: Tipado débil, requiere validación estricta

**Implementación**:
```python
class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    event_type = models.ForeignKey(EventType, on_delete=models.PROTECT)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField()
    payload = models.JSONField()  # JSONB en PostgreSQL
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['field', 'timestamp']),
            models.Index(fields=['event_type']),
            GinIndex(fields=['payload']),  # Para queries en JSONB
        ]
```

### 3.2 Validación con JSON Schema

**Decisión**: Usar JSON Schema para definir y validar esquemas de eventos.

**Justificación**:
- Estándar ampliamente adoptado
- Librerías maduras en Python (`jsonschema`)
- Expresividad para definir tipos, rangos, patrones
- Auto-documentado

**Ejemplo de Esquema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Riego",
  "properties": {
    "metodo": {
      "type": "string",
      "enum": ["goteo", "microaspersion", "gravedad", "aspersion"],
      "description": "Método de riego aplicado"
    },
    "duracion_min": {
      "type": "number",
      "minimum": 0,
      "maximum": 1440,
      "description": "Duración en minutos"
    },
    "volumen_m3": {
      "type": "number",
      "minimum": 0,
      "description": "Volumen de agua aplicado"
    }
  },
  "required": ["metodo", "duracion_min"]
}
```

### 3.3 Autenticación Dual (JWT + Session)

**Decisión**: Usar JWT para API y sesiones tradicionales para web.

**Justificación**:
- **JWT**: Ideal para API, stateless, integración con apps externas
- **Session**: Mejor experiencia en web, CSRF protection nativo
- Permite flexibilidad según canal de acceso

### 3.4 PostgreSQL como BD Única

**Decisión**: PostgreSQL para todo (transaccional + JSONB + geoespacial).

**Alternativas Consideradas**:
1. PostgreSQL + MongoDB (eventos en Mongo)
2. PostgreSQL + TimescaleDB (variables en time-series DB)
3. Solo PostgreSQL ✅

**Justificación**:
- Reduce complejidad operativa
- JSONB ofrece flexibilidad similar a MongoDB
- PostGIS para georreferenciación
- Mantenimiento más simple
- Transacciones ACID completas

### 3.5 Apps Django Modulares

**Decisión**: Separar funcionalidad en Django apps independientes.

**Justificación**:
- Cohesión alta, acoplamiento bajo
- Facilita testing unitario
- Posible extracción a microservicios futuro
- Mejor organización del código

## 4. Patrones de Diseño Aplicados

### 4.1 Repository Pattern (implícito en ORM)

Django ORM actúa como repositorio, abstrayendo acceso a datos.

### 4.2 Service Layer

Lógica de negocio compleja en servicios, no en vistas ni modelos.

```python
# events/services/event_service.py
class EventService:
    @staticmethod
    def create_event(event_type_id, field_id, campaign_id, timestamp, payload, user):
        # 1. Validar contra esquema
        event_type = EventType.objects.get(id=event_type_id)
        validate_json(payload, event_type.schema)
        
        # 2. Crear evento
        event = Event.objects.create(
            event_type=event_type,
            field_id=field_id,
            campaign_id=campaign_id,
            timestamp=timestamp,
            payload=payload,
            created_by=user
        )
        
        # 3. Auditar
        AuditLog.objects.create(
            user=user,
            action='CREATE_EVENT',
            entity='Event',
            entity_id=str(event.id)
        )
        
        return event
```

### 4.3 Strategy Pattern (Validadores)

Diferentes estrategias de validación según tipo de campo.

```python
class FieldValidator:
    def validate(self, value, schema):
        raise NotImplementedError

class NumberValidator(FieldValidator):
    def validate(self, value, schema):
        if 'minimum' in schema and value < schema['minimum']:
            raise ValidationError(...)
        # ...

class StringValidator(FieldValidator):
    # ...
```

### 4.4 Comando de Inicialización (Eventos Predefinidos)

Comando Django para cargar los 10 tipos de eventos predefinidos.

```python
# events/management/commands/setup_event_types.py
class Command(BaseCommand):
    def handle(self, *args, **options):
        event_types = [
            {
                'name': 'Aplicación de Riego',
                'category': 'riego',
                'schema': {...}
            },
            # ... otros 9 tipos
        ]
        for event_data in event_types:
            EventType.objects.get_or_create(
                name=event_data['name'],
                defaults=event_data
            )
```

### 4.5 Decorator Pattern (Auditoría)

Decorador para auditar automáticamente acciones.

```python
def audit_action(action_name):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            result = func(request, *args, **kwargs)
            AuditLog.objects.create(
                user=request.user,
                action=action_name,
                # ...
            )
            return result
        return wrapper
    return decorator

@audit_action('UPDATE_EVENT')
def update_event_view(request, event_id):
    # ...
```

## 5. Flujos de Datos Clave

### 5.1 Flujo de Creación de Evento

```
Usuario → Vista Web → Validación Formulario → Service Layer
                                                    ↓
                                            Validación JSON Schema
                                                    ↓
                                            Django ORM (Event.save())
                                                    ↓
                                            PostgreSQL (INSERT)
                                                    ↓
                                            Auditoría (AuditLog)
                                                    ↓
                                            Response → Usuario
```

### 5.2 Flujo de Consulta de Trazabilidad

```
Usuario → API/Web → Filters + Pagination → QuerySet
                                               ↓
                                        PostgreSQL (SELECT con JOINs)
                                               ↓
                                        Serialización (DRF/Template)
                                               ↓
                                        Response JSON/HTML
```

### 5.3 Flujo de Ingesta IoT

```
Dispositivo IoT → API POST /variables/bulk → Auth JWT
                                               ↓
                                        Validación Payload
                                               ↓
                                        Bulk Insert (PostgreSQL)
                                               ↓
                                        Response 201 Created
```

## 6. Seguridad

### 6.1 Capas de Seguridad

```
┌─────────────────────────────────────────────┐
│  HTTPS (TLS 1.2+)                           │
├─────────────────────────────────────────────┤
│  Rate Limiting (100 req/min)                │
├─────────────────────────────────────────────┤
│  Autenticación (JWT / Session)              │
├─────────────────────────────────────────────┤
│  Autorización (RBAC)                        │
├─────────────────────────────────────────────┤
│  Validación de Inputs                       │
├─────────────────────────────────────────────┤
│  Sanitización (SQL Injection, XSS)          │
├─────────────────────────────────────────────┤
│  Auditoría                                  │
└─────────────────────────────────────────────┘
```

### 6.2 Principios de Seguridad

- **Defense in Depth**: Múltiples capas
- **Least Privilege**: Permisos mínimos necesarios
- **Fail Securely**: Errores no exponen información sensible
- **Complete Mediation**: Validar siempre en backend

## 7. Escalabilidad y Rendimiento

### 7.1 Estrategias de Optimización

1. **Índices de BD**:
   - Índices en campos de filtrado frecuente
   - GIN index en JSONB
   - Índices compuestos (field_id, timestamp)

2. **Paginación**:
   - Todas las listas paginadas (50 items/página)
   - Cursor-based pagination para grandes volúmenes

3. **Caché** (futuro):
   - Redis para catálogos (lotes, campañas)
   - Cache de reportes generados

4. **Query Optimization**:
   - select_related / prefetch_related
   - Evitar N+1 queries
   - Agregaciones en BD, no en Python

### 7.2 Puntos de Escalabilidad Futura

- Separar API en servicio independiente
- Read replicas de PostgreSQL
- CDN para archivos estáticos
- Queue de tareas asíncronas (Celery) para reportes pesados

## 8. Tecnologías y Librerías

| Categoría | Tecnología | Versión | Justificación |
|-----------|-----------|---------|---------------|
| **Backend** | Python | 3.11+ | Moderno, tipado estático opcional |
| **Framework** | Django | 5.0 | Maduro, ORM potente, admin |
| **API** | Django REST Framework | 3.14+ | Estándar de facto |
| **BD** | PostgreSQL | 15+ | JSONB, PostGIS, robustez |
| **Autenticación** | djangorestframework-simplejwt | 5.3+ | JWT para DRF |
| **Validación JSON** | jsonschema | 4.x | Estándar JSON Schema |
| **Testing** | pytest-django | 4.x | Mejor que unittest |
| **Documentación API** | drf-spectacular | 0.27+ | OpenAPI 3.0 |
| **CORS** | django-cors-headers | 4.x | Control CORS |
| **Docker** | Docker + Docker Compose | - | Containerización |
| **Excel Export** | openpyxl | 3.x | Exportación Excel |

## 9. Despliegue

### 9.1 Arquitectura de Despliegue con Docker (MVP)

El sistema utiliza **Docker** para simplificar el despliegue y asegurar consistencia entre entornos:

```
┌─────────────────────────────────────────────┐
│         Docker Compose                      │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  Container: Django + Gunicorn         │ │
│  │  - Web Application                     │ │
│  │  - API REST                             │ │
│  └─────────────────┬──────────────────────┘ │
│                    ↓                         │
│  ┌────────────────────────────────────────┐ │
│  │  Container: PostgreSQL 15             │ │
│  │  - Database                             │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  Volumes:                                   │
│  - postgres_data                            │
│  - media_files                               │
│  - static_files                              │
└─────────────────────────────────────────────┘
```

**Docker Compose Configuration** (simplificada):
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: traceability
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres

  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    depends_on:
      - db

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### 9.1.1 Arquitectura de Producción (Futura)

```
┌─────────────────────────────────────────────┐
│         Servidor Linux (Ubuntu 22.04)       │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  Nginx (Reverse Proxy + Static Files) │ │
│  └─────────────────┬──────────────────────┘ │
│                    ↓                         │
│  ┌────────────────────────────────────────┐ │
│  │  Docker: Gunicorn + Django              │ │
│  └─────────────────┬──────────────────────┘ │
│                    ↓                         │
│  ┌────────────────────────────────────────┐ │
│  │  Docker: PostgreSQL 15                │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### 9.2 Variables de Entorno

```bash
# .env
DEBUG=False
SECRET_KEY=<generated>
DATABASE_URL=postgres://user:pass@localhost/traceability
ALLOWED_HOSTS=example.com,www.example.com
CORS_ALLOWED_ORIGINS=https://example.com

# Timezone
TZ=America/Mexico_City

# JWT
JWT_SECRET_KEY=<generated>
JWT_EXPIRATION_HOURS=1

# File Storage
MEDIA_ROOT=/var/www/traceability/media
MEDIA_URL=/media/

# Email (para notificaciones futuras)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
```

---

**Siguiente**: [Modelo de Dominio →](./04_modelo_dominio.md)

[← Volver al índice](../README.md)
