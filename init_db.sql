-- Script de inicialización de la base de datos

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- Para UUIDs
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- Para búsqueda de texto

-- Configuración de zona horaria
SET timezone = 'America/Mexico_City';

-- Mensaje de confirmación
DO $$ 
BEGIN 
    RAISE NOTICE 'Base de datos inicializada correctamente con extensiones UUID y pg_trgm';
END $$;
