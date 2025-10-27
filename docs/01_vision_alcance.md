# Visión y Alcance del Sistema

[← Volver al índice](../README.md)

## 1. Introducción

### 1.1 Propósito del Documento

Este documento establece la visión, objetivos y alcance del Sistema de Trazabilidad Agrícola para cultivo de limón. Define qué problemas resuelve el sistema, quiénes serán sus usuarios y qué beneficios aportará a la organización.

> **Nota importante**: Este sistema está diseñado como un **MVP (Minimum Viable Product)**, buscando ser lo más simple posible, minimizando la lógica y complejidad, priorizando la implementación rápida y sencilla. La única lógica compleja que se mantiene es la de creación dinámica de eventos, que es fundamental para la flexibilidad del sistema.

### 1.2 Audiencia

- Equipo de desarrollo
- Stakeholders del proyecto
- Administradores del centro de cultivo
- Personal técnico y agronómico

## 2. Visión del Producto


> **Enfoque MVP**: El sistema busca la máxima simplicidad en su diseño, priorizando la implementación rápida y la facilidad de uso. Se minimiza la complejidad de la lógica de negocio, exceptuando el sistema de eventos dinámicos que es fundamental para la flexibilidad del mismo.

### 2.2 Propuesta de Valor

El sistema proporcionará:

1. **Trazabilidad Completa**: Seguimiento del historial completo de cada lote desde la preparación del terreno hasta la comercialización
2. **Flexibilidad**: Capacidad de adaptar el sistema a nuevos tipos de eventos sin modificar código fuente
3. **Accesibilidad**: Información disponible desde cualquier lugar a través de web y API
4. **Toma de Decisiones**: KPIs y reportes que facilitan la optimización de recursos
5. **Cumplimiento**: Auditoría completa para certificaciones y normativas

## 3. Problema que Resuelve

### 3.1 Situación Actual

Los centros de cultivo de limón enfrentan varios desafíos:

- **Registro Manual Disperso**: Información en cuadernos, hojas de cálculo y formatos inconsistentes
- **Falta de Trazabilidad**: Dificultad para rastrear el historial de actividades por lote
- **Datos No Estructurados**: Información difícil de analizar y correlacionar
- **Pérdida de Información**: Registros extraviados o incompletos
- **Duplicación de Esfuerzos**: Captura repetida de la misma información
- **Dificultad en Auditorías**: Problemas para demostrar cumplimiento de prácticas agrícolas

### 3.2 Impacto del Problema

- Pérdida de certificaciones de calidad
- Decisiones agronómicas sub-óptimas
- Desperdicio de recursos (agua, fertilizantes, mano de obra)
- Imposibilidad de identificar causas de problemas en el cultivo
- Baja productividad administrativa

## 4. Alcance del Sistema

### 4.1 Dentro del Alcance (v1.0)

#### Módulos Principales

1. **Gestión de Infraestructura Agrícola**
   - Registro de lotes/parcelas con georreferenciación
   - Gestión de campañas/temporadas
   - Estaciones de monitoreo (clima/IoT)

2. **Sistema de Eventos de Trazabilidad**
   - Eventos base predefinidos (9 categorías principales)
   - Creación dinámica de nuevos tipos de eventos
   - Captura de instancias de eventos con campos personalizables
   - Adjuntos (fotos, documentos, etiquetas)

3. **Gestión de Variables Ambientales**
   - Registro manual y automático (IoT)
   - Variables de suelo, clima e índices de vegetación
   - Correlación básica con eventos

4. **Consultas y Reportes**
   - Línea de tiempo de eventos por lote
   - Filtros avanzados (fecha, tipo, responsable, campaña)
   - KPIs básicos (eficiencia de riego, correlación nutricional)
   - Exportación a CSV/Excel

5. **API REST**
   - Autenticación JWT
   - CRUD de catálogos
   - Lectura/escritura de eventos y variables
   - Documentación OpenAPI/Swagger

6. **Seguridad y Auditoría**
   - Control de acceso basado en roles (RBAC)
   - Registro de todas las operaciones
   - Histórico de cambios

#### Eventos Base Incluidos

1. **Riego**: Método, duración, volumen, presión, CE, pH
2. **Fertilización**: Productos, dosis, método de aplicación, análisis foliar
3. **Fitosanitarios**: Productos, dosis, plagas/enfermedades objetivo, método
4. **Labores Culturales**: Poda, deshierbe, aclareo de frutos
5. **Monitoreo de Plagas/Enfermedades**: Detección, severidad, ubicación
6. **Brotes**: Incidencias significativas
7. **Clima**: Registro de condiciones meteorológicas
8. **Cosecha**: Rendimiento, calidad, cuadrillas
9. **Poscosecha**: Almacenamiento, procesamiento

#### Variables Prioritarias

- **Suelo**: Humedad, temperatura, CE, pH
- **Clima**: Temperatura, humedad relativa, precipitación, viento
- **Vegetación**: NDVI, NDRE

### 4.2 Fuera del Alcance (v1.0)

- Análisis predictivo avanzado con ML/IA
- Módulo de contabilidad completo
- Gestión de inventario de productos
- Sistema de alertas en tiempo real vía SMS/WhatsApp
- Integración directa con sistemas ERP externos
- Aplicación móvil nativa (iOS/Android)
- Mapeo detallado con drones
- Control automático de sistemas de riego

### 4.3 Alcance Futuro (Post v1.0)

- **v1.1**: Módulo de alertas automáticas
- **v1.2**: Dashboard de analítica avanzada
- **v2.0**: Aplicación móvil nativa
- **v2.1**: Integración con sistemas de IoT comerciales
- **v2.2**: Sistema de recomendaciones basado en IA

## 5. Usuarios y Stakeholders

### 5.1 Usuarios Directos

| Rol | Responsabilidades | Frecuencia de Uso |
|-----|-------------------|-------------------|
| **Administrador de Sistema** | Configuración, gestión de usuarios, definición de tipos de evento | Ocasional |
| **Ingeniero Agrónomo / Supervisor** | Planificación, análisis, generación de reportes | Diario |
| **Técnico de Campo** | Captura de eventos, registro de observaciones | Diario/Múltiple veces |
| **Responsable de Calidad** | Auditoría, consulta de trazabilidad, reportes de certificación | Semanal |
| **Operador de Cosecha** | Registro de rendimientos y calidad | Temporal (época de cosecha) |

### 5.2 Stakeholders

- **Gerencia**: Información para toma de decisiones estratégicas
- **Entidades Certificadoras**: Acceso a registros de trazabilidad
- **Sistemas Externos**: Consumo de datos vía API

## 6. Restricciones

### 6.1 Restricciones Técnicas

- Desarrollo en Python 3.11+ con Django 5.x
- Base de datos PostgreSQL
- Despliegue en infraestructura existente (servidor Linux)
- Compatibilidad con navegadores modernos (últimas 2 versiones)

### 6.2 Restricciones de Negocio

- Presupuesto: Proyecto académico (sin licencias comerciales costosas)
- Tiempo: 16 semanas de desarrollo
- Personal: Equipo de desarrollo limitado

### 6.3 Restricciones Regulatorias

- Protección de datos personales (información de trabajadores)
- Cumplimiento con estándares de trazabilidad agrícola (GlobalGAP, orgánicos)

## 7. Supuestos y Dependencias

### 7.1 Supuestos

- Conectividad a internet disponible en las oficinas del centro de cultivo
- Personal técnico con conocimientos básicos de computación
- Infraestructura de servidor disponible para despliegue
- Dispositivos móviles/tablets disponibles para captura en campo (navegador web)

### 7.2 Dependencias

- Disponibilidad de personal del centro de cultivo para validación de requerimientos
- Acceso a datos históricos para migración inicial
- Coordinación con proveedores de sensores IoT (si aplica)

## 8. Criterios de Éxito

El proyecto será considerado exitoso si cumple:

1. ✅ **Funcionalidad**: Registro y consulta de al menos los 9 eventos base
2. ✅ **Flexibilidad**: Creación de al menos 2 eventos personalizados sin modificar código
3. ✅ **Usabilidad**: Tiempo de capacitación < 2 horas para usuarios técnicos
4. ✅ **Rendimiento**: Consultas de trazabilidad < 2 segundos
5. ✅ **Disponibilidad**: API funcional con documentación completa
6. ✅ **Adopción**: Al menos 80% del personal técnico usa el sistema activamente
7. ✅ **Calidad**: Cobertura de pruebas > 70%

## 9. Riesgos Iniciales

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Resistencia al cambio del personal | Media | Alto | Capacitación, demostrar valor temprano |
| Complejidad del sistema de eventos dinámicos | Alta | Alto | Prototipos tempranos, validación incremental |
| Falta de datos históricos | Media | Medio | Migración gradual, inicio desde temporada actual |
| Conectividad limitada en campo | Alta | Medio | Modo offline futuro, captura desde oficina |

---

**Siguiente**: [Análisis de Requerimientos →](./02_requerimientos.md)

[← Volver al índice](../README.md)
