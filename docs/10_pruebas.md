# Plan de Pruebas

[← Volver al índice](../README.md) | [← Riesgos](./09_riesgos.md) | [Glosario →](./glosario.md)

## 1. Introducción

Este documento define la estrategia, tipos de pruebas, casos de prueba y criterios de aceptación para asegurar la calidad del sistema de trazabilidad.

## 2. Objetivos de Testing

- ✅ Cobertura de código > 70%
- ✅ Cero defectos críticos en producción
- ✅ Validación funcional completa
- ✅ Performance dentro de SLA
- ✅ Seguridad validada (OWASP Top 10)

## 3. Tipos de Pruebas

### 3.1 Pirámide de Testing

```
                  ┌───────────┐
                  │  E2E (5%) │  ← Manual + Automatizado
                  └───────────┘
              ┌─────────────────┐
              │ Integración(25%)│  ← pytest
              └─────────────────┘
          ┌───────────────────────┐
          │  Unitarias (70%)      │  ← pytest + coverage
          └───────────────────────┘
```

### 3.2 Pruebas Unitarias

**Herramienta**: pytest + pytest-django  
**Cobertura Objetivo**: 70%+

**Áreas Críticas**:
- Validadores (JSON Schema)
- Servicios (EventService, VariableService)
- Modelos (clean(), métodos de negocio)
- Serializers (DRF)

**Ejemplo**:
```python
# tests/events/test_validators.py
import pytest
from events.validators import SchemaValidator
from django.core.exceptions import ValidationError

class TestSchemaValidator:
    def test_validate_valid_payload(self):
        schema = {
            "type": "object",
            "properties": {
                "metodo": {"type": "string"},
                "duracion_min": {"type": "number"}
            },
            "required": ["metodo"]
        }
        payload = {"metodo": "goteo", "duracion_min": 90}
        
        # No debe lanzar excepción
        SchemaValidator.validate(payload, schema)
    
    def test_validate_missing_required_field(self):
        schema = {
            "type": "object",
            "properties": {
                "metodo": {"type": "string"}
            },
            "required": ["metodo"]
        }
        payload = {}
        
        with pytest.raises(ValidationError):
            SchemaValidator.validate(payload, schema)
    
    def test_validate_wrong_type(self):
        schema = {
            "type": "object",
            "properties": {
                "duracion_min": {"type": "number"}
            }
        }
        payload = {"duracion_min": "invalid"}
        
        with pytest.raises(ValidationError):
            SchemaValidator.validate(payload, schema)
```

### 3.3 Pruebas de Integración

**Herramienta**: pytest + Django TestCase  
**Áreas**:
- Flujos completos (crear evento end-to-end)
- Interacción entre servicios
- Transacciones de BD
- API endpoints

**Ejemplo**:
```python
# tests/events/test_event_service.py
import pytest
from django.contrib.auth import get_user_model
from events.services import EventService
from events.models import EventType, Event
from fields.models import Field, Campaign

@pytest.mark.django_db
class TestEventService:
    def test_create_event_success(self):
        # Setup
        user = get_user_model().objects.create_user(username='test')
        field = Field.objects.create(name='Test Field', code='TF1', surface_ha=10)
        campaign = Campaign.objects.create(name='2025', start_date='2025-01-01')
        event_type = EventType.objects.create(
            name='Riego',
            category='riego',
            schema={
                "type": "object",
                "properties": {
                    "metodo": {"type": "string"}
                },
                "required": ["metodo"]
            }
        )
        
        # Ejecutar
        event = EventService.create_event(
            event_type_id=event_type.id,
            field_id=field.id,
            campaign_id=campaign.id,
            timestamp='2025-10-13 08:00:00',
            payload={"metodo": "goteo"},
            observations="Test",
            user=user
        )
        
        # Verificar
        assert event.id is not None
        assert event.payload['metodo'] == 'goteo'
        assert Event.objects.count() == 1
```

### 3.4 Pruebas de API (Integración)

**Herramienta**: pytest + DRF APITestCase

**Ejemplo**:
```python
# tests/api/test_events_api.py
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

@pytest.mark.django_db
class TestEventsAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_list_events(self):
        response = self.client.get('/api/v1/events/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
    
    def test_create_event_without_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/v1/events/', {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_event_invalid_payload(self):
        # Payload no valida contra schema
        response = self.client.post('/api/v1/events/', {
            'event_type_id': 1,
            'field_id': 'invalid-uuid',
            'timestamp': '2025-10-13T08:00:00Z',
            'payload': {}  # Faltan campos requeridos
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
```

### 3.5 Pruebas End-to-End (E2E)

**Herramienta**: Playwright o Selenium  
**Áreas**:
- Flujos de usuario completos
- Interfaz web

**Casos Críticos**:
1. Login → Dashboard → Crear Evento → Verificar en Trazabilidad
2. Admin crea EventType → Técnico captura evento con nuevo tipo
3. Exportar reporte Excel con filtros

**Ejemplo** (Playwright):
```python
# tests/e2e/test_create_event_flow.py
from playwright.sync_api import Page, expect

def test_create_event_flow(page: Page):
    # Login
    page.goto('http://localhost:8000/login/')
    page.fill('input[name="username"]', 'testuser')
    page.fill('input[name="password"]', 'testpass')
    page.click('button[type="submit"]')
    
    # Navegar a crear evento
    page.click('a:has-text("Nuevo Evento")')
    expect(page).to_have_url('/events/create/')
    
    # Llenar formulario
    page.select_option('select[name="field_id"]', label='Parcela 5A')
    page.select_option('select[name="event_type_id"]', label='Riego')
    page.fill('input[name="timestamp"]', '2025-10-13T08:00')
    page.select_option('select[name="metodo"]', 'goteo')
    page.fill('input[name="duracion_min"]', '90')
    
    # Enviar
    page.click('button[type="submit"]')
    
    # Verificar éxito
    expect(page).to_have_url('/events/')
    expect(page.locator('.alert-success')).to_be_visible()
```

### 3.6 Pruebas de Carga

**Herramienta**: Locust  
**Objetivos**:
- 50 usuarios concurrentes
- 100 req/min sostenido
- Latencia p95 < 500ms (API)

**Ejemplo**:
```python
# tests/load/locustfile.py
from locust import HttpUser, task, between

class TraceabilityUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post('/api/v1/auth/login/', json={
            'username': 'loadtest',
            'password': 'loadtest'
        })
        self.token = response.json()['access']
        self.client.headers['Authorization'] = f'Bearer {self.token}'
    
    @task(3)
    def list_events(self):
        self.client.get('/api/v1/events/')
    
    @task(1)
    def create_event(self):
        self.client.post('/api/v1/events/', json={
            'event_type_id': 1,
            'field_id': 'abc-123',
            'campaign_id': 1,
            'timestamp': '2025-10-13T08:00:00Z',
            'payload': {'metodo': 'goteo', 'duracion_min': 90}
        })
    
    @task(2)
    def get_traceability(self):
        self.client.get('/api/v1/events/?field_id=abc-123')
```

### 3.7 Pruebas de Seguridad

**Áreas OWASP Top 10**:
1. ✅ SQL Injection (Django ORM protege)
2. ✅ XSS (Django templates auto-escape)
3. ✅ CSRF (Django middleware)
4. ✅ Autenticación rota (JWT expiración)
5. ✅ Control de acceso (RBAC)
6. ✅ Configuración insegura (settings prod)
7. ✅ Datos sensibles (HTTPS, passwords hash)
8. ✅ Deserialización insegura (validar JSON)
9. ✅ Componentes vulnerables (pip audit)
10. ✅ Logging insuficiente (auditoría)

**Herramientas**:
- `bandit` (análisis estático Python)
- `safety` (vulnerabilidades en dependencias)
- OWASP ZAP (pruebas penetración)

```bash
# Ejecutar auditoría de seguridad
bandit -r . -ll
safety check
```

### 3.8 Pruebas de Usabilidad

**Método**: Sesiones con usuarios reales  
**Participantes**: 3-5 técnicos de campo  
**Tareas**:
1. Registrar evento de riego
2. Consultar trazabilidad de un lote
3. Exportar reporte

**Métricas**:
- Tiempo de completar tarea
- Errores cometidos
- Satisfacción (escala 1-5)

**Criterio de Éxito**: Tarea 1 < 3 minutos, satisfacción > 4/5

## 4. Casos de Prueba Críticos

### CP-001: Validación de Evento contra Schema

**Prioridad**: Crítica  
**Tipo**: Unitaria

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Crear EventType con schema que requiere "metodo" | EventType creado |
| 2 | Intentar crear Event sin campo "metodo" | ValidationError |
| 3 | Crear Event con "metodo" = "goteo" | Event creado exitosamente |

### CP-002: Trazabilidad Completa por Lote

**Prioridad**: Crítica  
**Tipo**: Integración

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Crear 10 eventos para Lote A | 10 eventos creados |
| 2 | Consultar trazabilidad de Lote A | 10 eventos retornados |
| 3 | Filtrar por tipo "Riego" | Solo eventos de riego |
| 4 | Filtrar por rango de fechas | Solo eventos en rango |

### CP-003: API Create Event con JWT

**Prioridad**: Alta  
**Tipo**: API

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | POST /auth/login/ con credenciales | Token JWT retornado |
| 2 | POST /events/ sin token | 401 Unauthorized |
| 3 | POST /events/ con token válido | 201 Created |
| 4 | POST /events/ con token expirado | 401 Unauthorized |

### CP-004: Performance de Consulta con 10k Eventos

**Prioridad**: Alta  
**Tipo**: Performance

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Crear 10,000 eventos | Eventos creados |
| 2 | Consultar trazabilidad de 1 lote (100 eventos) | < 2 segundos |
| 3 | Consultar trazabilidad de 1 lote (1000 eventos) | < 3 segundos |

### CP-005: Formulario Dinámico desde Schema

**Prioridad**: Crítica  
**Tipo**: E2E

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Admin crea EventType "Análisis Suelo" con 5 campos | EventType creado |
| 2 | Técnico navega a "Nuevo Evento" | Formulario renderizado con 5 campos |
| 3 | Técnico completa formulario | Validación en tiempo real |
| 4 | Técnico envía | Evento creado y visible |

## 5. Criterios de Aceptación

### 5.1 Cobertura de Código

```bash
pytest --cov=. --cov-report=html --cov-report=term
```

**Objetivo**: >70% cobertura total

| Módulo | Cobertura Mínima |
|--------|------------------|
| events/ | 80% |
| fields/ | 70% |
| variables/ | 70% |
| api/ | 75% |
| core/ | 60% |

### 5.2 Performance

| Métrica | SLA |
|---------|-----|
| Consulta simple | < 1s |
| Consulta compleja (trazabilidad) | < 2s |
| API p95 latency | < 500ms |
| Dashboard load | < 2s |

### 5.3 Calidad de Código

```bash
# Linting
flake8 .
pylint */

# Type checking
mypy .
```

**Sin errores críticos**

## 6. Entorno de Pruebas

### 6.1 Datos de Prueba

**Fixture de Datos**:
- 5 lotes
- 3 campañas
- 10 tipos de evento
- 100 eventos
- 1000 variables
- 5 usuarios (1 por rol)

**Comando**:
```bash
python manage.py load_test_data
```

### 6.2 Base de Datos de Prueba

```python
# settings_test.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'traceability_test',
        'USER': 'test',
        'PASSWORD': 'test',
        'HOST': 'localhost'
    }
}
```

## 7. Ejecución de Pruebas

### 7.1 Comandos

```bash
# Todas las pruebas
pytest

# Solo unitarias
pytest tests/unit/

# Solo API
pytest tests/api/

# Con cobertura
pytest --cov=. --cov-report=html

# Pruebas de carga
locust -f tests/load/locustfile.py --host=http://localhost:8000

# E2E
pytest tests/e2e/ --headed

# Seguridad
bandit -r . -ll
safety check
```

### 7.2 CI/CD (GitHub Actions)

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: traceability_test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-django pytest-cov
      
      - name: Run tests
        run: |
          pytest --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## 8. Reporte de Defectos

### 8.1 Severidad

| Nivel | Descripción | SLA Resolución |
|-------|-------------|----------------|
| **Crítico** | Sistema no funciona | 24 horas |
| **Alto** | Funcionalidad principal afectada | 3 días |
| **Medio** | Funcionalidad secundaria | 1 semana |
| **Bajo** | Cosmético | 2 semanas |

### 8.2 Template de Defecto

```markdown
**ID**: BUG-001
**Título**: No se puede crear evento sin campaña
**Severidad**: Alto
**Pasos para Reproducir**:
1. Login como técnico
2. Navegar a Nuevo Evento
3. Llenar formulario sin seleccionar campaña
4. Enviar

**Resultado Actual**: Error 500
**Resultado Esperado**: Validación clara o permitir null
**Evidencia**: screenshot.png
**Entorno**: Dev, Chrome 120
```

## 9. Registro de Pruebas

**Archivo**: `test_results.md`

| Fecha | Tipo | Total | Pasadas | Falladas | Cobertura |
|-------|------|-------|---------|----------|-----------|
| 2025-10-13 | Unit | 120 | 118 | 2 | 72% |
| 2025-10-14 | Integration | 45 | 45 | 0 | - |
| 2025-10-15 | E2E | 10 | 9 | 1 | - |

---

**Siguiente**: [Glosario →](./glosario.md)

[← Volver al índice](../README.md)
