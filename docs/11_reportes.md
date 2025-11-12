# Sistema de Reportes y Exportación de Datos

[← Volver al índice](../README.md) | [← Pruebas](./10_pruebas.md)

## 1. Introducción

El **Sistema de Reportes** permite a los usuarios generar, visualizar y exportar información del sistema de trazabilidad en diversos formatos. Este módulo es fundamental para el análisis de datos, toma de decisiones y cumplimiento de requisitos de certificación.

### 1.1 Objetivos

- **Análisis de Datos**: Facilitar el análisis de eventos y variables ambientales
- **Trazabilidad Completa**: Generar reportes de trazabilidad por lote/campaña
- **Exportación Flexible**: Permitir exportar datos en múltiples formatos
- **Certificación**: Generar documentación para auditorías y certificaciones
- **Toma de Decisiones**: Proporcionar KPIs y dashboards interactivos

### 1.2 Formatos de Exportación Soportados

| Formato | Descripción | Casos de Uso |
|---------|-------------|--------------|
| **PDF** | Documento imprimible | Reportes oficiales, certificaciones, auditorías |
| **CSV** | Valores separados por comas | Análisis en Excel, importación a otros sistemas |
| **Excel (XLSX)** | Hoja de cálculo | Análisis avanzado, gráficos, tablas dinámicas |
| **JSON** | Formato estructurado | Integración con otros sistemas, APIs |

## 2. Tipos de Reportes

### 2.1 Reportes de Trazabilidad

#### 2.1.1 Reporte de Trazabilidad por Lote

**Descripción**: Historial completo de eventos de un lote específico.

**Parámetros**:
- Lote (requerido)
- Rango de fechas (opcional)
- Campaña (opcional)
- Tipos de evento (opcional)

**Contenido**:
```
┌─────────────────────────────────────────────┐
│ REPORTE DE TRAZABILIDAD                     │
│ Lote: Campo Norte (NORTE-01)               │
│ Período: 01/01/2025 - 31/03/2025          │
│ Campaña: Primavera 2025                    │
└─────────────────────────────────────────────┘

📊 RESUMEN EJECUTIVO
- Total de eventos: 45
- Eventos de riego: 12
- Aplicaciones fitosanitarias: 8
- Fertilizaciones: 6
- Labores de cultivo: 10
- Cosechas: 2
- Otros: 7

📅 LÍNEA DE TIEMPO DE EVENTOS

┌─────────────┬──────────────────┬─────────────┐
│ Fecha       │ Tipo             │ Detalle     │
├─────────────┼──────────────────┼─────────────┤
│ 15/01/2025  │ Riego            │ Goteo 120min│
│ 18/01/2025  │ Fertilización    │ NPK 15-15-15│
│ 22/01/2025  │ Fitosanitario    │ Fungicida   │
│ ...         │ ...              │ ...         │
└─────────────┴──────────────────┴─────────────┘

📎 ARCHIVOS ADJUNTOS: 23 archivos
```

**Formatos Disponibles**:
- ✅ PDF (reporte formal con logos y firmas)
- ✅ CSV (datos tabulares para análisis)
- ✅ Excel (con múltiples hojas: resumen, detalle, adjuntos)

#### 2.1.2 Reporte de Trazabilidad por Campaña

**Descripción**: Vista consolidada de todos los lotes en una campaña.

**Parámetros**:
- Campaña (requerido)
- Lotes (opcional, por defecto todos)
- Tipos de evento (opcional)

**Contenido**:
- Resumen por lote
- Eventos totales por tipo
- Comparativa entre lotes
- Indicadores de rendimiento
- Cosecha total

**Formatos Disponibles**:
- ✅ PDF (reporte ejecutivo)
- ✅ Excel (análisis comparativo)

### 2.2 Reportes de Eventos Específicos

#### 2.2.1 Reporte de Aplicaciones Fitosanitarias

**Descripción**: Registro detallado de aplicaciones de productos químicos.

**Parámetros**:
- Rango de fechas
- Lote(s)
- Tipo de producto (opcional)

**Contenido**:
```
REGISTRO DE APLICACIONES FITOSANITARIAS

Producto: Mancozeb 80%
Ingrediente Activo: Mancozeb
Dosis: 2.5 kg/ha
Área Tratada: 3.5 ha
Intervalo de Seguridad: 14 días
Fecha de Aplicación: 15/03/2025
Próxima Cosecha Segura: 29/03/2025
Responsable: Juan Pérez
```

**Uso**: Certificaciones orgánicas, auditorías sanitarias, cumplimiento normativo.

**Formatos**:
- ✅ PDF (certificado oficial)
- ✅ CSV (base de datos)

#### 2.2.2 Reporte de Balance Hídrico

**Descripción**: Análisis del consumo de agua y eficiencia de riego.

**Parámetros**:
- Lote(s)
- Rango de fechas
- Tipo de riego (opcional)

**Contenido**:
- Volumen total aplicado (m³)
- Precipitación acumulada (mm)
- Agua total disponible
- Eficiencia de riego (%)
- Distribución por método de riego
- Gráficos de tendencia

**Formatos**:
- ✅ PDF (con gráficos)
- ✅ Excel (datos y gráficos interactivos)

#### 2.2.3 Reporte de Balance Nutricional

**Descripción**: Seguimiento de aplicaciones de fertilizantes.

**Parámetros**:
- Lote(s)
- Rango de fechas

**Contenido**:
- NPK total aplicado (kg/ha)
- Distribución por tipo de fertilizante
- Balance de nutrientes
- Recomendaciones de ajuste
- Comparativa con estándares

**Formatos**:
- ✅ PDF
- ✅ Excel

#### 2.2.4 Reporte de Cosecha

**Descripción**: Análisis de producción y calidad.

**Parámetros**:
- Campaña
- Lote(s) (opcional)

**Contenido**:
```
REPORTE DE COSECHA - CAMPAÑA PRIMAVERA 2025

Total Cosechado: 45,500 kg
Rendimiento Promedio: 18,200 kg/ha

Distribución por Calidad:
- Primera: 32,200 kg (70.8%)
- Segunda: 10,150 kg (22.3%)
- Tercera: 3,150 kg (6.9%)

Destino:
- Exportación: 28,600 kg (62.9%)
- Mercado Nacional: 13,750 kg (30.2%)
- Industria: 3,150 kg (6.9%)

Rendimiento por Lote:
┌───────────────┬─────────────┬──────────────┐
│ Lote          │ Superficie  │ Rendimiento  │
├───────────────┼─────────────┼──────────────┤
│ Campo Norte   │ 2.5 ha      │ 19,400 kg/ha │
│ Campo Sur     │ 3.0 ha      │ 17,800 kg/ha │
│ Campo Este    │ 1.8 ha      │ 16,500 kg/ha │
└───────────────┴─────────────┴──────────────┘
```

**Formatos**:
- ✅ PDF (reporte ejecutivo)
- ✅ Excel (análisis detallado)

### 2.3 Reportes Analíticos y KPIs

#### 2.3.1 Dashboard de Indicadores

**Descripción**: Vista consolidada de KPIs en tiempo real.

**KPIs Incluidos**:

1. **Eficiencia de Riego**
   - Fórmula: `(Incremento de humedad / Volumen aplicado) × 100`
   - Objetivo: > 75%

2. **Productividad por Hectárea**
   - Fórmula: `Total kg cosechados / Superficie total`
   - Benchmark: 18,000 kg/ha

3. **Índice de Aplicaciones Fitosanitarias**
   - Fórmula: `Total aplicaciones / Superficie / Período`
   - Objetivo: < 2 aplicaciones/ha/mes

4. **Tasa de Incidencia de Plagas**
   - Fórmula: `(Eventos de brote / Total eventos monitoreo) × 100`
   - Objetivo: < 10%

5. **Índice de Calidad de Cosecha**
   - Fórmula: `(Primera + Segunda) / Total × 100`
   - Objetivo: > 90%

6. **Costo de Mano de Obra por Hectárea**
   - Fórmula: `Total costos laborales / Superficie`
   - Benchmark: Variable por región

**Visualizaciones**:
- Gráficos de barras (comparativas)
- Gráficos de línea (tendencias)
- Gráficos circulares (distribuciones)
- Mapas de calor (por lote)

**Formatos**:
- ✅ Web (dashboard interactivo)
- ✅ PDF (snapshot)
- ✅ Excel (datos + gráficos)

#### 2.3.2 Análisis de Tendencias

**Descripción**: Evolución de variables en el tiempo.

**Análisis Disponibles**:
- Tendencia de rendimiento por campaña
- Evolución de incidencia de plagas
- Patrón de uso de agua
- Correlación clima-rendimiento
- Efectividad de tratamientos

**Formatos**:
- ✅ PDF (con gráficos de tendencia)
- ✅ Excel (datos históricos)

### 2.4 Reportes para Certificación

#### 2.4.1 Reporte de Trazabilidad para Auditoría

**Descripción**: Documentación completa para auditorías de certificación (GlobalGAP, orgánico, etc.).

**Contenido**:
- Identificación completa del lote
- Registro cronológico de todos los eventos
- Evidencias fotográficas (adjuntos)
- Registros de aplicaciones con intervalos de seguridad
- Análisis de suelo y agua
- Capacitaciones del personal
- Firmas digitales y validaciones

**Características**:
- Formato oficial con logo
- Numeración de páginas
- Código QR de verificación
- Marca de agua "ORIGINAL"
- Campos para firmas de responsables

**Formatos**:
- ✅ PDF (firmado digitalmente)

#### 2.4.2 Registro de Buenas Prácticas Agrícolas (BPA)

**Descripción**: Cumplimiento de normativas de BPA.

**Secciones**:
- Uso responsable de agroquímicos
- Gestión integrada de plagas
- Uso eficiente del agua
- Manejo de residuos
- Higiene y seguridad laboral

**Formatos**:
- ✅ PDF

## 3. Exportación de Datos

### 3.1 Exportación Masiva

#### 3.1.1 Exportar Todos los Eventos

**Descripción**: Descarga completa de la base de datos de eventos.

**Parámetros**:
- Rango de fechas (requerido)
- Lotes (opcional)
- Tipos de evento (opcional)

**Estructura CSV**:
```csv
id,tipo_evento,lote,campaña,fecha_hora,campo_1,campo_2,...,observaciones,creado_por,creado_el
uuid1,Riego,Norte,Primavera2025,2025-01-15 08:00,Goteo,120,...,Sin novedades,jperez,2025-01-15 09:30
```

**Estructura Excel**:
- Hoja 1: Eventos (todos los campos)
- Hoja 2: Resumen por tipo
- Hoja 3: Resumen por lote
- Hoja 4: Adjuntos (lista de archivos)

**Formatos**:
- ✅ CSV (datos planos)
- ✅ Excel (multi-hoja con formato)
- ✅ JSON (para APIs)

#### 3.1.2 Exportar Variables Ambientales

**Descripción**: Descarga de lecturas de sensores y variables.

**Parámetros**:
- Estación/Lote
- Rango de fechas
- Tipos de variable (opcional)

**Estructura CSV**:
```csv
timestamp,estacion,lote,tipo_variable,valor,unidad,origen
2025-01-15 08:00:00,Estacion-1,Norte,temperatura_aire,28.5,°C,automatico
2025-01-15 08:00:00,Estacion-1,Norte,humedad_suelo,65.2,%,automatico
```

**Formatos**:
- ✅ CSV
- ✅ Excel

### 3.2 Exportación Selectiva

#### 3.2.1 Exportar Eventos por Tipo

**Ejemplo**: Exportar solo eventos de riego del último mes.

**Parámetros**:
- Tipo de evento: Aplicación de Riego
- Fecha desde: 01/03/2025
- Fecha hasta: 31/03/2025

**Columnas Específicas**:
```csv
fecha,lote,metodo,duracion_min,volumen_m3,fuente_agua,ce_uScm,ph
2025-03-01,Norte,Goteo,120,45.5,Pozo,850,6.7
```

#### 3.2.2 Exportar con Filtros Avanzados

**Filtros Disponibles**:
- Por responsable
- Por campaña
- Por rango de valores (ej: riego > 100 minutos)
- Por existencia de adjuntos
- Por texto en observaciones

## 4. Arquitectura del Sistema de Reportes

### 4.1 Componentes

```
┌─────────────────────────────────────────────┐
│           CAPA DE PRESENTACIÓN              │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
│  │Dashboard │  │Reportes  │  │Exportar   │ │
│  │Web       │  │Web       │  │Datos      │ │
│  └──────────┘  └──────────┘  └───────────┘ │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────┴──────────────────────────┐
│           CAPA DE LÓGICA                    │
│  ┌──────────────────────────────────────┐   │
│  │   Generadores de Reportes            │   │
│  │  - ReportGenerator (Base)            │   │
│  │  - PDFReportGenerator                │   │
│  │  - CSVExporter                       │   │
│  │  - ExcelExporter                     │   │
│  └──────────────────────────────────────┘   │
│  ┌──────────────────────────────────────┐   │
│  │   Calculadores de KPIs               │   │
│  │  - IrrigationEfficiency              │   │
│  │  - YieldAnalyzer                     │   │
│  │  - PestIncidenceCalculator           │   │
│  └──────────────────────────────────────┘   │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────┴──────────────────────────┐
│           CAPA DE DATOS                     │
│  ┌──────────────────────────────────────┐   │
│  │   Repositorios                       │   │
│  │  - EventRepository                   │   │
│  │  - VariableRepository                │   │
│  │  - AggregationQueries                │   │
│  └──────────────────────────────────────┘   │
└──────────────────┬──────────────────────────┘
                   │
           ┌───────┴────────┐
           │   PostgreSQL   │
           └────────────────┘
```

### 4.2 Tecnologías

| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| **PDF** | ReportLab o WeasyPrint | Generación de PDFs con diseño |
| **Excel** | openpyxl | Generación de archivos .xlsx |
| **CSV** | Python csv module | Exportación simple |
| **Gráficos** | Matplotlib o Chart.js | Visualizaciones |
| **Templates** | Django Templates | Renderizado HTML para PDFs |
| **Caché** | Django Cache | Caché de reportes pesados |
| **Tareas Asíncronas** | Celery (opcional) | Generación en background |

### 4.3 Flujo de Generación de Reportes

```
Usuario → Solicita Reporte → Sistema
                                │
                                ↓
                    Valida Parámetros
                                │
                                ↓
                    Consulta Base de Datos
                                │
                                ↓
                    Procesa y Agrega Datos
                                │
                                ↓
                    Calcula KPIs (si aplica)
                                │
                                ↓
                    Aplica Formato
                                │
                    ┌───────────┴────────────┐
                    ↓                        ↓
              Genera PDF              Genera Excel/CSV
                    │                        │
                    └───────────┬────────────┘
                                ↓
                    Almacena en Media (opcional)
                                │
                                ↓
                    Retorna archivo al usuario
```

## 5. Casos de Uso

### 5.1 Caso de Uso: Auditoría de Certificación

**Actor**: Auditor Externo  
**Objetivo**: Verificar cumplimiento de BPA

**Flujo**:
1. Administrador genera "Reporte de Trazabilidad para Auditoría"
2. Selecciona lote y campaña
3. Sistema genera PDF con:
   - Todos los eventos registrados
   - Evidencias fotográficas
   - Intervalos de seguridad cumplidos
   - Análisis de laboratorio
4. PDF incluye código QR de verificación
5. Auditor descarga y verifica autenticidad

### 5.2 Caso de Uso: Análisis de Rendimiento

**Actor**: Ingeniero Agrónomo  
**Objetivo**: Analizar eficiencia de riego

**Flujo**:
1. Accede a Dashboard de KPIs
2. Selecciona "Eficiencia de Riego"
3. Filtra por lote y últimos 3 meses
4. Visualiza gráfico de tendencia
5. Exporta datos a Excel para análisis detallado
6. Realiza tablas dinámicas y correlaciones
7. Genera recomendaciones de ajuste

### 5.3 Caso de Uso: Exportación para Sistema Externo

**Actor**: Sistema ERP  
**Objetivo**: Importar datos de cosecha

**Flujo**:
1. Sistema hace petición API:
   ```
   GET /api/v1/reports/harvest-export/?campaign=5&format=csv
   ```
2. API retorna CSV con datos de cosecha
3. Sistema ERP procesa archivo
4. Actualiza inventario y contabilidad

## 6. Interfaz de Usuario

### 6.1 Página Principal de Reportes

```
┌────────────────────────────────────────────────┐
│ 📊 Sistema de Reportes y Exportación          │
└────────────────────────────────────────────────┘

🔍 REPORTES DE TRAZABILIDAD
┌──────────────────┬──────────────────┐
│ 📄 Por Lote      │ 📅 Por Campaña   │
│ Historial        │ Consolidado      │
│ completo         │ multi-lote       │
└──────────────────┴──────────────────┘

📈 REPORTES ANALÍTICOS
┌──────────────────┬──────────────────┬──────────────────┐
│ 💧 Balance       │ 🌱 Balance       │ 📊 KPIs y        │
│ Hídrico          │ Nutricional      │ Dashboard        │
└──────────────────┴──────────────────┴──────────────────┘

🎯 REPORTES ESPECÍFICOS
┌──────────────────┬──────────────────┬──────────────────┐
│ 🧪 Fitosanitarios│ 🌾 Cosecha       │ 👷 Mano de Obra  │
└──────────────────┴──────────────────┴──────────────────┘

📥 EXPORTACIÓN DE DATOS
┌──────────────────┬──────────────────┐
│ 📋 Todos Eventos │ 📉 Variables     │
│ CSV/Excel/JSON   │ Ambientales      │
└──────────────────┴──────────────────┘
```

### 6.2 Formulario de Generación

```
┌────────────────────────────────────────────┐
│ Generar Reporte de Trazabilidad por Lote  │
├────────────────────────────────────────────┤
│                                            │
│ Lote: [Campo Norte ▼]                     │
│                                            │
│ Rango de Fechas:                          │
│ Desde: [01/01/2025]  Hasta: [31/03/2025] │
│                                            │
│ Campaña (opcional): [Primavera 2025 ▼]   │
│                                            │
│ Tipos de Evento (opcional):               │
│ ☑ Riego                                   │
│ ☑ Fertilización                           │
│ ☑ Fitosanitario                           │
│ ☐ Labores                                 │
│ ☐ Cosecha                                 │
│ ☑ Todos                                   │
│                                            │
│ Formato:                                   │
│ ● PDF    ○ Excel    ○ CSV                │
│                                            │
│ Opciones Avanzadas:                       │
│ ☑ Incluir archivos adjuntos               │
│ ☑ Incluir observaciones                   │
│ ☑ Incluir datos de responsables           │
│                                            │
│ [Generar Reporte] [Cancelar]              │
└────────────────────────────────────────────┘
```

## 7. Seguridad y Permisos

### 7.1 Matriz de Permisos

| Rol | Ver Reportes | Generar Reportes | Exportar Datos | Dashboard KPIs |
|-----|--------------|------------------|----------------|----------------|
| **Admin** | ✅ Todos | ✅ Todos | ✅ Todos | ✅ |
| **Supervisor** | ✅ Todos | ✅ Todos | ✅ CSV/Excel | ✅ |
| **Técnico** | ✅ Sus lotes | ✅ Sus lotes | ✅ CSV | ❌ |
| **Consultor** | ✅ Lectura | ✅ Lectura | ✅ Todos | ✅ |
| **Integración** | ❌ | ❌ | ✅ API JSON | ❌ |

### 7.2 Auditoría de Reportes

Todos los reportes generados se registran:
- Usuario que generó
- Tipo de reporte
- Parámetros utilizados
- Fecha y hora
- Formato exportado
- IP de origen

## 8. Optimización y Rendimiento

### 8.1 Estrategias de Caché

```python
# Caché de reportes frecuentes
@cache_page(60 * 15)  # 15 minutos
def dashboard_kpis(request):
    # ...
    
# Caché de agregaciones pesadas
def get_irrigation_efficiency(field_id, date_range):
    cache_key = f'irrigation_eff_{field_id}_{date_range}'
    result = cache.get(cache_key)
    if result is None:
        result = calculate_irrigation_efficiency(field_id, date_range)
        cache.set(cache_key, result, 3600)  # 1 hora
    return result
```

### 8.2 Procesamiento Asíncrono

Para reportes pesados (> 10,000 registros):
```python
# Encolar tarea en Celery
@shared_task
def generate_large_report(params):
    # Generar reporte
    # Guardar en media/
    # Enviar email con link de descarga
    pass
```

### 8.3 Paginación y Límites

- Vista web: 50 registros por página
- Exportación CSV: Máximo 50,000 registros
- Exportación Excel: Máximo 100,000 registros
- API JSON: Paginación obligatoria (100 por página)

## 9. Roadmap de Implementación

### Fase 1 - MVP (Implementado)
- ✅ Health check API
- ✅ Estructura básica de app reports

### Fase 2 - Reportes Básicos (Sprint 1)
- [ ] Reporte de trazabilidad por lote (PDF)
- [ ] Exportación de eventos a CSV
- [ ] Dashboard básico de KPIs

### Fase 3 - Exportación Avanzada (Sprint 2)
- [ ] Exportación a Excel con múltiples hojas
- [ ] Filtros avanzados
- [ ] Reporte de fitosanitarios

### Fase 4 - Análisis (Sprint 3)
- [ ] Balance hídrico
- [ ] Balance nutricional
- [ ] Análisis de tendencias
- [ ] Gráficos interactivos

### Fase 5 - Certificación (Sprint 4)
- [ ] Reporte de auditoría
- [ ] Registro BPA
- [ ] Firma digital
- [ ] Código QR de verificación

## 10. Ejemplos de Código

### 10.1 Exportar Eventos a CSV

```python
# reports/views.py
import csv
from django.http import HttpResponse
from apps.events.models import Event

def export_events_csv(request):
    # Obtener parámetros
    field_id = request.GET.get('field')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Filtrar eventos
    events = Event.objects.filter(
        field_id=field_id,
        timestamp__range=[date_from, date_to]
    ).select_related('event_type', 'field', 'campaign', 'created_by')
    
    # Crear respuesta CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="eventos_{field_id}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Tipo', 'Lote', 'Campaña', 'Fecha/Hora',
        'Observaciones', 'Creado Por', 'Creado El'
    ])
    
    for event in events:
        writer.writerow([
            event.id,
            event.event_type.name,
            event.field.name,
            event.campaign.name if event.campaign else '',
            event.timestamp.strftime('%Y-%m-%d %H:%M'),
            event.observations or '',
            event.created_by.get_full_name() if event.created_by else '',
            event.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    return response
```

### 10.2 Generar Reporte PDF con ReportLab

```python
# reports/generators/pdf.py
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

def generate_traceability_pdf(field, events):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Contenido
    story = []
    
    # Título
    title = Paragraph(f"Reporte de Trazabilidad - {field.name}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Tabla de eventos
    data = [['Fecha', 'Tipo', 'Detalle']]
    for event in events:
        data.append([
            event.timestamp.strftime('%d/%m/%Y'),
            event.event_type.name,
            event.observations[:50] if event.observations else ''
        ])
    
    table = Table(data)
    story.append(table)
    
    # Generar PDF
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf
```

### 10.3 Calcular KPI de Eficiencia de Riego

```python
# reports/kpis/irrigation.py
from apps.events.models import IrrigationEvent
from django.db.models import Sum, Avg

def calculate_irrigation_efficiency(field_id, date_range):
    """
    Calcula eficiencia de riego basado en volumen aplicado.
    """
    events = IrrigationEvent.objects.filter(
        field_id=field_id,
        timestamp__range=date_range,
        volumen_m3__isnull=False
    )
    
    stats = events.aggregate(
        total_volume=Sum('volumen_m3'),
        avg_duration=Avg('duracion_minutos'),
        total_events=Count('id')
    )
    
    field_area = Field.objects.get(id=field_id).surface_ha
    
    efficiency = {
        'total_volume_m3': stats['total_volume'] or 0,
        'avg_duration_min': stats['avg_duration'] or 0,
        'total_events': stats['total_events'],
        'volume_per_ha': (stats['total_volume'] or 0) / field_area,
        'field_area_ha': field_area
    }
    
    return efficiency
```

## 11. Conclusión

El Sistema de Reportes es un componente crítico que transforma los datos de trazabilidad en información útil para la toma de decisiones, cumplimiento normativo y mejora continua. La implementación por fases permite entregar valor incremental mientras se construye funcionalidad más avanzada.

---

**Próximos Pasos**:
1. Implementar exportación CSV básica
2. Crear reporte de trazabilidad en PDF
3. Desarrollar dashboard de KPIs
4. Agregar exportación a Excel
