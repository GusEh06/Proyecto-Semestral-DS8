-- =====================================================
-- ESQUEMA DE BASE DE DATOS PARA SISTEMA DE RESTAURANTE
-- =====================================================
-- PostgreSQL Database Schema

-- Eliminar tablas si existen (para desarrollo)
DROP TABLE IF EXISTS reservas CASCADE;
DROP TABLE IF EXISTS mesas CASCADE;

-- ==================== TABLA: MESAS ====================
CREATE TABLE mesas (
    id_mesa SERIAL PRIMARY KEY,
    numero_mesa VARCHAR(10) UNIQUE NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'disponible',
    capacidad INTEGER NOT NULL,
    reservada BOOLEAN DEFAULT FALSE,
    id_reserva_actual INTEGER DEFAULT NULL,
    ubicacion VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    vision_detected_at TIMESTAMP,
    
    CONSTRAINT check_estado CHECK (estado IN ('disponible', 'ocupada', 'reservada', 'mantenimiento'))
);

-- Índices para optimizar consultas
CREATE INDEX idx_mesas_estado ON mesas(estado);
CREATE INDEX idx_mesas_reservada ON mesas(reservada);
CREATE INDEX idx_mesas_updated_at ON mesas(updated_at);

-- ==================== TABLA: RESERVAS ====================
CREATE TABLE reservas (
    id_reserva SERIAL PRIMARY KEY,
    id_mesa INTEGER NOT NULL,
    nombre_cliente VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    num_personas INTEGER NOT NULL,
    fecha_reserva DATE NOT NULL,
    hora_reserva TIME NOT NULL,
    estado_reserva VARCHAR(20) DEFAULT 'confirmada',
    notas TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT fk_mesa FOREIGN KEY (id_mesa) REFERENCES mesas(id_mesa) ON DELETE CASCADE,
    CONSTRAINT check_estado_reserva CHECK (estado_reserva IN ('confirmada', 'cancelada', 'completada', 'expirada', 'no_show'))
);

-- Índices para optimizar consultas
CREATE INDEX idx_reservas_mesa ON reservas(id_mesa);
CREATE INDEX idx_reservas_fecha ON reservas(fecha_reserva, hora_reserva);
CREATE INDEX idx_reservas_estado ON reservas(estado_reserva);
CREATE INDEX idx_reservas_cliente ON reservas(nombre_cliente);

-- ==================== DATOS DE EJEMPLO ====================

-- Insertar mesas de ejemplo
INSERT INTO mesas (numero_mesa, capacidad, estado, ubicacion) VALUES
('M01', 2, 'disponible', 'Ventana izquierda'),
('M02', 2, 'disponible', 'Ventana izquierda'),
('M03', 4, 'disponible', 'Centro'),
('M04', 4, 'disponible', 'Centro'),
('M05', 6, 'disponible', 'Zona VIP'),
('M06', 6, 'disponible', 'Zona VIP'),
('M07', 2, 'disponible', 'Barra'),
('M08', 4, 'disponible', 'Terraza'),
('M09', 4, 'disponible', 'Terraza'),
('M10', 8, 'disponible', 'Salón privado');

-- Insertar algunas reservas de ejemplo
INSERT INTO reservas (id_mesa, nombre_cliente, telefono, email, num_personas, fecha_reserva, hora_reserva, notas) VALUES
(5, 'María González', '+507 6123-4567', 'maria@example.com', 6, CURRENT_DATE + INTERVAL '1 day', '19:00:00', 'Celebración de cumpleaños'),
(8, 'Carlos Ramírez', '+507 6234-5678', 'carlos@example.com', 4, CURRENT_DATE + INTERVAL '2 days', '20:30:00', 'Cena de negocios');

-- Marcar las mesas con reservas como reservadas
UPDATE mesas SET reservada = TRUE, estado = 'reservada', id_reserva_actual = 1 WHERE id_mesa = 5;
UPDATE mesas SET reservada = TRUE, estado = 'reservada', id_reserva_actual = 2 WHERE id_mesa = 8;

-- ==================== FUNCIONES ÚTILES ====================

-- Función para obtener el estado del restaurante completo
CREATE OR REPLACE FUNCTION get_restaurant_status()
RETURNS TABLE (
    mesa VARCHAR,
    estado VARCHAR,
    reservada BOOLEAN,
    capacidad INTEGER,
    cliente VARCHAR,
    hora_reserva TIME
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.numero_mesa,
        m.estado,
        m.reservada,
        m.capacidad,
        r.nombre_cliente,
        r.hora_reserva
    FROM mesas m
    LEFT JOIN reservas r ON m.id_reserva_actual = r.id_reserva
    ORDER BY m.numero_mesa;
END;
$$ LANGUAGE plpgsql;

-- Función para liberar automáticamente reservas expiradas
CREATE OR REPLACE FUNCTION liberar_reservas_expiradas()
RETURNS INTEGER AS $$
DECLARE
    reservas_liberadas INTEGER;
BEGIN
    UPDATE mesas m
    SET reservada = FALSE,
        id_reserva_actual = NULL,
        estado = 'disponible',
        updated_at = NOW()
    FROM reservas r
    WHERE m.id_reserva_actual = r.id_reserva
    AND r.estado_reserva = 'confirmada'
    AND (r.fecha_reserva + r.hora_reserva + INTERVAL '2 hours') < NOW();
    
    GET DIAGNOSTICS reservas_liberadas = ROW_COUNT;
    
    UPDATE reservas
    SET estado_reserva = 'expirada',
        updated_at = NOW()
    WHERE estado_reserva = 'confirmada'
    AND (fecha_reserva + hora_reserva + INTERVAL '2 hours') < NOW();
    
    RETURN reservas_liberadas;
END;
$$ LANGUAGE plpgsql;

-- ==================== VISTAS ÚTILES ====================

-- Vista de mesas disponibles para reserva
CREATE OR REPLACE VIEW mesas_disponibles AS
SELECT 
    id_mesa,
    numero_mesa,
    capacidad,
    ubicacion,
    estado
FROM mesas
WHERE reservada = FALSE 
AND estado != 'mantenimiento';

-- Vista de reservas activas
CREATE OR REPLACE VIEW reservas_activas AS
SELECT 
    r.id_reserva,
    r.id_mesa,
    m.numero_mesa,
    r.nombre_cliente,
    r.telefono,
    r.num_personas,
    r.fecha_reserva,
    r.hora_reserva,
    r.estado_reserva,
    r.notas
FROM reservas r
JOIN mesas m ON r.id_mesa = m.id_mesa
WHERE r.estado_reserva = 'confirmada'
AND r.fecha_reserva >= CURRENT_DATE
ORDER BY r.fecha_reserva, r.hora_reserva;

-- ==================== TRIGGERS ====================

-- Trigger para actualizar el timestamp de updated_at automáticamente
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER mesas_update_timestamp
BEFORE UPDATE ON mesas
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER reservas_update_timestamp
BEFORE UPDATE ON reservas
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- ==================== PERMISOS (opcional) ====================

-- Crear usuario específico para la aplicación
-- CREATE USER restaurant_app WITH PASSWORD 'secure_password_here';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON mesas, reservas TO restaurant_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO restaurant_app;

-- ==================== QUERIES DE PRUEBA ====================

-- Ver estado de todas las mesas
-- SELECT * FROM get_restaurant_status();

-- Ver mesas disponibles
-- SELECT * FROM mesas_disponibles;

-- Ver reservas activas
-- SELECT * FROM reservas_activas;

-- Liberar reservas expiradas manualmente
-- SELECT liberar_reservas_expiradas();

-- Estadísticas del día
-- SELECT 
--     COUNT(*) FILTER (WHERE estado = 'disponible') as disponibles,
--     COUNT(*) FILTER (WHERE estado = 'ocupada') as ocupadas,
--     COUNT(*) FILTER (WHERE estado = 'reservada') as reservadas
-- FROM mesas;
