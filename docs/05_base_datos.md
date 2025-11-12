# Diseño de Base de Datos

[← Volver al índice](../README.md) | [← Modelo de Dominio](./04_modelo_dominio.md) | [API REST →](./06_api_rest.md)

## 1. Introducción

Este documento especifica el esquema físico de la base de datos PostgreSQL, incluyendo tablas, índices, constraints y optimizaciones. El sistema utiliza una arquitectura de herencia de tablas donde cada tipo de evento tiene su propia tabla que hereda de la tabla base `events`.

## 2. Motor de Base de Datos

**PostgreSQL 15+**

**Razones de Selección**:
- ✅ Soporte de **herencia de tablas** (Table Inheritance)
- ✅ **Transacciones ACID** completas
- ✅ **Índices avanzados** para optimización de consultas
- ✅ **Maduro y estable**
- ✅ **Open source** (sin costos de licenciamiento)
- ✅ **Docker ready** para despliegue simplificado

## 3. Configuración Recomendada

```sql
-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- Para UUIDs
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- Para búsqueda de texto

-- Configuración de zona horaria
SET timezone = 'America/Mexico_City';
```

## 4. Esquema de Tablas

### 4.1 Tabla: fields

Almacena lotes/parcelas.

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
COMMENT ON TABLE fields IS 'Lotes o parcelas de cultivo';
```

### 4.2 Tabla: campaigns

Almacena campañas/temporadas.

```sql
CREATE TABLE campaigns (
    id SERIAL PRIMARY KEY,
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

COMMENT ON TABLE campaigns IS 'Campañas o temporadas de producción';
```

### 4.3 Tabla: stations

Estaciones de monitoreo.

```sql
CREATE TABLE stations (
    id SERIAL PRIMARY KEY,
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
```

### 4.4 Tabla: event_types

Definición de tipos de evento predefinidos (10 tipos fijos con metadatos).

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

COMMENT ON TABLE event_types IS 'Definiciones de tipos de eventos predefinidos (10 tipos fijos)';
```

**Los 10 tipos de eventos predefinidos**:
1. Aplicación de Riego (irrigation)
2. Fertilización (fertilization)
3. Aplicación Fitosanitaria (phytosanitary)
4. Labores de Cultivo (maintenance)
5. Monitoreo (monitoring)
6. Brotes y Plagas (other)
7. Eventos Climáticos (other)
8. Cosecha (harvest)
9. Poscosecha (postharvest)
10. Mano de Obra y Costos (other)

### 4.5 Tabla: events (Base)

Tabla base que contiene campos comunes a todos los eventos. Las tablas específicas heredan de esta.

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type_id INT NOT NULL REFERENCES event_types(id) ON DELETE PROTECT,
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    campaign_id INT REFERENCES campaigns(id) ON DELETE SET NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    observations TEXT,
    created_by_id INT REFERENCES auth_user(id) ON DELETE SET NULL,
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

-- Trigger
CREATE TRIGGER update_events_updated_at
    BEFORE UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE events IS 'Tabla base para todos los eventos de trazabilidad';
```

### 4.6 Tablas Específicas de Eventos

Django utiliza herencia Multi-Table (cada tabla tiene su propia PK que es FK a la tabla padre).

#### 4.6.1 irrigation_events (Aplicación de Riego)

```sql
CREATE TABLE irrigation_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    metodo VARCHAR(50) NOT NULL,
    duracion_minutos INT NOT NULL CHECK (duracion_minutos > 0),
    fuente_agua VARCHAR(50) NOT NULL,
    volumen_m3 NUMERIC(10, 2) CHECK (volumen_m3 >= 0),
    presion_bar NUMERIC(5, 2) CHECK (presion_bar BETWEEN 0 AND 10),
    ce_uScm NUMERIC(10, 2) CHECK (ce_uScm >= 0),
    ph NUMERIC(4, 2) CHECK (ph BETWEEN 0 AND 14)
);

CREATE INDEX idx_irrigation_metodo ON irrigation_events(metodo);
COMMENT ON TABLE irrigation_events IS 'Eventos de aplicación de riego';
```

#### 4.6.2 fertilization_events (Fertilización)

```sql
CREATE TABLE fertilization_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    tipo_fertilizante VARCHAR(50) NOT NULL,
    nombre_producto VARCHAR(200) NOT NULL,
    dosis_total_kg NUMERIC(10, 2) NOT NULL CHECK (dosis_total_kg > 0),
    metodo_aplicacion VARCHAR(50) NOT NULL,
    area_aplicada_ha NUMERIC(10, 4) CHECK (area_aplicada_ha > 0),
    npk_formula VARCHAR(50)
);

CREATE INDEX idx_fertilization_tipo ON fertilization_events(tipo_fertilizante);
COMMENT ON TABLE fertilization_events IS 'Eventos de fertilización';
```

#### 4.6.3 phytosanitary_events (Aplicación Fitosanitaria)

```sql
CREATE TABLE phytosanitary_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    tipo_producto VARCHAR(50) NOT NULL,
    nombre_producto VARCHAR(200) NOT NULL,
    ingrediente_activo VARCHAR(200),
    dosis_total_l_kg NUMERIC(10, 2) NOT NULL CHECK (dosis_total_l_kg > 0),
    metodo_aplicacion VARCHAR(50) NOT NULL,
    area_tratada_ha NUMERIC(10, 4) CHECK (area_tratada_ha > 0),
    plagas_objetivo TEXT,
    intervalo_seguridad_dias INT CHECK (intervalo_seguridad_dias >= 0)
);

CREATE INDEX idx_phytosanitary_tipo ON phytosanitary_events(tipo_producto);
COMMENT ON TABLE phytosanitary_events IS 'Eventos de aplicación fitosanitaria';
```

#### 4.6.4 maintenance_events (Labores de Cultivo)

```sql
CREATE TABLE maintenance_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    tipo_labor VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    area_intervenida_ha NUMERIC(10, 4) CHECK (area_intervenida_ha > 0),
    horas_hombre NUMERIC(10, 2) CHECK (horas_hombre >= 0),
    maquinaria_utilizada TEXT
);

CREATE INDEX idx_maintenance_tipo ON maintenance_events(tipo_labor);
COMMENT ON TABLE maintenance_events IS 'Eventos de labores de cultivo (poda, deshierbe, etc.)';
```

#### 4.6.5 monitoring_events (Monitoreo)

```sql
CREATE TABLE monitoring_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    tipo_monitoreo VARCHAR(100) NOT NULL,
    parametros_medidos TEXT NOT NULL,
    resultados TEXT NOT NULL,
    area_muestreada_ha NUMERIC(10, 4) CHECK (area_muestreada_ha > 0),
    numero_muestras INT CHECK (numero_muestras > 0),
    hallazgos_relevantes TEXT
);

CREATE INDEX idx_monitoring_tipo ON monitoring_events(tipo_monitoreo);
COMMENT ON TABLE monitoring_events IS 'Eventos de monitoreo (fitosanitario, fenológico, suelo, etc.)';
```

#### 4.6.6 outbreak_events (Brotes y Plagas)

```sql
CREATE TABLE outbreak_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    tipo_organismo VARCHAR(50) NOT NULL,
    nombre_organismo VARCHAR(200) NOT NULL,
    nivel_severidad VARCHAR(20) NOT NULL CHECK (nivel_severidad IN ('Bajo', 'Medio', 'Alto', 'Crítico')),
    area_afectada_ha NUMERIC(10, 4) CHECK (area_afectada_ha > 0),
    poblacion_estimada TEXT,
    estado_fenologico VARCHAR(100),
    acciones_tomadas TEXT
);

CREATE INDEX idx_outbreak_severidad ON outbreak_events(nivel_severidad);
COMMENT ON TABLE outbreak_events IS 'Eventos de brotes de plagas y enfermedades';
```

#### 4.6.7 climate_events (Eventos Climáticos)

```sql
CREATE TABLE climate_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    tipo_evento VARCHAR(50) NOT NULL,
    temperatura_min_c NUMERIC(5, 2),
    temperatura_max_c NUMERIC(5, 2),
    precipitacion_mm NUMERIC(10, 2) CHECK (precipitacion_mm >= 0),
    humedad_relativa_pct NUMERIC(5, 2) CHECK (humedad_relativa_pct BETWEEN 0 AND 100),
    velocidad_viento_kmh NUMERIC(10, 2) CHECK (velocidad_viento_kmh >= 0),
    descripcion_condiciones TEXT
);

CREATE INDEX idx_climate_tipo ON climate_events(tipo_evento);
COMMENT ON TABLE climate_events IS 'Eventos climáticos (lluvia, helada, granizo, etc.)';
```

#### 4.6.8 harvest_events (Cosecha)

```sql
CREATE TABLE harvest_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    tipo_cosecha VARCHAR(50) NOT NULL,
    cantidad_kg NUMERIC(12, 2) NOT NULL CHECK (cantidad_kg > 0),
    calidad VARCHAR(50) NOT NULL,
    destino VARCHAR(100) NOT NULL,
    cuadrillas INT CHECK (cuadrillas > 0),
    horas_cosecha NUMERIC(10, 2) CHECK (horas_cosecha > 0)
);

CREATE INDEX idx_harvest_tipo ON harvest_events(tipo_cosecha);
CREATE INDEX idx_harvest_calidad ON harvest_events(calidad);
COMMENT ON TABLE harvest_events IS 'Eventos de cosecha';
```

#### 4.6.9 postharvest_events (Poscosecha)

```sql
CREATE TABLE postharvest_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    tipo_proceso VARCHAR(100) NOT NULL,
    lote_procesado VARCHAR(100),
    cantidad_entrada_kg NUMERIC(12, 2) CHECK (cantidad_entrada_kg > 0),
    cantidad_salida_kg NUMERIC(12, 2) CHECK (cantidad_salida_kg > 0),
    merma_pct NUMERIC(5, 2) CHECK (merma_pct BETWEEN 0 AND 100),
    temperatura_almacen_c NUMERIC(5, 2),
    duracion_proceso_horas NUMERIC(10, 2) CHECK (duracion_proceso_horas > 0)
);

CREATE INDEX idx_postharvest_tipo ON postharvest_events(tipo_proceso);
COMMENT ON TABLE postharvest_events IS 'Eventos de procesos poscosecha';
```

#### 4.6.10 labor_cost_events (Mano de Obra y Costos)

```sql
CREATE TABLE labor_cost_events (
    event_ptr_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    tipo_labor VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    numero_trabajadores INT NOT NULL CHECK (numero_trabajadores > 0),
    horas_totales NUMERIC(10, 2) NOT NULL CHECK (horas_totales > 0),
    costo_total_mxn NUMERIC(12, 2) NOT NULL CHECK (costo_total_mxn >= 0),
    tipo_pago VARCHAR(50) NOT NULL
);

CREATE INDEX idx_labor_tipo ON labor_cost_events(tipo_labor);
COMMENT ON TABLE labor_cost_events IS 'Eventos de mano de obra y costos laborales';
```

-- Índices parciales (para consultas frecuentes)
CREATE INDEX idx_events_recent ON events(timestamp DESC)
    WHERE timestamp > NOW() - INTERVAL '90 days';

-- Particionado (opcional, para gran volumen)
-- Se puede particionar por rango de timestamp

-- Trigger
CREATE TRIGGER update_events_updated_at
    BEFORE UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE events IS 'Instancias de eventos registrados';
COMMENT ON COLUMN events.payload IS 'Datos capturados validados contra event_type.schema';
```

**Ejemplo de registro**:
```sql
INSERT INTO events (event_type_id, field_id, campaign_id, timestamp, payload, created_by_id) VALUES (
    1,  -- Riego
    'a1b2c3d4-...',
    5,
    '2025-10-13 08:30:00-06',
    '{
        "metodo": "goteo",
        "duracion_min": 90,
        "volumen_m3": 45.5,
        "presion_bar": 1.8,
        "ce_uScm": 850,
        "ph": 6.7
    }'::jsonb,
    3
);
```

### 4.7 Tabla: attachments

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
    uploaded_by_id INT REFERENCES auth_user(id) ON DELETE SET NULL,
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_attachments_event ON attachments(event_id);
CREATE INDEX idx_attachments_uploaded_at ON attachments(uploaded_at DESC);
CREATE INDEX idx_attachments_mime_type ON attachments(mime_type);

COMMENT ON TABLE attachments IS 'Archivos adjuntos a eventos (fotos, PDFs, hojas de cálculo, etc.)';
COMMENT ON COLUMN attachments.file IS 'Ruta del archivo gestionada por Django FileField';
COMMENT ON COLUMN attachments.file_size IS 'Tamaño en bytes, máximo 10MB';
```

### 4.8 Tabla: variables

Variables ambientales/IoT.

```sql
CREATE TABLE variables (
    id BIGSERIAL PRIMARY KEY,
    station_id INT REFERENCES stations(id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    variable_type VARCHAR(50) NOT NULL,
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

-- Particionado (recomendado para alto volumen)
-- Particionar por mes: CREATE TABLE variables_202510 PARTITION OF variables
--     FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

COMMENT ON TABLE variables IS 'Mediciones de variables ambientales';
COMMENT ON COLUMN variables.variable_type IS 'Tipo: soil_moisture, air_temp, humidity, ndvi, etc.';
```

**Tipos de Variable Estándar**:
```sql
-- Catálogo de tipos de variable (puede ser tabla o enum)
CREATE TYPE variable_type_enum AS ENUM (
    'soil_moisture',      -- Humedad suelo (%)
    'soil_temp',          -- Temperatura suelo (°C)
    'soil_ec',            -- CE suelo (µS/cm)
    'soil_ph',            -- pH suelo
    'air_temp',           -- Temperatura aire (°C)
    'humidity',           -- Humedad relativa (%)
    'precipitation',      -- Precipitación (mm)
    'wind_speed',         -- Velocidad viento (m/s)
    'solar_radiation',    -- Radiación solar (W/m²)
    'ndvi',               -- NDVI
    'ndre'                -- NDRE
);
```

### 4.9 Tabla: audit_logs

Auditoría de operaciones.

```sql
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id INT REFERENCES auth_user(id) ON DELETE SET NULL,
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

-- Particionado por mes (recomendado)
-- Los logs crecen mucho, particionar facilita mantenimiento

COMMENT ON TABLE audit_logs IS 'Registro de auditoría de operaciones';
COMMENT ON COLUMN audit_logs.diff IS 'Diferencia antes/después del cambio';
```

### 4.9 Usuarios (Django Auth)

Django maneja la tabla `auth_user` automáticamente. Extensión para roles:

```sql
-- Django crea: auth_user, auth_group, auth_permission

-- Extensión de perfil de usuario
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
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

COMMENT ON TABLE user_profiles IS 'Extensión de perfil de usuario con rol';
```

## 5. Funciones y Triggers

### 5.1 Trigger para updated_at

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```


## 6. Vistas Útiles

### 6.1 Vista: Eventos con Información Completa

```sql
CREATE VIEW v_events_full AS
SELECT
    e.id,
    e.timestamp,
    et.name AS event_type_name,
    et.category AS event_category,
    f.name AS field_name,
    f.code AS field_code,
    c.name AS campaign_name,
    e.payload,
    e.observations,
    u.username AS created_by,
    e.created_at,
    (SELECT COUNT(*) FROM attachments WHERE event_id = e.id) AS attachment_count
FROM events e
JOIN event_types et ON e.event_type_id = et.id
JOIN fields f ON e.field_id = f.id
LEFT JOIN campaigns c ON e.campaign_id = c.id
LEFT JOIN auth_user u ON e.created_by_id = u.id;

COMMENT ON VIEW v_events_full IS 'Vista desnormalizada de eventos con joins';
```

### 6.2 Vista: Variables Recientes por Estación

```sql
CREATE VIEW v_latest_variables AS
SELECT DISTINCT ON (station_id, variable_type)
    v.*,
    s.name AS station_name,
    f.name AS field_name
FROM variables v
JOIN stations s ON v.station_id = s.id
JOIN fields f ON s.field_id = f.id
ORDER BY station_id, variable_type, timestamp DESC;

COMMENT ON VIEW v_latest_variables IS 'Última lectura de cada variable por estación';
```

### 6.3 Vista: KPIs de Eventos por Lote

```sql
CREATE VIEW v_event_summary_by_field AS
SELECT
    f.id AS field_id,
    f.name AS field_name,
    et.category AS event_category,
    COUNT(*) AS event_count,
    MAX(e.timestamp) AS last_event_date
FROM fields f
LEFT JOIN events e ON f.id = e.field_id
LEFT JOIN event_types et ON e.event_type_id = et.id
GROUP BY f.id, f.name, et.category;

COMMENT ON VIEW v_event_summary_by_field IS 'Resumen de eventos por lote y categoría';
```

## 7. Políticas de Seguridad a Nivel de BD

### 7.1 Row Level Security (RLS) - Opcional

Si se implementa multi-tenancy:

```sql
ALTER TABLE fields ENABLE ROW LEVEL SECURITY;

CREATE POLICY field_access_policy ON fields
    USING (organization_id = current_setting('app.current_organization_id')::INT);
```

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

| Tabla | Filas (5 años) | Tamaño Estimado |
|-------|----------------|-----------------|
| fields | 20 | < 1 MB |
| campaigns | 25 | < 1 MB |
| stations | 40 | < 1 MB |
| event_types | 50 | < 1 MB |
| events | 20,000 | ~50 MB |
| attachments | 10,000 | ~5 GB (archivos) + 10 MB (metadata) |
| variables | 91,250 | ~20 MB |
| audit_logs | 50,000 | ~30 MB |
| **Total BD** | | **~120 MB** |
| **Total Storage** | | **~5.1 GB** |

**Nota**: El mayor consumo es de archivos adjuntos.

---

**Siguiente**: [Especificación de API REST →](./06_api_rest.md)

[← Volver al índice](../README.md)
