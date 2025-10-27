# Plan de Desarrollo - Cronograma de 16 Semanas

[← Volver al índice](../README.md) | [← Eventos Dinámicos](./07_eventos_dinamicos.md) | [Riesgos →](./09_riesgos.md)

## 1. Resumen Ejecutivo

**Duración Total**: 16 semanas (4 meses)  
**Metodología**: Desarrollo iterativo incremental con entregas cada 2 semanas  
**Equipo**: 1-2 desarrolladores + 1 stakeholder (validación)

## 2. Fases del Proyecto

```
┌─────────────────────────────────────────────────────────────┐
│ Fase 1: Fundación (Semanas 1-3)                             │
│ - Setup proyecto                                             │
│ - Modelos base                                               │
│ - Autenticación y roles                                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Fase 2: Núcleo - Eventos Dinámicos (Semanas 4-7)           │
│ - EventType + validación JSON Schema                        │
│ - Event CRUD                                                 │
│ - Formularios dinámicos                                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Fase 3: Variables y Consultas (Semanas 8-10)               │
│ - Variables ambientales                                      │
│ - Trazabilidad por lote                                      │
│ - Adjuntos                                                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Fase 4: API y Reportes (Semanas 11-13)                     │
│ - API REST completa                                          │
│ - KPIs y reportes                                            │
│ - Exportaciones                                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Fase 5: Integración y Pruebas (Semanas 14-16)              │
│ - Pruebas integrales                                         │
│ - Optimizaciones                                             │
│ - Documentación                                              │
│ - Despliegue                                                 │
└─────────────────────────────────────────────────────────────┘
```

## 3. Cronograma Detallado

### **Semana 1: Configuración Inicial**

**Objetivos**: Establecer base del proyecto

| Tarea | Esfuerzo | Responsable | Entregable |
|-------|----------|-------------|------------|
| Setup Django 5 + Docker | 4h | Dev | Proyecto inicializado con Docker Compose |
| Configurar estructura de apps | 4h | Dev | Apps core, fields, events, variables, api |
| Configurar Git + .gitignore | 2h | Dev | Repositorio configurado |
| Dockerfile + docker-compose.yml | 3h | Dev | Containerización completa |
| Configurar PostgreSQL + extensiones | 3h | Dev | BD en contenedor con JSONB |
| Configurar Django settings (dev/prod) | 4h | Dev | settings.py modular |

**Entregables**: Proyecto Django funcional con BD conectada

---

### **Semana 2: Modelos Base y Autenticación**

**Objetivos**: Modelos fundamentales y sistema de usuarios

| Tarea | Esfuerzo | Responsable | Entregable |
|-------|----------|-------------|------------|
| Modelo Field (Lote) | 4h | Dev | Modelo + migración |
| Modelo Campaign | 3h | Dev | Modelo + migración |
| Modelo Station | 3h | Dev | Modelo + migración |
| Extender User con roles (RBAC) | 5h | Dev | UserProfile + permisos |
| Implementar autenticación JWT | 5h | Dev | Login API |
| Django Admin para catálogos | 4h | Dev | Admin personalizado |

**Entregables**: Modelos base funcionales + autenticación

---

### **Semana 3: Auditoría y UI Base**

**Objetivos**: Sistema de auditoría y templates base

| Tarea | Esfuerzo | Responsable | Entregable |
|-------|----------|-------------|------------|
| Modelo AuditLog | 3h | Dev | Modelo + migración |
| Middleware de auditoría | 5h | Dev | Middleware funcional |
| Templates base (base.html) | 4h | Dev | Layout responsive |
| Dashboard inicial (vacío) | 4h | Dev | Vista dashboard |
| Configurar HTMX/Alpine.js | 3h | Dev | Assets configurados |
| Testing básico (pytest setup) | 5h | Dev | Tests unitarios básicos |

**Entregables**: Sistema de auditoría + UI base

**🎯 Hito 1**: Fundación completa (Fin Semana 3)

---

### **Semana 4: EventType - Definición**

**Objetivos**: Modelo y validación de tipos de evento

| Tarea | Esfuerzo | Responsable | Entregable |
|-------|----------|-------------|------------|
| Modelo EventType | 4h | Dev | Modelo + migración |
| Validación JSON Schema | 6h | Dev | Validador funcional |
| Servicio EventTypeService | 4h | Dev | Lógica de negocio |
| CRUD EventType en Admin | 4h | Dev | Admin personalizado |
| Tests validación schema | 6h | Dev | Suite de tests |

**Entregables**: EventType funcional con validación

---

### **Semana 5: Event - Instancias**

**Objetivos**: Modelo de eventos y captura básica

| Tarea | Esfuerzo | Responsable | Entregable |
|-------|----------|-------------|------------|
| Modelo Event | 4h | Dev | Modelo + migración |
| Índices JSONB optimizados | 3h | Dev | Índices creados |
| Servicio EventService.create_event() | 6h | Dev | Lógica completa |
| Vista web para crear evento | 6h | Dev | Formulario básico |
| Integración auditoría en eventos | 3h | Dev | Auditoría funcional |
| Tests eventos | 6h | Dev | Tests unitarios |

**Entregables**: Creación de eventos básica

---

### **Semana 6: Formularios Dinámicos**

**Objetivos**: Renderizado dinámico de formularios

| Tarea | Esfuerzo | Responsable | Entregable |
|-------|----------|-------------|------------|
| DynamicFormRenderer | 8h | Dev | Generador de forms |
| Template event_form.html | 6h | Dev | Form renderizado |
| JavaScript para tipos especiales | 6h | Dev | Date picker, select, etc. |
| Previsualización de formulario | 4h | Dev | Preview en EventType |
| Tests formularios dinámicos | 6h | Dev | Tests E2E |

**Entregables**: Formularios 100% dinámicos

---

### **Semana 7: Eventos Base Predefinidos**

**Objetivos**: Cargar esquemas base

| Tarea | Esfuerzo | Responsable | Entregable |
|-------|----------|-------------|------------|
| Fixture riego | 2h | Dev | Schema JSON |
| Fixture fertilización | 2h | Dev | Schema JSON |
| Fixture fitosanitarios | 2h | Dev | Schema JSON |
| Fixture cosecha | 2h | Dev | Schema JSON |
| Fixtures otros 5 eventos | 4h | Dev | Schemas JSON |
| Command Django para cargar fixtures | 3h | Dev | manage.py load_event_types |
| Documentar esquemas | 3h | Dev | Documentación schemas |
| Validación con usuarios | 6h | Stakeholder | Feedback |

**Entregables**: 9 eventos base cargados

**🎯 Hito 2**: Sistema de Eventos Dinámicos completo (Fin Semana 7)

---

### **Semana 8: Variables Ambientales**

**Objetivos**: Gestión de variables

| Tarea | Esfuerzo | Responsable | Entregable |
|-------|----------|-------------|------------|
| Modelo Variable | 4h | Dev | Modelo + migración |
| Índices para time-series | 3h | Dev | Índices optimizados |
| API ingesta variables | 6h | Dev | POST /variables/ |
| API bulk ingesta (IoT) | 5h | Dev | POST /variables/bulk/ |
| Vista web registro manual | 5h | Dev | Formulario variables |
| Tests variables | 5h | Dev | Tests unitarios |

**Entregables**: Sistema de variables funcional

---

### **Semana 9: Consulta de Trazabilidad**

**Objetivos**: Visualización de historial

| Tarea | Esfuerzo | Responsable | Entregable |
|-------|----------|-------------|------------|
| Vista trazabilidad por lote | 8h | Dev | Línea de tiempo |
| Filtros avanzados | 5h | Dev | Filtros fecha/tipo |
| Paginación optimizada | 3h | Dev | Pagination |
| Detalle de evento | 4h | Dev | Modal/página detalle |
| Exportación CSV básica | 4h | Dev | Export funcional |
| Tests trazabilidad | 6h | Dev | Tests E2E |

**Entregables**: Consulta de trazabilidad completa

---

### **Semana 10: Adjuntos**

**Objetivos**: Gestión de archivos

| Tarea | Esfuerzo | Responsable | Entregable |
|-------|----------|-------------|------------|
| Modelo Attachment | 3h | Dev | Modelo + migración |
| Subida de archivos | 6h | Dev | Upload funcional |
| Validación tipo/tamaño | 3h | Dev | Validadores |
| Previsualización imágenes | 4h | Dev | Thumbnails |
| Descarga segura | 3h | Dev | URLs firmadas |
| Storage configuración | 3h | Dev | Local + S3 ready |
| Tests adjuntos | 5h | Dev | Tests |

**Entregables**: Sistema de adjuntos completo

**🎯 Hito 3**: Variables y Consultas funcionales (Fin Semana 10)

---

### **Semana 11: API REST - Parte 1**

**Objetivos**: API de catálogos y eventos

| Tarea | Esfuerzo | Responsable | Entregable |
|-------|----------|-------------|------------|
| DRF Serializers (Field, Campaign, etc.) | 5h | Dev | Serializers |
| API Fields CRUD | 4h | Dev | /api/v1/fields/ |
| API Campaigns CRUD | 3h | Dev | /api/v1/campaigns/ |
| API EventTypes (read-only) | 3h | Dev | /api/v1/event-types/ |
| API Events CRUD | 6h | Dev | /api/v1/events/ |
| Filtros y paginación DRF | 4h | Dev | Filtros funcionales |
| Tests API básicos | 5h | Dev | Tests API |

**Entregables**: API catálogos y eventos

---

### **Semana 12: API REST - Parte 2**

**Objetivos**: API variables y docs

| Tarea | Esfuerzo | Responsable | Entregable |
|-------|----------|-------------|------------|
| API Variables | 5h | Dev | /api/v1/variables/ |
| API Attachments | 4h | Dev | /api/v1/attachments/ |
| Rate limiting (throttling) | 4h | Dev | 100 req/min |
| Swagger/OpenAPI docs | 5h | Dev | Docs interactivas |
| CORS configuración | 2h | Dev | CORS headers |
| API versioning | 3h | Dev | /api/v1/, /api/v2/ |
| Tests API completos | 7h | Dev | Tests E2E API |

**Entregables**: API completa documentada

---

### **Semana 13: Reportes y KPIs**

**Objetivos**: Reportes y analítica

| Tarea | Esfuerzo | Responsable | Entregable |
|-------|----------|-------------|------------|
| KPI: Eficiencia de riego | 5h | Dev | Cálculo + vista |
| KPI: Impacto nutricional | 5h | Dev | Correlación NDRE |
| Dashboard con gráficos | 8h | Dev | Charts.js integrado |
| Reporte trazabilidad completo | 5h | Dev | Reporte detallado |
| Exportación Excel | 4h | Dev | openpyxl |
| Exportación PDF (opcional) | 3h | Dev | ReportLab |

**Entregables**: Reportes y KPIs funcionales

**🎯 Hito 4**: API y Reportes completos (Fin Semana 13)

---

### **Semana 14: Pruebas Integrales**

**Objetivos**: Testing exhaustivo

| Tarea | Esfuerzo | Responsable | Entregable |
|-------|----------|-------------|------------|
| Pruebas unitarias faltantes | 8h | Dev | Cobertura >70% |
| Pruebas de integración | 8h | Dev | Suite integración |
| Pruebas E2E (Selenium/Playwright) | 8h | Dev | Tests E2E |
| Pruebas de carga (Locust) | 6h | Dev | Load tests |

**Entregables**: Suite de pruebas completa

---

### **Semana 15: Optimización y Seguridad**

**Objetivos**: Performance y hardening

| Tarea | Esfuerzo | Responsable | Entregable |
|-------|----------|-------------|------------|
| Optimización queries (N+1) | 6h | Dev | select_related/prefetch |
| Particionamiento BD (opcional) | 6h | Dev | Particiones |
| Auditoría seguridad (OWASP) | 6h | Dev | Checklist cumplido |
| Configurar HTTPS | 3h | Dev | Certificado SSL |
| Configurar Gunicorn + Nginx | 6h | Dev | Deploy config |
| Backup automatizado | 3h | Dev | Script backup |

**Entregables**: Sistema optimizado y seguro

---

### **Semana 16: Documentación y Despliegue**

**Objetivos**: Entrega final

| Tarea | Esfuerzo | Responsable | Entregable |
|-------|----------|-------------|------------|
| Documentación de usuario | 8h | Dev | Manual usuario |
| Documentación técnica | 6h | Dev | README, deployment |
| Guía de despliegue | 4h | Dev | Docs despliegue |
| Capacitación usuarios | 6h | Dev + Stakeholder | Sesión capacitación |
| Despliegue en producción | 6h | Dev | Sistema en prod |

**Entregables**: Sistema desplegado y documentado

**🎯 Hito 5**: Entrega Final (Fin Semana 16)

---

## 4. Distribución de Esfuerzo

| Fase | Semanas | Esfuerzo (horas) | % Total |
|------|---------|------------------|---------|
| Fundación | 1-3 | 120h | 19% |
| Eventos Dinámicos | 4-7 | 160h | 25% |
| Variables y Consultas | 8-10 | 120h | 19% |
| API y Reportes | 11-13 | 120h | 19% |
| Pruebas y Despliegue | 14-16 | 120h | 19% |
| **Total** | **16** | **640h** | **100%** |

**Estimación**: ~40 horas/semana (tiempo completo)

## 5. Dependencias Críticas

```
Semana 1 ──→ Semana 2 ──→ Semana 3
                         ↓
                    Semana 4 ──→ Semana 5 ──→ Semana 6 ──→ Semana 7
                                                            ↓
                                                    Semana 8 ──→ Semana 9
                                                            ↓
                                                    Semana 10
                                                            ↓
                                            Semana 11 ──→ Semana 12 ──→ Semana 13
                                                                        ↓
                                                    Semana 14 ──→ Semana 15 ──→ Semana 16
```

**Ruta Crítica**: Semanas 1-7 (eventos dinámicos) son críticas. Retrasos aquí afectan todo.

## 6. Recursos Necesarios

### 6.1 Humanos

- **1 Desarrollador Full-Stack** (Django + Frontend)
- **1 Stakeholder/SME** (validación funcional)
- **1 DBA** (opcional, consultoría PostgreSQL)

### 6.2 Infraestructura

- **Desarrollo**: Laptop con 16GB RAM, Docker Desktop
- **Staging**: Docker Compose en VPS/VM (2GB RAM, 2 vCPU)
- **Producción**: Docker Compose en servidor Linux (4GB RAM, 2 vCPU)

### 6.3 Software

- Python 3.11+
- Django 5.0
- PostgreSQL 15+
- Docker + Docker Compose
- Git
- IDE (VS Code/PyCharm)

## 7. Riesgos y Mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Complejidad eventos dinámicos | Alta | Alto | Prototipar temprano (Semana 4) |
| Falta de validación usuario | Media | Alto | Revisiones cada 2 semanas |
| Problemas de rendimiento | Media | Medio | Pruebas de carga Semana 14 |
| Retrasos en dependencias | Baja | Alto | Buffer de 1 semana |

## 8. Entregables por Hito

| Hito | Semana | Entregables |
|------|--------|-------------|
| **Hito 1** | 3 | Proyecto base + modelos + auth |
| **Hito 2** | 7 | Sistema eventos dinámicos funcional |
| **Hito 3** | 10 | Variables + trazabilidad + adjuntos |
| **Hito 4** | 13 | API completa + reportes |
| **Hito 5** | 16 | Sistema en producción |

## 9. Criterios de Aceptación Final

- ✅ Todos los RF (1-15) implementados
- ✅ Cobertura de pruebas > 70%
- ✅ API documentada (Swagger)
- ✅ Performance: consultas < 2s
- ✅ Sistema desplegado en producción
- ✅ Usuarios capacitados
- ✅ Documentación completa

---

**Siguiente**: [Gestión de Riesgos →](./09_riesgos.md)

[← Volver al índice](../README.md)
