# API de Reportes - Documentación

## Descripción General

La API de Reportes permite generar documentos de trazabilidad en diferentes formatos (PDF, Excel, CSV) tanto para lotes individuales como para campañas completas.

**Base URL:** `/api/v1/reports/`

**Autenticación:** Todas las APIs requieren autenticación mediante token o sesión.

---

## Endpoints Disponibles

### 1. Listar Tipos de Reportes

**GET** `/api/v1/reports/types/`

Obtiene información sobre los tipos de reportes disponibles.

#### Respuesta Exitosa (200)

```json
[
  {
    "report_type": "field_traceability",
    "description": "Reporte de trazabilidad completo de un lote específico con historial de eventos",
    "formats": ["pdf", "excel", "csv"],
    "endpoint": "/api/v1/reports/field-traceability/"
  },
  {
    "report_type": "campaign_traceability",
    "description": "Reporte consolidado de todos los eventos de una campaña agrícola",
    "formats": ["pdf", "excel", "csv"],
    "endpoint": "/api/v1/reports/campaign-traceability/"
  }
]
```

---

### 2. Generar Reporte de Trazabilidad por Lote

**POST** `/api/v1/reports/field-traceability/`

Genera un reporte de trazabilidad completo para un lote específico.

#### Parámetros del Body (JSON)

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `field_id` | UUID | Sí | ID del lote |
| `date_from` | Date | No | Fecha inicio (YYYY-MM-DD) |
| `date_to` | Date | No | Fecha fin (YYYY-MM-DD) |
| `campaign_id` | UUID | No | ID de campaña para filtrar |
| `event_types` | Array[UUID] | No | IDs de tipos de eventos |
| `format` | String | No | Formato: `pdf`, `excel`, `csv` (default: `pdf`) |

#### Ejemplo 1: Reporte PDF Básico

```json
{
  "field_id": "123e4567-e89b-12d3-a456-426614174000",
  "format": "pdf"
}
```

#### Ejemplo 2: Reporte Excel con Filtros

```json
{
  "field_id": "123e4567-e89b-12d3-a456-426614174000",
  "date_from": "2024-01-01",
  "date_to": "2024-12-31",
  "campaign_id": "987e6543-e21b-43d3-a456-426614174999",
  "event_types": [
    "111e1111-e11b-11d3-a456-426614174111",
    "222e2222-e22b-22d3-a456-426614174222"
  ],
  "format": "excel"
}
```

#### Respuesta Exitosa (200)

Archivo binario en el formato solicitado con headers:
- `Content-Type`: `application/pdf` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | `text/csv`
- `Content-Disposition`: `attachment; filename="trazabilidad_LOTE01_20241112_182900.pdf"`

#### Errores Posibles

**400 Bad Request**
```json
{
  "error": {
    "field_id": ["Este campo es requerido."]
  }
}
```

**404 Not Found**
```json
{
  "error": "El lote especificado no existe"
}
```

**500 Internal Server Error**
```json
{
  "error": "Error al generar el reporte: [detalle del error]"
}
```

#### cURL Example

```bash
curl -X POST http://localhost:8000/api/v1/reports/field-traceability/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "123e4567-e89b-12d3-a456-426614174000",
    "format": "pdf"
  }' \
  -o reporte_lote.pdf
```

---

### 3. Generar Reporte de Trazabilidad por Campaña

**POST** `/api/v1/reports/campaign-traceability/`

Genera un reporte consolidado para una campaña completa.

#### Parámetros del Body (JSON)

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `campaign_id` | UUID | Sí | ID de la campaña |
| `field_ids` | Array[UUID] | No | IDs de lotes específicos (vacío = todos) |
| `event_types` | Array[UUID] | No | IDs de tipos de eventos (vacío = todos) |
| `format` | String | No | Formato: `pdf`, `excel`, `csv` (default: `pdf`) |

#### Ejemplo 1: Reporte PDF de Campaña Completa

```json
{
  "campaign_id": "789e4567-e89b-12d3-a456-426614174789",
  "format": "pdf"
}
```

#### Ejemplo 2: Reporte Excel Filtrado

```json
{
  "campaign_id": "789e4567-e89b-12d3-a456-426614174789",
  "field_ids": [
    "123e4567-e89b-12d3-a456-426614174000",
    "456e7890-e89b-12d3-a456-426614174456"
  ],
  "event_types": [
    "111e1111-e11b-11d3-a456-426614174111"
  ],
  "format": "excel"
}
```

#### Respuesta Exitosa (200)

Archivo binario en el formato solicitado con headers:
- `Content-Type`: `application/pdf` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | `text/csv`
- `Content-Disposition`: `attachment; filename="trazabilidad_campana_Primavera_2024_20241112_182900.pdf"`

#### Errores Posibles

**400 Bad Request**
```json
{
  "error": {
    "campaign_id": ["Este campo es requerido."]
  }
}
```

**404 Not Found**
```json
{
  "error": "La campaña especificada no existe"
}
```

**500 Internal Server Error**
```json
{
  "error": "Error al generar el reporte: [detalle del error]"
}
```

#### cURL Example

```bash
curl -X POST http://localhost:8000/api/v1/reports/campaign-traceability/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "789e4567-e89b-12d3-a456-426614174789",
    "format": "excel"
  }' \
  -o reporte_campana.xlsx
```

---

## Contenido de los Reportes

### Reporte de Trazabilidad por Lote

**Formato PDF:**
- Información general del lote (nombre, código, ubicación, superficie)
- Resumen estadístico (total de eventos, eventos por tipo)
- Línea de tiempo completa con todos los eventos
- Detalles de cada evento (fecha, tipo, responsable, observaciones)
- Lista de archivos adjuntos
- Gráfico de distribución de eventos por tipo

**Formato Excel:**
- Hoja 1: Lista completa de eventos con todos los campos
- Hoja 2: Resumen estadístico
- Hoja 3: Información del lote
- Formato profesional con filtros y tablas

**Formato CSV:**
- Datos tabulares con todos los campos de eventos
- Compatible con Excel y herramientas de análisis
- Codificación UTF-8 con BOM

### Reporte de Trazabilidad por Campaña

**Formato PDF:**
- Información general de la campaña
- Estadísticas consolidadas por lote
- Resumen de eventos por tipo
- Comparativas entre lotes
- Distribución temporal de actividades
- Totales de insumos utilizados

**Formato Excel:**
- Hoja 1: Eventos consolidados de todos los lotes
- Hoja 2: Resumen por lote
- Hoja 3: Información de la campaña
- Tablas dinámicas y gráficos comparativos

**Formato CSV:**
- Datos consolidados de eventos de la campaña
- Incluye información del lote en cada registro
- Apto para análisis masivo de datos

---

## Casos de Uso

### 1. Auditoría de un Lote Específico
```json
POST /api/v1/reports/field-traceability/
{
  "field_id": "...",
  "format": "pdf"
}
```
→ Documento profesional para auditorías y certificaciones

### 2. Análisis de Datos de Campaña
```json
POST /api/v1/reports/campaign-traceability/
{
  "campaign_id": "...",
  "format": "excel"
}
```
→ Hojas de cálculo para análisis detallado

### 3. Exportación para Sistemas Externos
```json
POST /api/v1/reports/field-traceability/
{
  "field_id": "...",
  "format": "csv"
}
```
→ Datos tabulares para importar en otros sistemas

### 4. Reporte Filtrado por Tipo de Evento
```json
POST /api/v1/reports/campaign-traceability/
{
  "campaign_id": "...",
  "event_types": ["id_riego", "id_fertilizacion"],
  "format": "pdf"
}
```
→ Reporte especializado solo con riegos y fertilizaciones

---

## Notas Importantes

1. **Autenticación:** Todos los endpoints requieren autenticación
2. **Formatos:** Cada formato tiene un propósito específico:
   - PDF: Presentaciones, auditorías, impresión
   - Excel: Análisis detallado, gráficos, filtros
   - CSV: Integración con otros sistemas, análisis masivo
3. **Performance:** La generación de reportes puede tomar tiempo dependiendo del volumen de datos
4. **Filtros:** Los filtros opcionales permiten generar reportes específicos según necesidades
5. **Nombres de archivo:** Se generan automáticamente con timestamp para evitar conflictos

---

## Testing en Swagger

Accede a la documentación interactiva en:
- **Swagger UI:** http://localhost:8000/api/schema/swagger-ui/
- **ReDoc:** http://localhost:8000/api/schema/redoc/

En Swagger UI puedes:
1. Ver todos los endpoints documentados
2. Probar las APIs directamente desde el navegador
3. Ver ejemplos de request/response
4. Descargar el esquema OpenAPI

---

## Próximos Desarrollos

- [ ] Reportes programados (scheduling)
- [ ] Envío de reportes por email
- [ ] Reportes personalizados con plantillas
- [ ] Dashboard de métricas agregadas
- [ ] Reportes comparativos entre campañas
