-- Migración: Agregar campo personas_actuales a la tabla mesas
-- Fecha: 2025-12-08
-- Descripción: Agrega el campo personas_actuales para almacenar el número de personas
--              detectadas en tiempo real por el sistema de visión YOLO

-- Verificar si la columna ya existe antes de agregarla
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'mesas'
        AND column_name = 'personas_actuales'
    ) THEN
        ALTER TABLE mesas
        ADD COLUMN personas_actuales INTEGER NOT NULL DEFAULT 0;

        RAISE NOTICE 'Columna personas_actuales agregada exitosamente';
    ELSE
        RAISE NOTICE 'La columna personas_actuales ya existe';
    END IF;
END $$;

-- Verificar el resultado
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'mesas'
ORDER BY ordinal_position;
