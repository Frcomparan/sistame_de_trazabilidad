# Sistema de Reportes - Guía de Uso

## 📋 Descripción

El sistema de reportes permite generar documentos PDF profesionales, exportar datos a Excel y CSV, y analizar la información de trazabilidad del sistema.

## 🚀 Funcionalidades Implementadas

### ✅ Generación de Reportes PDF
- **Reporte de Trazabilidad por Lote**: Documento profesional con:
  - Información general del lote
  - Resumen estadístico de eventos
  - Línea de tiempo completa
  - Lista de archivos adjuntos
  - Diseño profesional listo para imprimir o presentar

### ✅ Exportación de Datos
- **CSV**: Datos tabulares simples para análisis en Excel u otras herramientas
- **Excel (XLSX)**: Archivos con formato profesional, múltiples hojas:
  - Hoja de eventos con todos los datos
  - Hoja de resumen estadístico
  - Formato con colores y diseño

### ✅ Filtros Avanzados
- Por lote
- Por campaña
- Por rango de fechas
- Por tipos de evento específicos

## 🎯 Cómo Usar

### 1. Acceder al Sistema de Reportes

1. Inicia sesión en el sistema
2. En el menú de navegación superior, haz clic en **"Reportes"**
3. Verás el dashboard principal de reportes

### 2. Generar un Reporte de Trazabilidad

#### Opción A: Desde el Dashboard
1. En el dashboard de reportes, haz clic en **"Generar Reporte"** en la tarjeta "Trazabilidad por Lote"

#### Opción B: URL Directa
```
http://localhost:8000/reportes/trazabilidad/
```

#### Completar el Formulario:

**Parámetros Básicos:**
- **Lote** (requerido): Selecciona el lote sobre el cual generar el reporte
- **Campaña** (opcional): Filtra eventos de una campaña específica
- **Fecha Desde** (opcional): Inicio del período a reportar
- **Fecha Hasta** (opcional): Fin del período a reportar

**Filtrar por Tipos de Evento:**
- Marca los tipos de evento que quieres incluir
- Si no seleccionas ninguno, se incluyen todos
- Botones de ayuda: "Seleccionar Todos" / "Deseleccionar Todos"

**Formato de Exportación:**
- **PDF**: Reporte imprimible profesional (recomendado para presentaciones)
- **Excel**: Hoja de cálculo con formato (para análisis detallado)
- **CSV**: Datos tabulares simples (para importar a otros sistemas)

3. Haz clic en **"Generar Reporte"**
4. El archivo se descargará automáticamente

### 3. Exportación Masiva de Datos

Para exportar todos los eventos del sistema:

1. En el dashboard de reportes, en la sección "Exportación de Datos"
2. Haz clic en el botón **CSV** o **Excel**
3. Se descargará el archivo con todos los eventos

#### Con Filtros (vía URL):
```
# Exportar eventos de un lote específico
http://localhost:8000/reportes/exportar/?format=csv&field_id=1

# Con rango de fechas
http://localhost:8000/reportes/exportar/?format=excel&date_from=2025-01-01&date_to=2025-03-31

# Lote y fechas
http://localhost:8000/reportes/exportar/?format=csv&field_id=1&date_from=2025-01-01&date_to=2025-03-31
```

## 📊 Estructura de los Reportes

### Reporte PDF de Trazabilidad

El PDF incluye:

1. **Encabezado**: Logo y título del sistema
2. **Información General**:
   - Nombre y código del lote
   - Superficie del lote
   - Campaña (si aplica)
   - Período del reporte
   - Fecha de generación

3. **Resumen Ejecutivo**:
   - Total de eventos
   - Archivos adjuntos
   - Tipos de evento registrados

4. **Distribución por Tipo**:
   - Tabla con cantidad de eventos por tipo

5. **Línea de Tiempo**:
   - Tabla completa con todos los eventos:
     - Fecha y hora
     - Tipo de evento (con badge de color)
     - Observaciones
     - Responsable
     - Número de adjuntos

6. **Archivos Adjuntos**:
   - Lista de todos los archivos con detalles

7. **Footer**:
   - Información de generación
   - Sección de firmas

### Exportación Excel (XLSX)

El archivo Excel contiene:

**Hoja 1 - Eventos**:
- Todas las columnas de eventos
- Encabezados con formato (fondo azul, texto blanco)
- Filas alternadas con color de fondo
- Columnas con ancho ajustado

**Hoja 2 - Resumen**:
- Total de eventos
- Fecha de generación
- Metadatos del reporte

### Exportación CSV

Archivo de texto plano con:
- Codificación UTF-8 con BOM (compatible con Excel)
- Separador: coma (,)
- Columnas:
  - id
  - tipo_evento
  - lote
  - campana
  - fecha_hora
  - observaciones
  - creado_por
  - creado_el

## 🔧 Características Técnicas

### Tecnologías Utilizadas

- **WeasyPrint 62.3**: Generación de PDFs desde HTML/CSS
- **openpyxl 3.1.5**: Generación de archivos Excel
- **Django Templates**: Renderizado de HTML para PDFs
- **Python CSV Module**: Exportación CSV

### Generadores Disponibles

Los siguientes generadores están disponibles en `apps/reports/generators.py`:

1. **PDFReportGenerator**:
   - `generate_traceability_report()`: Reporte de trazabilidad
   - `generate_phytosanitary_report()`: Reporte fitosanitario (próximamente)

2. **CSVExporter**:
   - `export_events()`: Exportar eventos a CSV

3. **ExcelExporter**:
   - `export_events()`: Exportar eventos a Excel

### Optimizaciones

- **Caché**: Los reportes frecuentes se cachean (próximamente)
- **Paginación**: Límite de registros para evitar archivos enormes
- **Consultas Optimizadas**: Uso de `select_related()` para reducir queries

## 📝 Ejemplos de Uso

### Ejemplo 1: Reporte Completo de un Lote

```
Lote: Campo Norte
Fecha Desde: 2025-01-01
Fecha Hasta: 2025-03-31
Campaña: Primavera 2025
Tipos de Evento: Todos
Formato: PDF
```

**Resultado**: PDF con todos los eventos del lote "Campo Norte" durante el primer trimestre de 2025.

### Ejemplo 2: Solo Eventos de Riego

```
Lote: Campo Sur
Tipos de Evento: [✓] Aplicación de Riego
Formato: Excel
```

**Resultado**: Excel con solo los eventos de riego del lote "Campo Sur".

### Ejemplo 3: Exportación Masiva

```
URL: /reportes/exportar/?format=csv
```

**Resultado**: CSV con todos los eventos del sistema.

## 🎨 Personalización

### Modificar el Template del PDF

Edita el archivo:
```
templates/reports/pdf/traceability_report.html
```

El template usa CSS inline para el diseño. Puedes modificar:
- Colores (variables CSS)
- Fuentes
- Logo y branding
- Secciones del reporte

### Agregar Nuevos Tipos de Reportes

1. Crea un nuevo método en `PDFReportGenerator`
2. Crea un nuevo template HTML en `templates/reports/pdf/`
3. Agrega una vista en `apps/reports/views.py`
4. Agrega la ruta en `apps/reports/urls.py`
5. Agrega el botón en el dashboard

## 🚧 Próximas Funcionalidades

Las siguientes funcionalidades están planificadas según `docs/11_reportes.md`:

### Fase 3 - Exportación Avanzada
- [ ] Filtros avanzados en la interfaz web
- [ ] Reporte de aplicaciones fitosanitarias
- [ ] Reporte de cosecha

### Fase 4 - Análisis
- [ ] Balance hídrico
- [ ] Balance nutricional
- [ ] Análisis de tendencias
- [ ] Gráficos interactivos
- [ ] Dashboard de KPIs

### Fase 5 - Certificación
- [ ] Reporte de auditoría
- [ ] Registro BPA
- [ ] Firma digital
- [ ] Código QR de verificación

## 📞 Soporte

Para más información, consulta:
- Documentación completa: `docs/11_reportes.md`
- Código fuente: `apps/reports/`
- Templates: `templates/reports/`

## 🔒 Permisos

Todos los reportes requieren autenticación (`@login_required`).

Los permisos por rol se implementarán en futuras versiones según la matriz de permisos en `docs/11_reportes.md`.
