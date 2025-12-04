-- ========================================
-- SCRIPT DE DATOS DE EJEMPLO
-- Sistema de Gestión de Restaurante
-- ========================================

-- NOTA: Ejecuta este script DESPUÉS de crear las tablas (reservationsdb.sql)

-- ========================================
-- 1. TIPOS DE MESA
-- ========================================

INSERT INTO tipo_mesa (descripcion, cantidad_sillas) VALUES
('Mesa para 2 personas', 2),
('Mesa para 4 personas', 4),
('Mesa para 6 personas', 6),
('Mesa para 8 personas', 8),
('Mesa VIP para 10 personas', 10)
ON CONFLICT DO NOTHING;

-- ========================================
-- 2. MESAS DEL RESTAURANTE
-- ========================================

-- 5 mesas para 2 personas (ID tipo: 1)
INSERT INTO mesas (id_tipo_mesa, estado) VALUES
(1, 'disponible'),
(1, 'disponible'),
(1, 'disponible'),
(1, 'disponible'),
(1, 'disponible');

-- 8 mesas para 4 personas (ID tipo: 2)
INSERT INTO mesas (id_tipo_mesa, estado) VALUES
(2, 'disponible'),
(2, 'disponible'),
(2, 'disponible'),
(2, 'disponible'),
(2, 'disponible'),
(2, 'disponible'),
(2, 'disponible'),
(2, 'disponible');

-- 4 mesas para 6 personas (ID tipo: 3)
INSERT INTO mesas (id_tipo_mesa, estado) VALUES
(3, 'disponible'),
(3, 'disponible'),
(3, 'disponible'),
(3, 'disponible');

-- 2 mesas para 8 personas (ID tipo: 4)
INSERT INTO mesas (id_tipo_mesa, estado) VALUES
(4, 'disponible'),
(4, 'disponible');

-- 1 mesa VIP para 10 personas (ID tipo: 5)
INSERT INTO mesas (id_tipo_mesa, estado) VALUES
(5, 'disponible');

-- Total: 20 mesas

-- ========================================
-- 3. RESERVACIONES DE EJEMPLO (Opcional)
-- ========================================

-- Reservaciones para HOY (ajusta la fecha según necesites)
INSERT INTO reservaciones (
    nombre,
    apellido,
    correo,
    telefono,
    cantidad_personas,
    fecha,
    hora,
    id_mesa,
    estado
) VALUES
-- Reservaciones confirmadas para hoy
('Juan', 'Pérez', 'juan.perez@email.com', '6000-0000', 4, CURRENT_DATE, '18:00:00', 6, 'confirmada'),
('María', 'González', 'maria.gonzalez@email.com', '6111-1111', 2, CURRENT_DATE, '19:00:00', 1, 'confirmada'),
('Carlos', 'Rodríguez', 'carlos.rodriguez@email.com', '6222-2222', 6, CURRENT_DATE, '20:00:00', 14, 'confirmada'),
('Ana', 'López', 'ana.lopez@email.com', '6333-3333', 4, CURRENT_DATE, '19:30:00', 7, 'confirmada'),

-- Reservaciones pendientes para hoy
('Luis', 'Martínez', 'luis.martinez@email.com', '6444-4444', 2, CURRENT_DATE, '21:00:00', 2, 'pendiente'),
('Elena', 'Sánchez', 'elena.sanchez@email.com', '6555-5555', 4, CURRENT_DATE, '21:30:00', 8, 'pendiente'),

-- Reservaciones para mañana
('Pedro', 'Ramírez', 'pedro.ramirez@email.com', '6666-6666', 8, CURRENT_DATE + 1, '19:00:00', 19, 'pendiente'),
('Laura', 'Torres', 'laura.torres@email.com', '6777-7777', 4, CURRENT_DATE + 1, '20:00:00', 9, 'pendiente'),
('José', 'Flores', 'jose.flores@email.com', '6888-8888', 6, CURRENT_DATE + 1, '18:30:00', 15, 'confirmada'),

-- Reservaciones para pasado mañana
('Sofía', 'Vargas', 'sofia.vargas@email.com', '6999-9999', 2, CURRENT_DATE + 2, '19:00:00', 3, 'pendiente'),
('Miguel', 'Cruz', 'miguel.cruz@email.com', '6000-1111', 10, CURRENT_DATE + 2, '20:00:00', 20, 'confirmada');

-- ========================================
-- 4. VERIFICACIÓN
-- ========================================

-- Mostrar resumen de datos insertados
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'RESUMEN DE DATOS INSERTADOS';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tipos de mesa: %', (SELECT COUNT(*) FROM tipo_mesa);
    RAISE NOTICE 'Mesas: %', (SELECT COUNT(*) FROM mesas);
    RAISE NOTICE 'Reservaciones: %', (SELECT COUNT(*) FROM reservaciones);
    RAISE NOTICE 'Usuarios admin: %', (SELECT COUNT(*) FROM usuarios_admin);
    RAISE NOTICE '';
    RAISE NOTICE 'Distribución de mesas por capacidad:';
    RAISE NOTICE '  - 2 personas: %', (SELECT COUNT(*) FROM mesas WHERE id_tipo_mesa = 1);
    RAISE NOTICE '  - 4 personas: %', (SELECT COUNT(*) FROM mesas WHERE id_tipo_mesa = 2);
    RAISE NOTICE '  - 6 personas: %', (SELECT COUNT(*) FROM mesas WHERE id_tipo_mesa = 3);
    RAISE NOTICE '  - 8 personas: %', (SELECT COUNT(*) FROM mesas WHERE id_tipo_mesa = 4);
    RAISE NOTICE '  - 10 personas: %', (SELECT COUNT(*) FROM mesas WHERE id_tipo_mesa = 5);
    RAISE NOTICE '';
    RAISE NOTICE 'Estados de mesas:';
    RAISE NOTICE '  - Disponibles: %', (SELECT COUNT(*) FROM mesas WHERE estado = 'disponible');
    RAISE NOTICE '  - Ocupadas: %', (SELECT COUNT(*) FROM mesas WHERE estado = 'ocupada');
    RAISE NOTICE '  - Reservadas: %', (SELECT COUNT(*) FROM mesas WHERE estado = 'reservada');
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE '✓ Datos insertados correctamente';
    RAISE NOTICE '========================================';
END $$;
