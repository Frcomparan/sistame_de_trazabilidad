# Análisis de Requerimientos

[← Volver al índice](../README.md) | [← Visión y Alcance](./01_vision_alcance.md) | [Arquitectura →](./03_arquitectura.md)

## 1. Introducción

Este documento detalla los requerimientos funcionales y no funcionales del Sistema de Trazabilidad Agrícola, estableciendo qué debe hacer el sistema y las restricciones bajo las cuales debe operar.

## 2. Requerimientos Funcionales (RF)

### 2.1 Gestión de Catálogos Base

#### RF-01: Gestión de Lotes/Parcelas

**Prioridad**: Alta  
**Descripción**: El sistema debe permitir crear, modificar, consultar y eliminar lotes o parcelas.

**Criterios de Aceptación**:
- Registrar nombre, código único, superficie (ha)
- Registrar ubicación textual y coordenadas geográficas (opcional)
- Asociar geometría (polígono) opcional para visualización en mapa
- Marcar lotes como activos/inactivos
- Historial de modificaciones

**Datos**:
```
- Nombre: texto obligatorio
- Código: alfanumérico único
- Superficie: decimal (hectáreas)
- Ubicación: texto
- Latitud/Longitud: decimal opcional
- Geometría: GeoJSON opcional
- Estado: activo/inactivo
```

#### RF-02: Gestión de Campañas/Temporadas

**Prioridad**: Alta  
**Descripción**: Definir períodos de producción para organizar los eventos por temporada.

**Criterios de Aceptación**:
- Crear campañas con nombre, fecha inicio, fecha fin
- Asociar variedad de limón (ej. Persa, Limón Real)
- Vincular eventos a una campaña específica
- Generar reportes por campaña

**Datos**:
```
- Nombre: texto (ej. "2025 - Temporada Alta")
- Temporada: texto (Primavera/Verano/Otoño/Invierno)
- Variedad: catálogo (Limón Persa, Limón Real, etc.)
- Fecha inicio: date
- Fecha fin: date
```

#### RF-03: Gestión de Estaciones de Monitoreo

**Prioridad**: Media  
**Descripción**: Registrar puntos físicos de medición de variables ambientales.

**Criterios de Aceptación**:
- Crear estaciones con nombre y ubicación
- Asociar a un lote/parcela
- Registrar coordenadas GPS precisas
- Estado operativo (activa/inactiva/mantenimiento)

**Datos**:
```
- Nombre: texto
- Lote asociado: FK
- Latitud: decimal
- Longitud: decimal
- Tipo: clima/suelo/multivariable
- Estado: activo/inactivo/mantenimiento
```

### 2.2 Sistema de Eventos Dinámicos (Núcleo)

#### RF-04: Definición de Tipos de Evento

**Prioridad**: Crítica  
**Descripción**: Los administradores deben poder crear y configurar nuevos tipos de eventos sin modificar código.

**Criterios de Aceptación**:
- Crear tipo de evento con nombre, categoría y descripción
- Definir esquema de campos dinámicamente:
  - Nombre del campo
  - Tipo de dato (texto, número, decimal, fecha, fecha-hora, selección, booleano)
  - Obligatorio/opcional
  - Unidad de medida (cuando aplique)
  - Valores permitidos (para campos de selección)
  - Validaciones (rangos, expresiones regulares)
- Versionar el esquema (permitir evolución sin romper datos históricos)
- Activar/desactivar tipos de evento
- Previsualizar formulario antes de publicar

**Ejemplo de Esquema (JSON)**:
```json
{
  "type": "object",
  "properties": {
    "metodo": {
      "type": "string",
      "enum": ["goteo", "microaspersión", "gravedad"],
      "required": true
    },
    "duracion_min": {
      "type": "number",
      "minimum": 0,
      "required": true,
      "unit": "minutos"
    },
    "volumen_m3": {
      "type": "number",
      "minimum": 0,
      "required": false,
      "unit": "m³"
    },
    "presion_bar": {
      "type": "number",
      "minimum": 0,
      "maximum": 10,
      "required": false,
      "unit": "bar"
    }
  }
}
```

#### RF-05: Registro de Instancias de Eventos

**Prioridad**: Crítica  
**Descripción**: Capturar eventos reales que ocurren en campo según los tipos definidos.

**Criterios de Aceptación**:
- Seleccionar lote/parcela
- Seleccionar campaña
- Seleccionar tipo de evento
- Renderizar formulario dinámico según esquema del tipo
- Validar datos contra el esquema
- Registrar fecha/hora del evento
- Registrar usuario responsable
- Permitir observaciones adicionales (campo libre)
- Guardar en formato JSONB (PostgreSQL)

**Datos**:
```
- ID: UUID
- Tipo de evento: FK
- Lote: FK
- Campaña: FK
- Fecha/hora: timestamp con zona horaria
- Payload: JSONB (datos según esquema)
- Observaciones: texto opcional
- Usuario responsable: FK
- Fecha de captura: timestamp
```

#### RF-06: Adjuntar Evidencias a Eventos

**Prioridad**: Media  
**Descripción**: Permitir adjuntar archivos (fotos, PDFs, CSVs) a los eventos.

**Criterios de Aceptación**:
- Subir múltiples archivos por evento
- Tipos permitidos: JPG, PNG, PDF, CSV, XLS
- Tamaño máximo: 10 MB por archivo
- Almacenar metadata (nombre original, tamaño, tipo, fecha subida)
- Previsualización de imágenes
- Descarga de archivos adjuntos
- Control de acceso (solo usuarios autorizados)

### 2.3 Gestión de Variables Ambientales

#### RF-07: Registro de Variables

**Prioridad**: Alta  
**Descripción**: Capturar mediciones de sensores o registros manuales.

**Criterios de Aceptación**:
- Ingresar variable por estación o lote
- Tipos de variable: humedad suelo, temperatura aire, HR, precipitación, NDVI, NDRE, etc.
- Valor numérico con unidad
- Timestamp de la medición
- Origen: manual/automático (IoT)
- Validación de rangos razonables

**Datos**:
```
- ID: bigint
- Estación: FK opcional
- Lote: FK opcional
- Timestamp: timestamp con zona horaria
- Tipo variable: texto (código normalizado)
- Valor: decimal
- Unidad: texto
- Origen: manual/automático
```

#### RF-08: Ingesta de Variables vía API

**Prioridad**: Media  
**Descripción**: Recibir datos de dispositivos IoT automáticamente.

**Criterios de Aceptación**:
- Endpoint POST /api/v1/variables/bulk
- Autenticación por token de dispositivo
- Validación de payload JSON
- Inserción masiva eficiente
- Manejo de errores y reintentos

### 2.4 Consultas y Reportes

#### RF-09: Consulta de Trazabilidad por Lote

**Prioridad**: Crítica  
**Descripción**: Ver el historial completo de eventos de un lote en orden cronológico.

**Criterios de Aceptación**:
- Seleccionar lote
- Visualizar línea de tiempo de eventos
- Filtrar por:
  - Rango de fechas
  - Tipo de evento
  - Campaña
  - Responsable
- Ordenar por fecha ascendente/descendente
- Paginación (50 eventos por página)
- Exportar a CSV/Excel

#### RF-10: Dashboard de KPIs

**Prioridad**: Media  
**Descripción**: Visualizar indicadores clave de rendimiento.

**Criterios de Aceptación**:
- KPIs básicos:
  - Eficiencia de riego: Δ humedad / volumen aplicado
  - Correlación nutricional: Δ NDRE vs kg nutriente
  - Eventos de riego por semana
  - Incidencias de plagas/enfermedades
  - Rendimiento de cosecha (kg/ha)
- Filtrar por lote y campaña
- Gráficos básicos (barras, líneas)

#### RF-11: Reportes Personalizados

**Prioridad**: Baja  
**Descripción**: Generar reportes ad-hoc configurables.

**Criterios de Aceptación**:
- Seleccionar campos a incluir
- Aplicar filtros múltiples
- Agrupar por lote/campaña/tipo
- Exportar a CSV, Excel, PDF

### 2.5 API REST

#### RF-12: API de Consulta

**Prioridad**: Alta  
**Descripción**: Exponer datos para consumo externo.

**Criterios de Aceptación**:
- Endpoints REST estándar (GET, POST, PUT, DELETE)
- Autenticación JWT
- Recursos principales:
  - `/api/v1/fields/` (lotes)
  - `/api/v1/campaigns/` (campañas)
  - `/api/v1/event-types/` (tipos de evento)
  - `/api/v1/events/` (eventos)
  - `/api/v1/variables/` (variables)
  - `/api/v1/attachments/` (adjuntos)
- Filtros y paginación
- Rate limiting (100 req/min)
- Documentación OpenAPI/Swagger

#### RF-13: API de Escritura

**Prioridad**: Alta  
**Descripción**: Permitir inserción de datos desde sistemas externos.

**Criterios de Aceptación**:
- Validación estricta de payload
- Respuestas de error descriptivas (HTTP 400, 422)
- Idempotencia (para evitar duplicados)
- Logs de auditoría de escrituras API

### 2.6 Seguridad y Auditoría

#### RF-14: Control de Acceso Basado en Roles (RBAC)

**Prioridad**: Alta  
**Descripción**: Gestionar permisos según roles de usuario.

**Roles y Permisos**:

| Rol | Permisos |
|-----|----------|
| **Administrador** | Todo: CRUD catálogos, usuarios, tipos de evento |
| **Supervisor** | Lectura todo, escritura eventos, reportes |
| **Técnico Campo** | Lectura catálogos, escritura eventos y variables |
| **Consultor** | Solo lectura (reportes y consultas) |
| **Integración** | API: lectura/escritura eventos y variables |

#### RF-15: Auditoría de Operaciones

**Prioridad**: Alta  
**Descripción**: Registrar todas las acciones relevantes.

**Criterios de Aceptación**:
- Log de:
  - Creación/modificación/eliminación de eventos
  - Cambios en catálogos
  - Accesos a reportes
  - Llamadas API (con IP y token)
- Campos del log:
  - Usuario/token
  - Acción (CREATE/UPDATE/DELETE/READ)
  - Entidad afectada
  - Timestamp
  - Diff de cambios (antes/después)
- Retención de logs: 2 años
- Consulta de auditoría por administradores

## 3. Requerimientos No Funcionales (RNF)

### 3.1 Rendimiento

#### RNF-01: Tiempo de Respuesta

- Consultas simples: < 1 segundo
- Consultas complejas (reportes): < 5 segundos
- Carga de dashboard: < 2 segundos
- API: < 500 ms (p95)

#### RNF-02: Escalabilidad

- Soportar al menos 10,000 eventos/año
- Crecimiento anual proyectado: 20%
- Hasta 50 usuarios concurrentes
- API: 100 requests/minuto sostenido

#### RNF-03: Volumetría

- Eventos: 100,000 registros
- Variables: 1,000,000 registros (5 años)
- Adjuntos: 5 GB de almacenamiento

### 3.2 Usabilidad

#### RNF-04: Facilidad de Uso

- Interfaz intuitiva, sin requerir manual extenso
- Capacitación < 2 horas para usuarios básicos
- Mensajes de error claros y en español
- Diseño responsivo (móvil, tablet, desktop)

#### RNF-05: Accesibilidad

- Compatibilidad WCAG 2.1 nivel AA (deseable)
- Soporte de lectores de pantalla en formularios principales
- Contraste de colores adecuado

### 3.3 Seguridad

#### RNF-06: Autenticación y Autorización

- Autenticación por usuario/contraseña
- Contraseñas hasheadas (bcrypt/argon2)
- JWT con expiración (1 hora) y refresh tokens
- Sesiones web con CSRF protection

#### RNF-07: Protección de Datos

- Transmisión HTTPS obligatoria
- Cifrado de datos sensibles en BD (opcional)
- Sanitización de inputs (prevención SQL injection, XSS)
- Rate limiting en API

#### RNF-08: Backup y Recuperación

- Backup diario automático de BD
- Retención: 30 días
- Tiempo de recuperación objetivo (RTO): < 4 horas
- Punto de recuperación objetivo (RPO): < 24 horas

### 3.4 Mantenibilidad

#### RNF-09: Código y Documentación

- Código Python siguiendo PEP 8
- Cobertura de pruebas: > 70%
- Documentación de API (Swagger)
- README y documentación de despliegue

#### RNF-10: Versionado

- Control de versiones con Git
- Conventional Commits
- Semantic Versioning (vX.Y.Z)

### 3.5 Portabilidad

#### RNF-11: Compatibilidad

- Navegadores: Chrome, Firefox, Safari, Edge (últimas 2 versiones)
- Servidor: Linux (Ubuntu 22.04 LTS recomendado)
- Base de datos: PostgreSQL 15+

#### RNF-12: Despliegue

- Dockerizado (deseable)
- Variables de entorno para configuración
- Script de despliegue automatizado
- Migraciones de BD gestionadas (Django migrations)

### 3.6 Observabilidad

#### RNF-13: Logs y Monitoreo

- Logs estructurados (JSON)
- Niveles: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Rotación de logs diaria
- Métricas básicas: requests/segundo, errores, latencia

### 3.7 Disponibilidad

#### RNF-14: Uptime

- Disponibilidad objetivo: 99% (permite ~7h downtime/mes)
- Mantenimientos programados fuera de horario laboral
- Ventana de mantenimiento: domingos 2:00-6:00 AM

### 3.8 Cumplimiento

#### RNF-15: Normativas

- Protección de datos personales (información de trabajadores)
- Zona horaria consistente: America/Mexico_City
- Formatos de fecha ISO 8601

## 4. Matriz de Trazabilidad

| ID Requerimiento | Prioridad | Módulo Afectado | Sprint |
|------------------|-----------|-----------------|--------|
| RF-01 | Alta | Catálogos | 1 |
| RF-02 | Alta | Catálogos | 1 |
| RF-03 | Media | Catálogos | 2 |
| RF-04 | Crítica | Eventos Dinámicos | 2-3 |
| RF-05 | Crítica | Eventos Dinámicos | 3-4 |
| RF-06 | Media | Eventos Dinámicos | 5 |
| RF-07 | Alta | Variables | 4 |
| RF-08 | Media | Variables | 6 |
| RF-09 | Crítica | Consultas | 5 |
| RF-10 | Media | Reportes | 7 |
| RF-11 | Baja | Reportes | 8 |
| RF-12 | Alta | API | 3-6 |
| RF-13 | Alta | API | 3-6 |
| RF-14 | Alta | Seguridad | 1 |
| RF-15 | Alta | Auditoría | 2 |

## 5. Casos de Uso Principales

### CU-01: Registrar Evento de Riego

**Actor**: Técnico de Campo  
**Flujo Principal**:
1. Usuario inicia sesión
2. Selecciona "Nuevo Evento"
3. Selecciona Lote "Parcela 5A"
4. Selecciona Campaña "2025 - Temporada Alta"
5. Selecciona Tipo "Riego"
6. Sistema renderiza formulario con campos: método, duración, volumen, presión, CE, pH
7. Usuario completa: goteo, 90 min, 45 m³, 1.8 bar, 850 µS/cm, 6.7
8. Opcionalmente adjunta foto del medidor
9. Usuario guarda
10. Sistema valida, registra evento y muestra confirmación

### CU-02: Consultar Trazabilidad

**Actor**: Supervisor  
**Flujo Principal**:
1. Usuario selecciona "Consultar Trazabilidad"
2. Selecciona Lote "Parcela 5A"
3. Define rango: 01/01/2025 - 31/03/2025
4. Opcionalmente filtra por tipo: "Riego"
5. Sistema muestra línea de tiempo con eventos
6. Usuario expande evento para ver detalles
7. Usuario exporta a Excel

### CU-03: Crear Tipo de Evento Personalizado

**Actor**: Administrador  
**Flujo Principal**:
1. Administrador accede a "Gestión de Tipos de Evento"
2. Crea nuevo tipo "Análisis de Suelo"
3. Define campos:
   - pH (número, requerido, rango 4-9)
   - Materia Orgánica (número, %, requerido)
   - Nitrógeno (número, ppm, opcional)
   - Laboratorio (texto, requerido)
4. Previsualiza formulario
5. Activa el tipo
6. Técnicos ahora pueden registrar este nuevo evento

---

**Siguiente**: [Arquitectura del Sistema →](./03_arquitectura.md)

[← Volver al índice](../README.md)
