# Diseño de Base de Datos

[← Volver al índice](../README.md) | [← Modelo de Dominio](./04_modelo_dominio.md) | [API REST →](./06_api_rest.md)

## 1. Introducción

Este documento especifica el esquema físico de la base de datos PostgreSQL para **Green Flowers**, incluyendo tablas, índices, constraints y optimizaciones. El sistema utiliza una arquitectura de herencia Multi-Table donde cada tipo de evento especializado tiene su propia tabla que extiende la tabla base `events`.

## 2. Motor de Base de Datos

**PostgreSQL 15+**

**Razones de Selección**:

- ✅ Soporte de **herencia Multi-Table** (Django MTI)
- ✅ **Transacciones ACID** completas
- ✅ **Índices avanzados** para optimización de consultas
- ✅ **Maduro y estable**
- ✅ **Open source** (sin costos de licenciamiento)
- ✅ **Docker ready** para despliegue simplificado
- ✅ Soporte nativo de **UUID** y **JSONB**

## 3. Configuración Recomendada

```sql
-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- Para UUIDs
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- Para búsqueda de texto

-- Configuración de zona horaria
SET timezone = 'America/Mexico_City';
```

## 4. Esquema de Tablas

### 4.1 Tabla: fields (Campos)

Almacena lotes/parcelas de cultivo.

```sql
CREATE TABLE fields (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    surface_ha NUMERIC(10, 4) CHECK (surface_ha > 0),
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_fields_code ON fields(code);
CREATE INDEX idx_fields_is_active ON fields(is_active);

-- Trigger para updated_at
CREATE TRIGGER update_fields_updated_at
    BEFORE UPDATE ON fields
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comentarios
COMMENT ON TABLE fields IS 'Lotes o parcelas de cultivo de limón';
COMMENT ON COLUMN fields.id IS 'Identificador único UUID';
COMMENT ON COLUMN fields.name IS 'Nombre del campo';
COMMENT ON COLUMN fields.code IS 'Código único del campo';
COMMENT ON COLUMN fields.surface_ha IS 'Superficie en hectáreas';
COMMENT ON COLUMN fields.notes IS 'Notas adicionales';
COMMENT ON COLUMN fields.is_active IS 'Indica si el campo está activo';
```

### 4.2 Tabla: campaigns (Campañas)

Almacena campañas/temporadas de producción.

```sql
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    season VARCHAR(50),
    variety VARCHAR(100),
    start_date DATE NOT NULL,
    end_date DATE,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT check_campaign_dates CHECK (end_date IS NULL OR end_date >= start_date)
);

-- Índices
CREATE INDEX idx_campaigns_dates ON campaigns(start_date, end_date);
CREATE INDEX idx_campaigns_is_active ON campaigns(is_active);

-- Trigger
CREATE TRIGGER update_campaigns_updated_at
    BEFORE UPDATE ON campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE campaigns IS 'Campañas o temporadas de producción de limón';
COMMENT ON COLUMN campaigns.id IS 'Identificador único UUID';
COMMENT ON COLUMN campaigns.name IS 'Nombre de la campaña';
COMMENT ON COLUMN campaigns.season IS 'Temporada (ej: Primavera 2025)';
COMMENT ON COLUMN campaigns.variety IS 'Variedad de limón cultivada';
COMMENT ON COLUMN campaigns.start_date IS 'Fecha de inicio de la campaña';
COMMENT ON COLUMN campaigns.end_date IS 'Fecha de finalización de la campaña';
COMMENT ON COLUMN campaigns.notes IS 'Notas adicionales';
COMMENT ON COLUMN campaigns.is_active IS 'Indica si la campaña está activa';
COMMENT ON COLUMN campaigns.created_at IS 'Fecha de creación del registro';
COMMENT ON COLUMN campaigns.updated_at IS 'Fecha de última actualización';
```

### 4.3 Tabla: stations (Estaciones)

Estaciones de monitoreo de variables ambientales.

```sql
CREATE TABLE stations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    station_type VARCHAR(50) DEFAULT 'multivariable'
        CHECK (station_type IN ('clima', 'suelo', 'multivariable')),
    notes TEXT,
    is_operational BOOLEAN DEFAULT TRUE,
    installed_at DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_stations_field ON stations(field_id);
CREATE INDEX idx_stations_operational ON stations(is_operational);

-- Trigger
CREATE TRIGGER update_stations_updated_at
    BEFORE UPDATE ON stations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE stations IS 'Estaciones de monitoreo de variables ambientales';
COMMENT ON COLUMN stations.id IS 'Identificador único UUID';
COMMENT ON COLUMN stations.name IS 'Nombre de la estación';
COMMENT ON COLUMN stations.field_id IS 'Referencia al campo donde está instalada';
COMMENT ON COLUMN stations.station_type IS 'Tipo: clima, suelo o multivariable';
COMMENT ON COLUMN stations.notes IS 'Notas adicionales';
COMMENT ON COLUMN stations.is_operational IS 'Indica si la estación está operativa';
COMMENT ON COLUMN stations.installed_at IS 'Fecha de instalación';
COMMENT ON COLUMN stations.created_at IS 'Fecha de creación del registro';
COMMENT ON COLUMN stations.updated_at IS 'Fecha de última actualización';
```

### 4.4 Tabla: event_types (Tipos de Evento)

Define los tipos de eventos predefinidos del sistema con sus metadatos de visualización.

```sql
CREATE TABLE event_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    icon VARCHAR(50),       -- CSS class para icono (ej: 'bi-droplet')
    color VARCHAR(7),       -- Color hex (ej: #28a745)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT check_event_type_category CHECK (category IN (
        'irrigation', 'fertilization', 'phytosanitary', 'maintenance',
        'monitoring', 'harvest', 'postharvest', 'other'
    ))
);

-- Índices
CREATE INDEX idx_event_types_name ON event_types(name);
CREATE INDEX idx_event_types_category ON event_types(category);
CREATE INDEX idx_event_types_active ON event_types(is_active);

-- Trigger
CREATE TRIGGER update_event_types_updated_at
    BEFORE UPDATE ON event_types
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE event_types IS 'Definiciones de tipos de eventos del sistema';
COMMENT ON COLUMN event_types.id IS 'Identificador único autoincremental';
COMMENT ON COLUMN event_types.name IS 'Nombre del tipo de evento';
COMMENT ON COLUMN event_types.category IS 'Categoría del evento para agrupación';
COMMENT ON COLUMN event_types.description IS 'Descripción detallada del tipo de evento';
COMMENT ON COLUMN event_types.is_active IS 'Indica si el tipo de evento está activo';
COMMENT ON COLUMN event_types.icon IS 'Clase CSS de Bootstrap Icons';
COMMENT ON COLUMN event_types.color IS 'Color en formato hexadecimal';
COMMENT ON COLUMN event_types.created_at IS 'Fecha de creación del registro';
COMMENT ON COLUMN event_types.updated_at IS 'Fecha de última actualización';
```

**Los 10 tipos de eventos principales del sistema**:

1. Aplicación de Riego (irrigation)
2. Aplicación de Fertilizante (fertilization)
3. Aplicación Fitosanitaria (phytosanitary)
4. Labores de Cultivo (maintenance)
5. Monitoreo de Plagas (monitoring)
6. Brote de Plaga/Enfermedad (other)
7. Condiciones Climáticas (other)
8. Cosecha (harvest)
9. Almacenamiento Poscosecha (postharvest)
10. Mano de Obra y Costos (other)

### 4.5 Tabla: events (Eventos - Base)

Tabla base que contiene campos comunes a todos los eventos. Los eventos específicos extienden esta tabla mediante herencia Multi-Table de Django.

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type_id INT NOT NULL REFERENCES event_types(id) ON DELETE PROTECT,
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    observations TEXT,
    created_by_id UUID REFERENCES auth_user(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT check_event_timestamp CHECK (
        timestamp <= NOW() + INTERVAL '1 hour'
    )
);

-- Índices cruciales para rendimiento
CREATE INDEX idx_events_field_timestamp ON events(field_id, timestamp DESC);
CREATE INDEX idx_events_event_type ON events(event_type_id);
CREATE INDEX idx_events_campaign ON events(campaign_id);
CREATE INDEX idx_events_timestamp ON events(timestamp DESC);
CREATE INDEX idx_events_created_by ON events(created_by_id);

-- Índice parcial para eventos recientes (más consultados)
CREATE INDEX idx_events_recent ON events(timestamp DESC)
    WHERE timestamp > NOW() - INTERVAL '90 days';

-- Trigger
CREATE TRIGGER update_events_updated_at
    BEFORE UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE events IS 'Tabla base para todos los eventos de trazabilidad';
COMMENT ON COLUMN events.id IS 'Identificador único UUID';
COMMENT ON COLUMN events.event_type_id IS 'Referencia al tipo de evento';
COMMENT ON COLUMN events.field_id IS 'Referencia al campo donde ocurrió el evento';
COMMENT ON COLUMN events.campaign_id IS 'Referencia a la campaña asociada (opcional)';
COMMENT ON COLUMN events.timestamp IS 'Fecha y hora cuando ocurrió el evento';
COMMENT ON COLUMN events.observations IS 'Observaciones generales del evento';
COMMENT ON COLUMN events.created_by_id IS 'Usuario que registró el evento';
COMMENT ON COLUMN events.created_at IS 'Fecha de creación del registro';
COMMENT ON COLUMN events.updated_at IS 'Fecha de última actualización';
```

### 4.6 Tablas Específicas de Eventos

Django utiliza herencia Multi-Table (MTI) donde cada tabla específica tiene su propia clave primaria que es una clave foránea a la tabla padre `events`. Cada evento específico extiende el modelo base agregando campos especializados.

#### 4.6.1 irrigation_events (Eventos de Riego)

```sql
CREATE TABLE irrigation_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    metodo VARCHAR(50) NOT NULL CHECK (metodo IN (
        'Aspersión', 'Goteo', 'Surco', 'Pivote', 'Manual', 'Microaspersión'
    )),
    duracion_minutos INT NOT NULL CHECK (duracion_minutos > 0),
    fuente_agua VARCHAR(50) NOT NULL CHECK (fuente_agua IN (
        'Pozo', 'Río', 'Presa', 'Red municipal', 'Otro'
    )),
    volumen_m3 NUMERIC(10, 2) CHECK (volumen_m3 >= 0),
    presion_bar NUMERIC(5, 2) CHECK (presion_bar BETWEEN 0 AND 10),
    ce_uScm NUMERIC(8, 2) CHECK (ce_uScm >= 0),
    ph NUMERIC(4, 2) CHECK (ph BETWEEN 0 AND 14)
);

CREATE INDEX idx_irrigation_metodo ON irrigation_events(metodo);
COMMENT ON TABLE irrigation_events IS 'Eventos de aplicación de riego';
COMMENT ON COLUMN irrigation_events.metodo IS 'Método de riego utilizado';
COMMENT ON COLUMN irrigation_events.duracion_minutos IS 'Duración del riego en minutos';
COMMENT ON COLUMN irrigation_events.fuente_agua IS 'Fuente de agua utilizada';
COMMENT ON COLUMN irrigation_events.volumen_m3 IS 'Volumen de agua en metros cúbicos';
COMMENT ON COLUMN irrigation_events.presion_bar IS 'Presión del sistema en bares';
COMMENT ON COLUMN irrigation_events.ce_uScm IS 'Conductividad eléctrica en µS/cm';
COMMENT ON COLUMN irrigation_events.ph IS 'pH del agua de riego';
```

#### 4.6.2 fertilization_events (Eventos de Fertilización)

```sql
CREATE TABLE fertilization_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    producto VARCHAR(200) NOT NULL,
    metodo_aplicacion VARCHAR(50) NOT NULL CHECK (metodo_aplicacion IN (
        'Foliar', 'Fertirriego', 'Edáfica', 'Inyección'
    )),
    dosis NUMERIC(10, 2) NOT NULL CHECK (dosis > 0),
    unidad_dosis VARCHAR(20) DEFAULT 'kg/ha',
    n_porcentaje NUMERIC(5, 2) CHECK (n_porcentaje BETWEEN 0 AND 100),
    p_porcentaje NUMERIC(5, 2) CHECK (p_porcentaje BETWEEN 0 AND 100),
    k_porcentaje NUMERIC(5, 2) CHECK (k_porcentaje BETWEEN 0 AND 100),
    volumen_caldo_l NUMERIC(10, 2) CHECK (volumen_caldo_l >= 0)
);

CREATE INDEX idx_fertilization_producto ON fertilization_events(producto);
CREATE INDEX idx_fertilization_metodo ON fertilization_events(metodo_aplicacion);
COMMENT ON TABLE fertilization_events IS 'Eventos de aplicación de fertilizantes';
COMMENT ON COLUMN fertilization_events.producto IS 'Nombre comercial del fertilizante';
COMMENT ON COLUMN fertilization_events.n_porcentaje IS 'Porcentaje de Nitrógeno (N)';
COMMENT ON COLUMN fertilization_events.p_porcentaje IS 'Porcentaje de Fósforo (P)';
COMMENT ON COLUMN fertilization_events.k_porcentaje IS 'Porcentaje de Potasio (K)';
```

#### 4.6.3 phytosanitary_events (Eventos Fitosanitarios)

```sql
CREATE TABLE phytosanitary_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    producto VARCHAR(200) NOT NULL,
    ingrediente_activo VARCHAR(200),
    tipo_producto VARCHAR(50) NOT NULL CHECK (tipo_producto IN (
        'Insecticida', 'Fungicida', 'Herbicida', 'Acaricida',
        'Nematicida', 'Bactericida', 'Coadyuvante'
    )),
    objetivo VARCHAR(200) NOT NULL,
    metodo_aplicacion VARCHAR(50) NOT NULL CHECK (metodo_aplicacion IN (
        'Mochila manual', 'Mochila motorizada', 'Tractor', 'Dron',
        'Avión', 'Fertirrigación', 'Inyección al tronco'
    )),
    dosis NUMERIC(10, 2) NOT NULL CHECK (dosis > 0),
    unidad_dosis VARCHAR(20) DEFAULT 'L/ha',
    lote_producto VARCHAR(100),
    volumen_caldo_l NUMERIC(10, 2) CHECK (volumen_caldo_l >= 0),
    presion_bar NUMERIC(5, 2) CHECK (presion_bar >= 0),
    intervalo_seguridad_dias INT CHECK (intervalo_seguridad_dias >= 0),
    responsable_aplicacion VARCHAR(200),
    eficacia_observada VARCHAR(20) CHECK (eficacia_observada IN (
        'No evaluada', 'Muy baja', 'Baja', 'Media', 'Alta', 'Muy alta'
    )),
    fitotoxicidad BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_phytosanitary_tipo ON phytosanitary_events(tipo_producto);
CREATE INDEX idx_phytosanitary_objetivo ON phytosanitary_events(objetivo);
COMMENT ON TABLE phytosanitary_events IS 'Eventos de aplicación de productos fitosanitarios';
COMMENT ON COLUMN phytosanitary_events.objetivo IS 'Plaga, enfermedad o maleza objetivo';
COMMENT ON COLUMN phytosanitary_events.intervalo_seguridad_dias IS 'Días de espera antes de cosecha';
COMMENT ON COLUMN phytosanitary_events.fitotoxicidad IS 'Indica si se observó daño a las plantas';
```

#### 4.6.4 maintenance_events (Eventos de Labores de Cultivo)

```sql
CREATE TABLE maintenance_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    actividad VARCHAR(100) NOT NULL CHECK (actividad IN (
        'Poda', 'Deshierbe', 'Entutorado', 'Aclareo de frutos', 'Despunte',
        'Cobertura vegetal', 'Desbrote', 'Raleo', 'Limpieza de canales',
        'Reparación de sistema de riego'
    )),
    horas_hombre NUMERIC(10, 2) NOT NULL CHECK (horas_hombre >= 0),
    herramienta_equipo VARCHAR(200),
    numero_jornales INT CHECK (numero_jornales >= 1),
    objetivo TEXT,
    porcentaje_completado NUMERIC(5, 2) CHECK (porcentaje_completado BETWEEN 0 AND 100),
    herramientas_desinfectadas BOOLEAN
);

CREATE INDEX idx_maintenance_actividad ON maintenance_events(actividad);
COMMENT ON TABLE maintenance_events IS 'Eventos de labores de cultivo (poda, deshierbe, etc.)';
COMMENT ON COLUMN maintenance_events.horas_hombre IS 'Total de horas-hombre invertidas';
COMMENT ON COLUMN maintenance_events.numero_jornales IS 'Cantidad de trabajadores';
```

#### 4.6.5 monitoring_events (Eventos de Monitoreo)

```sql
CREATE TABLE monitoring_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    plaga_enfermedad VARCHAR(200) NOT NULL,
    metodo_muestreo VARCHAR(50) NOT NULL CHECK (metodo_muestreo IN (
        'Visual directa', 'Trampa adhesiva', 'Trampa de luz',
        'Muestreo de suelo', 'Muestreo foliar', 'Otro'
    )),
    incidencia VARCHAR(20) NOT NULL CHECK (incidencia IN (
        'Muy baja', 'Baja', 'Media', 'Alta', 'Muy alta'
    )),
    severidad VARCHAR(20) CHECK (severidad IN (
        'Muy baja', 'Baja', 'Media', 'Alta', 'Muy alta'
    )),
    ubicacion_campo VARCHAR(200),
    numero_muestras INT CHECK (numero_muestras >= 1),
    accion_recomendada TEXT
);

CREATE INDEX idx_monitoring_plaga ON monitoring_events(plaga_enfermedad);
CREATE INDEX idx_monitoring_incidencia ON monitoring_events(incidencia);
COMMENT ON TABLE monitoring_events IS 'Eventos de monitoreo de plagas y enfermedades';
COMMENT ON COLUMN monitoring_events.incidencia IS 'Porcentaje o nivel de plantas afectadas';
COMMENT ON COLUMN monitoring_events.severidad IS 'Nivel de daño en plantas afectadas';
```

#### 4.6.6 outbreak_events (Eventos de Brotes)

```sql
CREATE TABLE outbreak_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    tipo_problema VARCHAR(200) NOT NULL,
    severidad VARCHAR(20) NOT NULL CHECK (severidad IN (
        'Baja', 'Media', 'Alta', 'Crítica'
    )),
    metodo_deteccion VARCHAR(50) NOT NULL CHECK (metodo_deteccion IN (
        'Monitoreo rutinario', 'Inspección visual', 'Síntomas observados',
        'Reporte de trabajador', 'Análisis de laboratorio', 'Otro'
    )),
    area_afectada_ha NUMERIC(10, 4) CHECK (area_afectada_ha >= 0),
    porcentaje_afectacion NUMERIC(5, 2) CHECK (porcentaje_afectacion BETWEEN 0 AND 100),
    accion_inmediata TEXT,
    requiere_tratamiento BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_outbreak_severidad ON outbreak_events(severidad);
CREATE INDEX idx_outbreak_tipo ON outbreak_events(tipo_problema);
COMMENT ON TABLE outbreak_events IS 'Eventos de brotes de plagas y enfermedades';
COMMENT ON COLUMN outbreak_events.tipo_problema IS 'Tipo de plaga o enfermedad detectada';
COMMENT ON COLUMN outbreak_events.requiere_tratamiento IS 'Indica si requiere intervención química';
```

#### 4.6.7 climate_events (Eventos Climáticos)

```sql
CREATE TABLE climate_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    temperatura_max NUMERIC(5, 2) NOT NULL CHECK (temperatura_max BETWEEN -20 AND 50),
    temperatura_min NUMERIC(5, 2) NOT NULL CHECK (temperatura_min BETWEEN -20 AND 50),
    humedad_relativa NUMERIC(5, 2) CHECK (humedad_relativa BETWEEN 0 AND 100),
    precipitacion_mm NUMERIC(8, 2) CHECK (precipitacion_mm >= 0),
    velocidad_viento_ms NUMERIC(5, 2) CHECK (velocidad_viento_ms >= 0),
    viento VARCHAR(20) CHECK (viento IN (
        'Sin viento', 'Viento leve', 'Viento moderado', 'Viento fuerte'
    )),
    radiacion_solar_wm2 NUMERIC(8, 2) CHECK (radiacion_solar_wm2 >= 0)
);

CREATE INDEX idx_climate_fecha ON climate_events(event_ptr_id);
COMMENT ON TABLE climate_events IS 'Eventos de condiciones climáticas';
COMMENT ON COLUMN climate_events.temperatura_max IS 'Temperatura máxima en °C';
COMMENT ON COLUMN climate_events.temperatura_min IS 'Temperatura mínima en °C';
COMMENT ON COLUMN climate_events.precipitacion_mm IS 'Precipitación en milímetros';
COMMENT ON COLUMN climate_events.velocidad_viento_ms IS 'Velocidad del viento en m/s';
COMMENT ON COLUMN climate_events.radiacion_solar_wm2 IS 'Radiación solar en W/m²';
```

#### 4.6.8 harvest_events (Eventos de Cosecha)

```sql
CREATE TABLE harvest_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    variedad VARCHAR(100),
    volumen_kg NUMERIC(12, 2) NOT NULL CHECK (volumen_kg > 0),
    rendimiento_kg_ha NUMERIC(10, 2) NOT NULL CHECK (rendimiento_kg_ha > 0),
    calidad VARCHAR(20) CHECK (calidad IN (
        'exportacion', 'primera', 'segunda', 'tercera'
    )),
    numero_trabajadores INT CHECK (numero_trabajadores >= 1),
    horas_trabajo NUMERIC(8, 2) CHECK (horas_trabajo >= 0),
    fecha_inicio DATE,
    fecha_fin DATE
);

CREATE INDEX idx_harvest_calidad ON harvest_events(calidad);
CREATE INDEX idx_harvest_variedad ON harvest_events(variedad);
COMMENT ON TABLE harvest_events IS 'Eventos de cosecha de limón';
COMMENT ON COLUMN harvest_events.volumen_kg IS 'Volumen total cosechado en kilogramos';
COMMENT ON COLUMN harvest_events.rendimiento_kg_ha IS 'Rendimiento por hectárea';
COMMENT ON COLUMN harvest_events.calidad IS 'Clasificación de calidad del producto';
```

#### 4.6.9 postharvest_events (Eventos Poscosecha)

```sql
CREATE TABLE postharvest_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    producto VARCHAR(200) NOT NULL,
    cantidad_kg NUMERIC(12, 2) NOT NULL CHECK (cantidad_kg > 0),
    temperatura NUMERIC(5, 2) NOT NULL CHECK (temperatura BETWEEN -5 AND 30),
    humedad NUMERIC(5, 2) NOT NULL CHECK (humedad BETWEEN 0 AND 100),
    tipo_almacenamiento VARCHAR(100),
    fecha_ingreso DATE,
    fecha_salida_prevista DATE,
    condiciones_observadas TEXT
);

CREATE INDEX idx_postharvest_producto ON postharvest_events(producto);
CREATE INDEX idx_postharvest_fechas ON postharvest_events(fecha_ingreso, fecha_salida_prevista);
COMMENT ON TABLE postharvest_events IS 'Eventos de almacenamiento poscosecha';
COMMENT ON COLUMN postharvest_events.temperatura IS 'Temperatura de almacenamiento en °C';
COMMENT ON COLUMN postharvest_events.humedad IS 'Humedad relativa en %';
```

#### 4.6.10 labor_cost_events (Eventos de Mano de Obra)

```sql
CREATE TABLE labor_cost_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    actividad VARCHAR(100) NOT NULL CHECK (actividad IN (
        'Riego', 'Fertilización', 'Aplicación fitosanitaria', 'Poda',
        'Deshierbe', 'Cosecha', 'Mantenimiento', 'Transporte', 'Otra'
    )),
    numero_trabajadores INT NOT NULL CHECK (numero_trabajadores >= 1),
    horas_trabajo NUMERIC(8, 2) CHECK (horas_trabajo >= 0),
    costo_hora NUMERIC(10, 2) CHECK (costo_hora >= 0),
    costo_total NUMERIC(12, 2) NOT NULL CHECK (costo_total >= 0)
);

CREATE INDEX idx_labor_actividad ON labor_cost_events(actividad);
CREATE INDEX idx_labor_fecha ON labor_cost_events(event_ptr_id);
COMMENT ON TABLE labor_cost_events IS 'Eventos de mano de obra y costos laborales';
COMMENT ON COLUMN labor_cost_events.costo_total IS 'Costo total de la actividad en moneda local';
COMMENT ON COLUMN labor_cost_events.costo_hora IS 'Costo por hora de trabajo';
```

### 4.7 Tabla: attachments (Adjuntos)

Archivos adjuntos a eventos (imágenes, PDFs, documentos, etc.).

```sql
CREATE TABLE attachments (
    id BIGSERIAL PRIMARY KEY,
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    file VARCHAR(500) NOT NULL,  -- Ruta del archivo (Django FileField)
    file_name VARCHAR(255) NOT NULL,
    file_size INT CHECK (file_size > 0 AND file_size <= 10485760),  -- Max 10MB
    mime_type VARCHAR(100) NOT NULL,
    metadata JSONB,
    uploaded_by_id UUID REFERENCES auth_user(id) ON DELETE SET NULL,
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_attachments_event ON attachments(event_id);
CREATE INDEX idx_attachments_uploaded_at ON attachments(uploaded_at DESC);
CREATE INDEX idx_attachments_mime_type ON attachments(mime_type);

COMMENT ON TABLE attachments IS 'Archivos adjuntos a eventos (fotos, PDFs, documentos, etc.)';
COMMENT ON COLUMN attachments.id IS 'Identificador único autoincremental';
COMMENT ON COLUMN attachments.event_id IS 'Referencia al evento asociado';
COMMENT ON COLUMN attachments.file IS 'Ruta del archivo gestionada por Django FileField';
COMMENT ON COLUMN attachments.file_name IS 'Nombre original del archivo';
COMMENT ON COLUMN attachments.file_size IS 'Tamaño en bytes, máximo 10MB';
COMMENT ON COLUMN attachments.mime_type IS 'Tipo MIME del archivo (image/jpeg, application/pdf, etc.)';
COMMENT ON COLUMN attachments.metadata IS 'Metadatos adicionales del archivo en formato JSON';
COMMENT ON COLUMN attachments.uploaded_by_id IS 'Usuario que subió el archivo';
COMMENT ON COLUMN attachments.uploaded_at IS 'Fecha y hora de carga del archivo';
```

### 4.8 Tabla: variables (Variables Ambientales)

Variables ambientales/IoT medidas en estaciones o campos.

```sql
CREATE TABLE variables (
    id BIGSERIAL PRIMARY KEY,
    station_id UUID REFERENCES stations(id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    variable_type VARCHAR(50) NOT NULL CHECK (variable_type IN (
        'soil_moisture', 'soil_temp', 'soil_ec', 'soil_ph',
        'air_temp', 'humidity', 'precipitation', 'wind_speed',
        'solar_radiation', 'ndvi', 'ndre'
    )),
    value NUMERIC(12, 4) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    source VARCHAR(20) DEFAULT 'manual' CHECK (source IN ('manual', 'automatic')),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT check_variable_location CHECK (
        station_id IS NOT NULL OR field_id IS NOT NULL
    )
);

-- Índices optimizados para time-series
CREATE INDEX idx_variables_station_timestamp ON variables(station_id, timestamp DESC);
CREATE INDEX idx_variables_field_timestamp ON variables(field_id, timestamp DESC);
CREATE INDEX idx_variables_type_timestamp ON variables(variable_type, timestamp DESC);
CREATE INDEX idx_variables_timestamp ON variables(timestamp DESC);

-- Índice parcial para datos recientes (más consultados)
CREATE INDEX idx_variables_recent ON variables(timestamp DESC)
    WHERE timestamp > NOW() - INTERVAL '30 days';

COMMENT ON TABLE variables IS 'Mediciones de variables ambientales e IoT';
COMMENT ON COLUMN variables.id IS 'Identificador único autoincremental';
COMMENT ON COLUMN variables.station_id IS 'Referencia a la estación de monitoreo (opcional)';
COMMENT ON COLUMN variables.field_id IS 'Referencia al campo (opcional si hay estación)';
COMMENT ON COLUMN variables.timestamp IS 'Fecha y hora de la medición';
COMMENT ON COLUMN variables.variable_type IS 'Tipo de variable medida';
COMMENT ON COLUMN variables.value IS 'Valor numérico de la medición';
COMMENT ON COLUMN variables.unit IS 'Unidad de medida';
COMMENT ON COLUMN variables.source IS 'Fuente de datos: manual o automática';
COMMENT ON COLUMN variables.metadata IS 'Metadatos adicionales en formato JSON';
COMMENT ON COLUMN variables.created_at IS 'Fecha de creación del registro';
```

**Tipos de Variable Soportados**:

- `soil_moisture`: Humedad del Suelo (%)
- `soil_temp`: Temperatura del Suelo (°C)
- `soil_ec`: CE del Suelo (µS/cm)
- `soil_ph`: pH del Suelo
- `air_temp`: Temperatura del Aire (°C)
- `humidity`: Humedad Relativa (%)
- `precipitation`: Precipitación (mm)
- `wind_speed`: Velocidad del Viento (m/s)
- `solar_radiation`: Radiación Solar (W/m²)
- `ndvi`: NDVI (Índice de Vegetación)
- `ndre`: NDRE (Índice de Clorofila)

### 4.9 Tabla: auth_user (Usuarios)

Django gestiona la autenticación mediante las tablas `auth_user`, `auth_group` y `auth_permission`. El sistema utiliza UUID como clave primaria personalizada.

```sql
CREATE TABLE auth_user (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMPTZ,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    email VARCHAR(254),
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_auth_user_username ON auth_user(username);
CREATE INDEX idx_auth_user_email ON auth_user(email);

COMMENT ON TABLE auth_user IS 'Usuarios del sistema (tabla de Django)';
COMMENT ON COLUMN auth_user.id IS 'Identificador único UUID';
COMMENT ON COLUMN auth_user.password IS 'Contraseña hasheada';
COMMENT ON COLUMN auth_user.last_login IS 'Fecha y hora del último inicio de sesión';
COMMENT ON COLUMN auth_user.is_superuser IS 'Indica si el usuario es superusuario';
COMMENT ON COLUMN auth_user.username IS 'Nombre de usuario único';
COMMENT ON COLUMN auth_user.first_name IS 'Nombre(s) del usuario';
COMMENT ON COLUMN auth_user.last_name IS 'Apellido(s) del usuario';
COMMENT ON COLUMN auth_user.email IS 'Correo electrónico';
COMMENT ON COLUMN auth_user.is_staff IS 'Indica si tiene acceso al panel de administración';
COMMENT ON COLUMN auth_user.is_active IS 'Indica si la cuenta está activa';
COMMENT ON COLUMN auth_user.date_joined IS 'Fecha de registro en el sistema';
```

### 4.10 Tabla: user_profiles (Perfiles de Usuario)

Extensión del perfil de usuario con información adicional y roles.

```sql
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN (
        'ADMIN', 'SUPERVISOR', 'FIELD_TECH', 'CONSULTANT', 'INTEGRATION'
    )),
    phone VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_user_profiles_user ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_role ON user_profiles(role);

-- Trigger
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE user_profiles IS 'Extensión de perfil de usuario con rol y datos adicionales';
COMMENT ON COLUMN user_profiles.id IS 'Identificador único autoincremental';
COMMENT ON COLUMN user_profiles.user_id IS 'Referencia al usuario de Django';
COMMENT ON COLUMN user_profiles.role IS 'Rol del usuario en el sistema';
COMMENT ON COLUMN user_profiles.phone IS 'Número telefónico';
COMMENT ON COLUMN user_profiles.notes IS 'Notas adicionales';
COMMENT ON COLUMN user_profiles.created_at IS 'Fecha de creación del registro';
COMMENT ON COLUMN user_profiles.updated_at IS 'Fecha de última actualización';
```

**Roles disponibles**:

- `ADMIN`: Administrador del sistema
- `SUPERVISOR`: Supervisor de campo
- `FIELD_TECH`: Técnico de campo
- `CONSULTANT`: Consultor externo
- `INTEGRATION`: Usuario de integración (API)

### 4.11 Tabla: audit_logs (Auditoría)

Registro de auditoría de operaciones del sistema.

```sql
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth_user(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    entity VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    diff JSONB,  -- Cambios antes/después

    CONSTRAINT check_audit_action CHECK (action IN (
        'CREATE_EVENT', 'UPDATE_EVENT', 'DELETE_EVENT',
        'CREATE_FIELD', 'UPDATE_FIELD', 'DELETE_FIELD',
        'CREATE_CAMPAIGN', 'UPDATE_CAMPAIGN',
        'CREATE_EVENT_TYPE', 'UPDATE_EVENT_TYPE',
        'API_READ', 'API_WRITE',
        'LOGIN', 'LOGOUT', 'LOGIN_FAILED',
        'EXPORT_REPORT'
    ))
);

-- Índices
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity, entity_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

COMMENT ON TABLE audit_logs IS 'Registro de auditoría de operaciones';
COMMENT ON COLUMN audit_logs.id IS 'Identificador único autoincremental';
COMMENT ON COLUMN audit_logs.user_id IS 'Usuario que realizó la operación';
COMMENT ON COLUMN audit_logs.action IS 'Tipo de acción realizada';
COMMENT ON COLUMN audit_logs.entity IS 'Tipo de entidad afectada (tabla/modelo)';
COMMENT ON COLUMN audit_logs.entity_id IS 'Identificador de la entidad afectada';
COMMENT ON COLUMN audit_logs.timestamp IS 'Fecha y hora de la operación';
COMMENT ON COLUMN audit_logs.ip_address IS 'Dirección IP desde donde se realizó la operación';
COMMENT ON COLUMN audit_logs.user_agent IS 'User-Agent del navegador/cliente';
COMMENT ON COLUMN audit_logs.diff IS 'Diferencia JSON antes/después del cambio';
```

## 5. Funciones y Triggers

### 5.1 Función: Actualización Automática de updated_at

Función PostgreSQL para actualizar automáticamente el campo `updated_at` en cada UPDATE.

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_updated_at_column() IS 'Actualiza automáticamente updated_at al modificar registros';
```

Esta función se aplica mediante triggers en las siguientes tablas:

- `fields`
- `campaigns`
- `stations`
- `event_types`
- `events`
- `user_profiles`

## 6. Vistas Útiles

### 6.1 Vista: v_events_full (Eventos con Información Completa)

Vista desnormalizada que une eventos con su información relacionada.

```sql
CREATE VIEW v_events_full AS
SELECT
    e.id,
    e.timestamp,
    et.name AS tipo_evento,
    et.category AS categoria,
    et.icon AS icono,
    et.color AS color,
    f.name AS campo_nombre,
    f.code AS campo_codigo,
    f.surface_ha AS campo_superficie_ha,
    c.name AS campana_nombre,
    c.season AS campana_temporada,
    e.observations AS observaciones,
    u.username AS creado_por,
    u.first_name || ' ' || u.last_name AS nombre_completo_usuario,
    e.created_at AS fecha_registro,
    e.updated_at AS fecha_actualizacion,
    (SELECT COUNT(*) FROM attachments WHERE event_id = e.id) AS num_adjuntos
FROM events e
JOIN event_types et ON e.event_type_id = et.id
JOIN fields f ON e.field_id = f.id
LEFT JOIN campaigns c ON e.campaign_id = c.id
LEFT JOIN auth_user u ON e.created_by_id = u.id;

COMMENT ON VIEW v_events_full IS 'Vista desnormalizada de eventos con información completa';
```

### 6.2 Vista: v_latest_variables (Variables Recientes por Estación)

Última lectura de cada tipo de variable por estación.

```sql
CREATE VIEW v_latest_variables AS
SELECT DISTINCT ON (station_id, variable_type)
    v.id,
    v.station_id,
    v.field_id,
    v.timestamp,
    v.variable_type,
    v.value,
    v.unit,
    v.source,
    s.name AS estacion_nombre,
    s.station_type AS tipo_estacion,
    f.name AS campo_nombre,
    f.code AS campo_codigo
FROM variables v
LEFT JOIN stations s ON v.station_id = s.id
LEFT JOIN fields f ON v.field_id = f.id OR f.id = s.field_id
ORDER BY station_id, variable_type, timestamp DESC;

COMMENT ON VIEW v_latest_variables IS 'Última lectura de cada variable por estación';
```

### 6.3 Vista: v_event_summary_by_field (Resumen de Eventos por Campo)

Resumen estadístico de eventos agrupados por campo y categoría.

```sql
CREATE VIEW v_event_summary_by_field AS
SELECT
    f.id AS campo_id,
    f.name AS campo_nombre,
    f.code AS campo_codigo,
    et.category AS categoria_evento,
    et.name AS tipo_evento,
    COUNT(*) AS total_eventos,
    MAX(e.timestamp) AS ultimo_evento,
    MIN(e.timestamp) AS primer_evento
FROM fields f
LEFT JOIN events e ON f.id = e.field_id
LEFT JOIN event_types et ON e.event_type_id = et.id
GROUP BY f.id, f.name, f.code, et.category, et.name
ORDER BY f.name, et.category;

COMMENT ON VIEW v_event_summary_by_field IS 'Resumen estadístico de eventos por campo y categoría';
```

### 6.4 Vista: v_harvest_summary (Resumen de Cosechas)

Resumen de cosechas por campo y campaña.

```sql
CREATE VIEW v_harvest_summary AS
SELECT
    f.id AS campo_id,
    f.name AS campo_nombre,
    c.id AS campana_id,
    c.name AS campana_nombre,
    c.season AS temporada,
    COUNT(h.event_ptr_id) AS num_cosechas,
    SUM(h.volumen_kg) AS volumen_total_kg,
    AVG(h.rendimiento_kg_ha) AS rendimiento_promedio_kg_ha,
    MIN(e.timestamp) AS fecha_primera_cosecha,
    MAX(e.timestamp) AS fecha_ultima_cosecha
FROM fields f
LEFT JOIN events e ON f.id = e.field_id
LEFT JOIN harvest_events h ON e.id = h.event_ptr_id
LEFT JOIN campaigns c ON e.campaign_id = c.id
WHERE h.event_ptr_id IS NOT NULL
GROUP BY f.id, f.name, c.id, c.name, c.season
ORDER BY f.name, c.start_date DESC;

COMMENT ON VIEW v_harvest_summary IS 'Resumen de cosechas por campo y campaña';
```

FROM fields f
LEFT JOIN events e ON f.id = e.field_id
LEFT JOIN event_types et ON e.event_type_id = et.id
GROUP BY f.id, f.name, et.category;

COMMENT ON VIEW v_event_summary_by_field IS 'Resumen de eventos por lote y categoría';

````

## 7. Políticas de Seguridad a Nivel de BD

### 7.1 Row Level Security (RLS) - Opcional

Si se implementa multi-tenancy:

```sql
ALTER TABLE fields ENABLE ROW LEVEL SECURITY;

CREATE POLICY field_access_policy ON fields
    USING (organization_id = current_setting('app.current_organization_id')::INT);
````

### 7.2 Roles de BD

```sql
-- Rol para la aplicación (Django)
CREATE ROLE traceability_app WITH LOGIN PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE traceability TO traceability_app;
GRANT USAGE ON SCHEMA public TO traceability_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO traceability_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO traceability_app;

-- Rol de solo lectura (para reportes)
CREATE ROLE traceability_readonly WITH LOGIN PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE traceability TO traceability_readonly;
GRANT USAGE ON SCHEMA public TO traceability_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO traceability_readonly;
```

## 8. Estrategias de Optimización

### 8.1 Particionamiento

**Tabla `events`** - Por rango de timestamp (anual o mensual):

```sql
-- Crear tabla padre como particionada
CREATE TABLE events_partitioned (
    LIKE events INCLUDING ALL
) PARTITION BY RANGE (timestamp);

-- Crear particiones por año
CREATE TABLE events_2025 PARTITION OF events_partitioned
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE events_2026 PARTITION OF events_partitioned
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
```

**Beneficios**:

- Consultas más rápidas (prune de particiones)
- Mantenimiento más simple (DROP particiones antiguas)
- Backups más eficientes

### 8.2 Índices Especializados

**Índice para búsqueda de texto**:

```sql
CREATE INDEX idx_fields_name_trgm ON fields USING GIN(name gin_trgm_ops);
CREATE INDEX idx_events_observations_trgm ON events USING GIN(observations gin_trgm_ops);
```

**Índice para consultas específicas en JSONB**:

```sql
-- Consultar eventos por método de riego
CREATE INDEX idx_events_riego_metodo ON events
    USING BTREE ((payload->>'metodo'))
    WHERE event_type_id = 1;  -- ID del tipo "Riego"
```

### 8.3 Mantenimiento Automatizado

```sql
-- Configurar autovacuum agresivo para tablas de alta escritura
ALTER TABLE variables SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);

ALTER TABLE audit_logs SET (
    autovacuum_vacuum_scale_factor = 0.05
);
```

## 9. Backup y Recuperación

### 9.1 Estrategia de Backup

```bash
# Backup diario completo
pg_dump -Fc -h localhost -U postgres traceability > backup_$(date +%Y%m%d).dump

# Backup solo de esquema
pg_dump -s -h localhost -U postgres traceability > schema_$(date +%Y%m%d).sql

# Backup solo de datos
pg_dump -a -h localhost -U postgres traceability > data_$(date +%Y%m%d).sql
```

### 9.2 Recuperación

```bash
# Restaurar desde backup
pg_restore -h localhost -U postgres -d traceability_restore backup_20251013.dump

# Restaurar desde SQL
psql -h localhost -U postgres -d traceability < backup_20251013.sql
```

### 9.3 Point-in-Time Recovery (PITR)

Habilitar WAL archiving en `postgresql.conf`:

```ini
wal_level = replica
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/wal_archive/%f'
```

## 10. Estimación de Tamaño

### 10.1 Proyección de Crecimiento

**Supuestos**:

- 20 lotes
- 200 eventos/año por lote = 4,000 eventos/año
- 50 variables/día = 18,250 variables/año
- 5 años de operación

| Tabla             | Filas (5 años) | Tamaño Estimado                     |
| ----------------- | -------------- | ----------------------------------- |
| fields            | 20             | < 1 MB                              |
| campaigns         | 25             | < 1 MB                              |
| stations          | 40             | < 1 MB                              |
| event_types       | 50             | < 1 MB                              |
| events            | 20,000         | ~50 MB                              |
| attachments       | 10,000         | ~5 GB (archivos) + 10 MB (metadata) |
| variables         | 91,250         | ~20 MB                              |
| audit_logs        | 50,000         | ~30 MB                              |
| **Total BD**      |                | **~120 MB**                         |
| **Total Storage** |                | **~5.1 GB**                         |

**Nota**: El mayor consumo es de archivos adjuntos.

---

**Siguiente**: [Especificación de API REST →](./06_api_rest.md)

[← Volver al índice](../README.md)
