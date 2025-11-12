# Gestión de Riesgos

[← Volver al índice](../README.md) | [← Cronograma](./08_cronograma.md) | [Plan de Pruebas →](./10_pruebas.md)

## 1. Introducción

Este documento identifica, analiza y propone estrategias de mitigación para los riesgos del proyecto de trazabilidad agrícola.

## 2. Matriz de Riesgos

### 2.1 Clasificación de Impacto

| Nivel | Descripción | Efecto |
|-------|-------------|--------|
| **Muy Alto** | Cancela el proyecto | Pérdida total |
| **Alto** | Retraso > 4 semanas | Objetivos no cumplidos |
| **Medio** | Retraso 1-4 semanas | Alcance reducido |
| **Bajo** | Retraso < 1 semana | Afectación mínima |

### 2.2 Clasificación de Probabilidad

| Nivel | Rango | Criterio |
|-------|-------|----------|
| **Muy Alta** | >70% | Casi seguro que ocurra |
| **Alta** | 40-70% | Probablemente ocurra |
| **Media** | 15-40% | Puede ocurrir |
| **Baja** | <15% | Poco probable |

## 3. Riesgos Identificados

### R01: Validación de Formularios Complejos

**Categoría**: Técnico  
**Probabilidad**: Media (40%)  
**Impacto**: Medio  
**Fase Crítica**: Semanas 4-7

**Descripción**: La validación de formularios basados en JSON Schema puede presentar desafíos. Riesgo de:
- Errores en la validación de campos complejos
- Problemas con validaciones en tiempo real
- Dificultades para mostrar mensajes de error claros
- Rendimiento de queries JSONB

**Indicadores de Riesgo**:
- ⚠️ Semana 5: Validación JSON Schema no funciona correctamente
- ⚠️ Semana 6: Formularios no muestran errores de validación claros
- ⚠️ Semana 7: Consultas JSONB lentas (>3s)

**Estrategias de Mitigación**:

| Acción | Tipo | Responsable | Cuándo |
|--------|------|-------------|--------|
| Prototipo técnico (spike) antes de Semana 4 | Prevención | Dev | Semana 3 |
| Consultar experto PostgreSQL/JSONB | Prevención | Dev | Semana 2 |
| Implementar índices GIN desde inicio | Prevención | Dev | Semana 5 |
| Tener plan B: EAV simplificado | Contingencia | Dev | Si falla Sem 6 |
| Revisión código semanal (peer review) | Detección | Dev + DBA | Semanal |

**Plan de Contingencia**:
Si falla validación compleja:
1. Simplificar a validación básica (tipos + required)
2. Validación avanzada en roadmap futuro
3. Foco en funcionalidad, no flexibilidad extrema

**Costo Contingencia**: +2 semanas

---

### R02: Falta de Validación con Usuarios Finales

**Categoría**: Negocio  
**Probabilidad**: Media (40%)  
**Impacto**: Alto

**Descripción**: Desarrollar funcionalidades que no satisfacen necesidades reales por falta de feedback continuo.

**Indicadores**:
- ⚠️ Usuario no comprende interfaz
- ⚠️ Eventos predefinidos no cubren casos reales
- ⚠️ Flujos no intuitivos

**Estrategias de Mitigación**:

| Acción | Tipo | Responsable | Cuándo |
|--------|------|-------------|--------|
| Sesiones de validación cada 2 semanas | Prevención | Dev + Stakeholder | Cada hito |
| Mockups/wireframes antes de implementar | Prevención | Dev | Antes UI |
| Piloto con 2-3 usuarios en Semana 10 | Detección | Stakeholder | Semana 10 |
| Recopilar feedback en prototipo funcional | Detección | Dev | Semana 7 |

**Plan de Contingencia**:
- Dedicar Semana 15 a ajustes UX si feedback negativo
- Priorizar funcionalidades críticas, posponer secundarias

**Costo**: +1 semana

---

### R03: Rendimiento Insuficiente de Consultas

**Categoría**: Técnico  
**Probabilidad**: Media (35%)  
**Impacto**: Medio

**Descripción**: Consultas de trazabilidad o reportes lentas (>5s) por:
- Falta de índices
- N+1 queries
- Volumen de datos mayor al esperado

**Indicadores**:
- ⚠️ Consulta trazabilidad 1 año >5s
- ⚠️ Dashboard tarda >3s en cargar

**Estrategias de Mitigación**:

| Acción | Tipo | Responsable | Cuándo |
|--------|------|-------------|--------|
| Índices desde inicio (field+timestamp) | Prevención | Dev | Semana 5 |
| Usar select_related/prefetch_related | Prevención | Dev | Siempre |
| Pruebas de carga con datos realistas | Detección | Dev | Semana 14 |
| Particionado de eventos por año | Contingencia | DBA | Si necesario |
| Caché de reportes frecuentes (Redis) | Contingencia | Dev | Si necesario |

**Plan de Contingencia**:
- Paginación más agresiva (20 items/página)
- Particionamiento de tabla events
- Implementar caché

**Costo**: +1 semana

---

### R04: Resistencia al Cambio del Personal

**Categoría**: Organizacional  
**Probabilidad**: Alta (50%)  
**Impacto**: Alto

**Descripción**: Personal técnico prefiere métodos manuales (cuadernos, Excel) y no adopta el sistema.

**Indicadores**:
- ⚠️ < 50% de eventos registrados en sistema
- ⚠️ Quejas sobre complejidad
- ⚠️ Captura retrasada (días después del evento)

**Estrategias de Mitigación**:

| Acción | Tipo | Responsable | Cuándo |
|--------|------|-------------|--------|
| Involucrar usuarios desde Semana 1 | Prevención | Stakeholder | Continuo |
| Capacitación práctica (no solo teoría) | Prevención | Dev | Semana 16 |
| Mostrar valor: reportes automáticos | Motivación | Stakeholder | Semana 13 |
| Gamificación: insignias por eventos | Motivación | Dev | Semana 15 |
| Hacer sistema MÁS fácil que Excel | Prevención | Dev | Diseño UX |

**Plan de Contingencia**:
- Migración gradual (50% eventos primeros 3 meses)
- Incentivos por uso (reconocimiento)
- Soporte intensivo primeros 2 meses

---

### R05: Falta de Conectividad en Campo

**Categoría**: Infraestructura  
**Probabilidad**: Alta (60%)  
**Impacto**: Medio

**Descripción**: Internet limitado en campo impide captura en tiempo real.

**Indicadores**:
- ⚠️ Usuarios reportan errores de conexión
- ⚠️ Eventos capturados horas/días después

**Estrategias de Mitigación**:

| Acción | Tipo | Responsable | Cuándo |
|--------|------|-------------|--------|
| Captura desde oficina (aceptable v1.0) | Aceptación | - | - |
| Interfaz ligera (pocos requests) | Prevención | Dev | Diseño |
| Modo offline en roadmap v2.0 | Contingencia | - | Post MVP |

**Plan de Contingencia**:
- Aceptar captura diferida (dentro de 24h)
- No es bloqueante para v1.0

---

### R06: Pérdida de Datos

**Categoría**: Técnico  
**Probabilidad**: Baja (10%)  
**Impacto**: Muy Alto

**Descripción**: Falla de hardware, error humano o bug elimina datos.

**Indicadores**:
- 🔥 Corrupción de BD
- 🔥 Eliminación accidental de lote con eventos

**Estrategias de Mitigación**:

| Acción | Tipo | Responsable | Cuándo |
|--------|------|-------------|--------|
| Backups diarios automáticos | Prevención | DBA/Dev | Desde Semana 1 |
| Soft delete (is_active=False) | Prevención | Dev | Diseño |
| Retención backups 30 días | Prevención | DBA | Configuración |
| Tests de restauración mensual | Detección | DBA | Mensual |
| Auditoría completa (rastrear cambios) | Detección | Dev | Semana 3 |

**Plan de Contingencia**:
- Restaurar desde backup último día
- Recuperar desde auditoría si disponible

**Costo**: RTO 4h, RPO 24h

---

### R07: Falta de Documentación

**Categoría**: Proceso  
**Probabilidad**: Media (30%)  
**Impacto**: Medio

**Descripción**: Documentación técnica insuficiente dificulta mantenimiento futuro.

**Indicadores**:
- ⚠️ Código sin comentarios
- ⚠️ API sin docs
- ⚠️ No hay guía de despliegue

**Estrategias de Mitigación**:

| Acción | Tipo | Responsable | Cuándo |
|--------|------|-------------|--------|
| Documentar en paralelo al desarrollo | Prevención | Dev | Continuo |
| Swagger auto-generado | Prevención | Dev | Semana 12 |
| README.md desde Semana 1 | Prevención | Dev | Semana 1 |
| Docstrings en funciones críticas | Prevención | Dev | Siempre |
| Dedicar Semana 16 a docs | Detección | Dev | Semana 16 |

**Plan de Contingencia**:
- Sprint de documentación post-entrega
- Knowledge transfer session

---

### R08: Cambios de Alcance (Scope Creep)

**Categoría**: Negocio  
**Probabilidad**: Alta (55%)  
**Impacto**: Alto

**Descripción**: Stakeholder solicita funcionalidades adicionales no planeadas.

**Indicadores**:
- ⚠️ "¿Podríamos agregar...?"
- ⚠️ Solicitudes frecuentes de cambios

**Estrategias de Mitigación**:

| Acción | Tipo | Responsable | Cuándo |
|--------|------|-------------|--------|
| Documento alcance firmado | Prevención | Dev + Stakeholder | Semana 1 |
| Backlog priorizado (MoSCoW) | Prevención | Dev | Semana 1 |
| Change request formal | Prevención | Dev | Cuando ocurra |
| Roadmap v2.0 para "nice to have" | Aceptación | Dev | Continuo |

**Plan de Contingencia**:
- Negociar: nueva feature = posponer otra
- Foco en MVP funcional

---

### R09: Dependencias de Terceros

**Categoría**: Técnico  
**Probabilidad**: Baja (15%)  
**Impacto**: Medio

**Descripción**: Librería crítica (Django, DRF, jsonschema) tiene bug o cambia API.

**Indicadores**:
- 🔥 Breaking change en actualización
- 🔥 Bug crítico en librería

**Estrategias de Mitigación**:

| Acción | Tipo | Responsable | Cuándo |
|--------|------|-------------|--------|
| Versiones fijas en requirements.txt | Prevención | Dev | Semana 1 |
| No actualizar en medio del proyecto | Prevención | Dev | - |
| Tests de regresión | Detección | Dev | Continuo |

**Plan de Contingencia**:
- Rollback a versión anterior
- Fork de librería si necesario (extremo)

---

### R10: Falta de Tiempo

**Categoría**: Gestión  
**Probabilidad**: Media (35%)  
**Impacto**: Alto

**Descripción**: Subestimación de esfuerzo lleva a no completar a tiempo.

**Indicadores**:
- ⚠️ Retraso >1 semana en hito
- ⚠️ Burnout del equipo

**Estrategias de Mitigación**:

| Acción | Tipo | Responsable | Cuándo |
|--------|------|-------------|--------|
| Buffer de 10% en estimaciones | Prevención | Dev | Planificación |
| Revisión semanal de avance | Detección | Dev | Semanal |
| Priorizar MoSCoW (Must/Should/Could) | Contingencia | Dev | Continuo |
| Reducir alcance si necesario | Contingencia | Dev + Stakeholder | Semana 12 |

**Plan de Contingencia**:
- Eliminar funcionalidades "Could have"
- Extender a 18 semanas (negociar)

---

## 4. Matriz de Riesgos (Resumen)

| ID | Riesgo | Prob. | Impacto | Severidad | Estado |
|----|--------|-------|---------|-----------|--------|
| R01 | Validación de formularios complejos | Media | Medio | **Medio** | Activo |
| R02 | Falta validación usuarios | Media | Alto | **Alto** | Activo |
| R03 | Rendimiento | Media | Medio | Medio | Activo |
| R04 | Resistencia al cambio | Alta | Alto | **Crítico** | Activo |
| R05 | Falta conectividad | Alta | Medio | Medio | Aceptado |
| R06 | Pérdida de datos | Baja | Muy Alto | **Alto** | Mitigado |
| R07 | Falta documentación | Media | Medio | Medio | Activo |
| R08 | Scope creep | Alta | Alto | **Crítico** | Activo |
| R09 | Dependencias terceros | Baja | Medio | Bajo | Monitoreo |
| R10 | Falta de tiempo | Media | Alto | **Alto** | Activo |

## 5. Plan de Monitoreo

**Frecuencia**: Revisión semanal de riesgos

**Responsable**: Líder del proyecto

**Acciones**:
1. Revisar indicadores de cada riesgo
2. Actualizar probabilidad/impacto
3. Activar planes de contingencia si necesario
4. Comunicar a stakeholders riesgos críticos

## 6. Reserva de Contingencia

**Tiempo**: +3 semanas (buffer)  
**Presupuesto**: 10% adicional para imprevistos  
**Uso**: Solo para riesgos R01, R04, R08 (críticos)

---

**Siguiente**: [Plan de Pruebas →](./10_pruebas.md)

[← Volver al índice](../README.md)
