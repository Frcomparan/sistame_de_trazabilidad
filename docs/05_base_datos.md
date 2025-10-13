# Diseño de Base de Datos

[← Volver al índice](../README.md) | [← Modelo de Dominio](./04_modelo_dominio.md) | [API REST →](./06_api_rest.md)

## 1. Introducción

Este documento especifica el esquema físico de la base de datos PostgreSQL, incluyendo tablas, índices, constraints y optimizaciones.

## 2. Motor de Base de Datos

**PostgreSQL 15+**

**Razones de Selección**:
- ✅ Soporte nativo de **JSONB** (crítico para eventos dinámicos)
- ✅ **Índices GIN** para consultas eficientes en JSONB
- ✅ **PostGIS** para datos geoespaciales (opcional)
- ✅ **Transacciones ACID** completas
- ✅ **Maduro y estable**
- ✅ **Open source** (sin costos de licenciamiento)

## 3. Configuración Recomendada

```sql
-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- Para UUIDs
CREATE EXTENSION IF NOT EXISTS "postgis";        -- Para geometrías (opcional)
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
    location VARCHAR(200),
    latitude NUMERIC(9, 6) CHECK (latitude BETWEEN -90 AND 90),
    longitude NUMERIC(9, 6) CHECK (longitude BETWEEN -180 AND 180),
    geometry GEOGRAPHY(POLYGON, 4326),  -- PostGIS
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_fields_code ON fields(code);
CREATE INDEX idx_fields_is_active ON fields(is_active);
CREATE INDEX idx_fields_geometry ON fields USING GIST(geometry);  -- PostGIS

-- Trigger para updated_at
CREATE TRIGGER update_fields_updated_at
    BEFORE UPDATE ON fields
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comentarios
COMMENT ON TABLE fields IS 'Lotes o parcelas de cultivo';
COMMENT ON COLUMN fields.geometry IS 'Polígono del lote en formato WGS84';
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
    latitude NUMERIC(9, 6) NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude NUMERIC(9, 6) NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    is_operational BOOLEAN DEFAULT TRUE,
    installed_at DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_stations_field ON stations(field_id);
CREATE INDEX idx_stations_operational ON stations(is_operational);
CREATE INDEX idx_stations_location ON stations(latitude, longitude);

-- Trigger
CREATE TRIGGER update_stations_updated_at
    BEFORE UPDATE ON stations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE stations IS 'Estaciones de monitoreo de variables ambientales';
```

### 4.4 Tabla: event_types

Definición de tipos de evento (esquemas dinámicos).

```sql
CREATE TABLE event_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    schema JSONB NOT NULL,  -- JSON Schema de validación
    version INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    icon VARCHAR(50),       -- CSS class para icono
    color VARCHAR(7),       -- Color hex (ej: #28a745)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT check_event_type_category CHECK (category IN (
        'riego', 'fertilizacion', 'fitosanitarios', 'labores',
        'monitoreo', 'brotes', 'clima', 'cosecha', 'poscosecha',
        'mano_obra', 'otro'
    ))
);

-- Índices
CREATE INDEX idx_event_types_name ON event_types(name);
CREATE INDEX idx_event_types_category ON event_types(category);
CREATE INDEX idx_event_types_active ON event_types(is_active);
CREATE INDEX idx_event_types_schema_gin ON event_types USING GIN(schema);

-- Trigger
CREATE TRIGGER update_event_types_updated_at
    BEFORE UPDATE ON event_types
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE event_types IS 'Definiciones de tipos de eventos con esquemas dinámicos';
COMMENT ON COLUMN event_types.schema IS 'JSON Schema (draft-07) para validación del payload';
```

**Ejemplo de registro**:
```sql
INSERT INTO event_types (name, category, description, schema, icon, color) VALUES (
    'Riego',
    'riego',
    'Evento de aplicación de riego',
    '{
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "metodo": {
                "type": "string",
                "enum": ["goteo", "microaspersion", "gravedad", "aspersion"],
                "title": "Método de Riego"
            },
            "duracion_min": {
                "type": "number",
                "minimum": 0,
                "title": "Duración (min)"
            },
            "volumen_m3": {
                "type": "number",
                "minimum": 0,
                "title": "Volumen (m³)",
                "unit": "m³"
            },
            "presion_bar": {
                "type": "number",
                "minimum": 0,
                "maximum": 10,
                "title": "Presión (bar)",
                "unit": "bar"
            },
            "ce_uScm": {
                "type": "number",
                "minimum": 0,
                "title": "CE (µS/cm)",
                "unit": "µS/cm"
            },
            "ph": {
                "type": "number",
                "minimum": 0,
                "maximum": 14,
                "title": "pH"
            }
        },
        "required": ["metodo", "duracion_min"]
    }'::jsonb,
    'fas fa-tint',
    '#007bff'
);
```

### 4.5 Tabla: events

Instancias de eventos (registros reales).

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type_id INT NOT NULL REFERENCES event_types(id) ON DELETE PROTECT,
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    campaign_id INT REFERENCES campaigns(id) ON DELETE SET NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    payload JSONB NOT NULL,  -- Datos capturados según schema
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
CREATE INDEX idx_events_payload_gin ON events USING GIN(payload jsonb_path_ops);

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

### 4.6 Tabla: attachments

Archivos adjuntos a eventos.

```sql
CREATE TABLE attachments (
    id BIGSERIAL PRIMARY KEY,
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
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

COMMENT ON TABLE attachments IS 'Archivos adjuntos (fotos, PDFs, etc.)';
COMMENT ON COLUMN attachments.file_path IS 'Ruta relativa en storage';
```

### 4.7 Tabla: variables

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

### 4.8 Tabla: audit_logs

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

### 5.2 Función de Validación de Geometría

```sql
CREATE OR REPLACE FUNCTION validate_station_within_field()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM fields
        WHERE id = NEW.field_id
          AND geometry IS NOT NULL
          AND NOT ST_Within(
              ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326),
              geometry
          )
    ) THEN
        RAISE EXCEPTION 'La estación debe estar dentro del polígono del lote';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_station_location
    BEFORE INSERT OR UPDATE ON stations
    FOR EACH ROW
    EXECUTE FUNCTION validate_station_within_field();
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
