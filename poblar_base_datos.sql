-- ========================================
-- SCRIPT PARA POBLAR LA BASE DE DATOS
-- Sistema de Gestión de Restaurante
-- ========================================
-- Ejecutar con: psql -U postgres -d restaurante_db -f poblar_base_datos.sql

BEGIN;

-- ========================================
-- 1. LIMPIAR DATOS EXISTENTES (OPCIONAL)
-- ========================================
-- Descomenta estas líneas si quieres empezar desde cero
-- TRUNCATE TABLE reservaciones CASCADE;
-- TRUNCATE TABLE mesas CASCADE;
-- TRUNCATE TABLE tipo_mesa CASCADE;

-- ========================================
-- 2. TIPOS DE MESA
-- ========================================

-- Verificar si ya existen tipos de mesa
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM tipo_mesa LIMIT 1) THEN
        INSERT INTO tipo_mesa (descripcion, cantidad_sillas) VALUES
        ('Mesa pequeña para 2 personas', 2),
        ('Mesa estándar para 4 personas', 4),
        ('Mesa familiar para 6 personas', 6),
        ('Mesa grande para 8 personas', 8),
        ('Mesa VIP para 10 personas', 10);

        RAISE NOTICE '✓ Insertados 5 tipos de mesa';
    ELSE
        RAISE NOTICE '⚠ Los tipos de mesa ya existen, saltando...';
    END IF;
END $$;

-- ========================================
-- 3. MESAS DEL RESTAURANTE
-- ========================================

-- Verificar si ya existen mesas
DO $$
DECLARE
    mesa_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO mesa_count FROM mesas;

    IF mesa_count = 0 THEN
        -- 5 mesas para 2 personas
        INSERT INTO mesas (id_tipo_mesa, estado) VALUES
        (1, 'disponible'),
        (1, 'disponible'),
        (1, 'disponible'),
        (1, 'disponible'),
        (1, 'disponible');

        -- 8 mesas para 4 personas
        INSERT INTO mesas (id_tipo_mesa, estado) VALUES
        (2, 'disponible'),
        (2, 'disponible'),
        (2, 'disponible'),
        (2, 'disponible'),
        (2, 'disponible'),
        (2, 'disponible'),
        (2, 'disponible'),
        (2, 'disponible');

        -- 4 mesas para 6 personas
        INSERT INTO mesas (id_tipo_mesa, estado) VALUES
        (3, 'disponible'),
        (3, 'disponible'),
        (3, 'disponible'),
        (3, 'disponible');

        -- 2 mesas para 8 personas
        INSERT INTO mesas (id_tipo_mesa, estado) VALUES
        (4, 'disponible'),
        (4, 'disponible');

        -- 1 mesa VIP para 10 personas
        INSERT INTO mesas (id_tipo_mesa, estado) VALUES
        (5, 'disponible');

        RAISE NOTICE '✓ Insertadas 20 mesas';
    ELSE
        RAISE NOTICE '⚠ Ya existen % mesas, saltando...', mesa_count;
    END IF;
END $$;

-- ========================================
-- 4. RESERVACIONES DE EJEMPLO
-- ========================================

-- Insertar reservaciones solo si no hay ninguna
DO $$
DECLARE
    reserva_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO reserva_count FROM reservaciones;

    IF reserva_count = 0 THEN
        -- Reservaciones confirmadas para HOY
        INSERT INTO reservaciones (
            nombre, apellido, correo, telefono,
            cantidad_personas, fecha, hora, id_mesa, estado
        ) VALUES
        ('Juan', 'Pérez', 'juan.perez@email.com', '6000-0000', 4, CURRENT_DATE, '18:00:00', 6, 'confirmada'),
        ('María', 'González', 'maria.gonzalez@email.com', '6111-1111', 2, CURRENT_DATE, '19:00:00', 1, 'confirmada'),
        ('Carlos', 'Rodríguez', 'carlos.rodriguez@email.com', '6222-2222', 6, CURRENT_DATE, '20:00:00', 14, 'confirmada'),
        ('Ana', 'López', 'ana.lopez@email.com', '6333-3333', 4, CURRENT_DATE, '19:30:00', 7, 'confirmada');

        -- Reservaciones pendientes para HOY
        INSERT INTO reservaciones (
            nombre, apellido, correo, telefono,
            cantidad_personas, fecha, hora, id_mesa, estado
        ) VALUES
        ('Luis', 'Martínez', 'luis.martinez@email.com', '6444-4444', 2, CURRENT_DATE, '21:00:00', 2, 'pendiente'),
        ('Elena', 'Sánchez', 'elena.sanchez@email.com', '6555-5555', 4, CURRENT_DATE, '21:30:00', 8, 'pendiente');

        -- Reservaciones para MAÑANA
        INSERT INTO reservaciones (
            nombre, apellido, correo, telefono,
            cantidad_personas, fecha, hora, id_mesa, estado
        ) VALUES
        ('Pedro', 'Ramírez', 'pedro.ramirez@email.com', '6666-6666', 8, CURRENT_DATE + 1, '19:00:00', 19, 'pendiente'),
        ('Laura', 'Torres', 'laura.torres@email.com', '6777-7777', 4, CURRENT_DATE + 1, '20:00:00', 9, 'pendiente'),
        ('José', 'Flores', 'jose.flores@email.com', '6888-8888', 6, CURRENT_DATE + 1, '18:30:00', 15, 'confirmada');

        -- Reservaciones para PASADO MAÑANA
        INSERT INTO reservaciones (
            nombre, apellido, correo, telefono,
            cantidad_personas, fecha, hora, id_mesa, estado
        ) VALUES
        ('Sofía', 'Vargas', 'sofia.vargas@email.com', '6999-9999', 2, CURRENT_DATE + 2, '19:00:00', 3, 'pendiente'),
        ('Miguel', 'Cruz', 'miguel.cruz@email.com', '6000-1111', 10, CURRENT_DATE + 2, '20:00:00', 20, 'confirmada');

        -- Reservaciones COMPLETADAS (ayer)
        INSERT INTO reservaciones (
            nombre, apellido, correo, telefono,
            cantidad_personas, fecha, hora, id_mesa, estado
        ) VALUES
        ('Roberto', 'Morales', 'roberto.morales@email.com', '6111-2222', 4, CURRENT_DATE - 1, '19:00:00', 6, 'completada'),
        ('Carmen', 'Ruiz', 'carmen.ruiz@email.com', '6222-3333', 2, CURRENT_DATE - 1, '20:00:00', 1, 'completada');

        -- Reservaciones CANCELADAS
        INSERT INTO reservaciones (
            nombre, apellido, correo, telefono,
            cantidad_personas, fecha, hora, id_mesa, estado
        ) VALUES
        ('Diego', 'Silva', 'diego.silva@email.com', '6333-4444', 6, CURRENT_DATE, '22:00:00', 14, 'cancelada');

        RAISE NOTICE '✓ Insertadas 14 reservaciones de ejemplo';
    ELSE
        RAISE NOTICE '⚠ Ya existen % reservaciones, saltando...', reserva_count;
    END IF;
END $$;

-- ========================================
-- 5. ACTUALIZAR ESTADO DE MESAS RESERVADAS
-- ========================================

-- Marcar como "reservadas" las mesas que tienen reservaciones confirmadas para hoy
UPDATE mesas m
SET estado = 'reservada'
WHERE id_mesa IN (
    SELECT id_mesa
    FROM reservaciones
    WHERE fecha = CURRENT_DATE
    AND estado IN ('confirmada', 'pendiente')
    AND id_mesa IS NOT NULL
);

-- ========================================
-- 6. RESUMEN DE DATOS INSERTADOS
-- ========================================

DO $$
DECLARE
    tipos_count INTEGER;
    mesas_count INTEGER;
    reservas_count INTEGER;
    usuarios_count INTEGER;
    mesas_disponibles INTEGER;
    mesas_ocupadas INTEGER;
    mesas_reservadas INTEGER;
BEGIN
    SELECT COUNT(*) INTO tipos_count FROM tipo_mesa;
    SELECT COUNT(*) INTO mesas_count FROM mesas;
    SELECT COUNT(*) INTO reservas_count FROM reservaciones;
    SELECT COUNT(*) INTO usuarios_count FROM usuarios_admin;

    SELECT COUNT(*) INTO mesas_disponibles FROM mesas WHERE estado = 'disponible';
    SELECT COUNT(*) INTO mesas_ocupadas FROM mesas WHERE estado = 'ocupada';
    SELECT COUNT(*) INTO mesas_reservadas FROM mesas WHERE estado = 'reservada';

    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE '         RESUMEN DE LA BASE DE DATOS';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Tipos de mesa: %', tipos_count;
    RAISE NOTICE 'Total de mesas: %', mesas_count;
    RAISE NOTICE '  - Disponibles: %', mesas_disponibles;
    RAISE NOTICE '  - Ocupadas: %', mesas_ocupadas;
    RAISE NOTICE '  - Reservadas: %', mesas_reservadas;
    RAISE NOTICE '';
    RAISE NOTICE 'Total de reservaciones: %', reservas_count;
    RAISE NOTICE 'Usuarios administradores: %', usuarios_count;
    RAISE NOTICE '';

    IF usuarios_count = 0 THEN
        RAISE NOTICE '⚠ IMPORTANTE: No hay usuarios admin';
        RAISE NOTICE '   Ejecuta: cd back-end && python create_admin.py';
        RAISE NOTICE '';
    END IF;

    RAISE NOTICE '========================================';
    RAISE NOTICE '✓ Base de datos poblada correctamente';
    RAISE NOTICE '========================================';
END $$;

COMMIT;

-- ========================================
-- 7. CONSULTAS DE VERIFICACIÓN
-- ========================================

-- Mostrar distribución de mesas por tipo
SELECT
    t.descripcion as "Tipo de Mesa",
    t.cantidad_sillas as "Capacidad",
    COUNT(m.id_mesa) as "Cantidad"
FROM tipo_mesa t
LEFT JOIN mesas m ON t.id_tipo_mesa = m.id_tipo_mesa
GROUP BY t.id_tipo_mesa, t.descripcion, t.cantidad_sillas
ORDER BY t.cantidad_sillas;

-- Mostrar estado de mesas
SELECT
    estado as "Estado",
    COUNT(*) as "Cantidad"
FROM mesas
GROUP BY estado
ORDER BY
    CASE estado
        WHEN 'disponible' THEN 1
        WHEN 'ocupada' THEN 2
        WHEN 'reservada' THEN 3
    END;

-- Mostrar reservaciones de hoy
SELECT
    r.id_reserva as "ID",
    r.nombre || ' ' || r.apellido as "Cliente",
    r.cantidad_personas as "Personas",
    r.hora as "Hora",
    r.id_mesa as "Mesa",
    r.estado as "Estado"
FROM reservaciones r
WHERE r.fecha = CURRENT_DATE
ORDER BY r.hora;
