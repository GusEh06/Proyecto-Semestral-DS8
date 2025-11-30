-- PostgreSQL database dump - CLEANED VERSION
-- Database: Restaurant Reservation System
-- Date: 2025-11-22

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';
SET default_table_access_method = heap;

-- =====================================================
-- TABLA: tipo_mesa
-- =====================================================
CREATE TABLE IF NOT EXISTS public.tipo_mesa (
    id_tipo_mesa SERIAL PRIMARY KEY,
    descripcion VARCHAR(50) NOT NULL,
    cantidad_sillas INTEGER NOT NULL,
    CONSTRAINT tipo_mesa_cantidad_sillas_check CHECK (cantidad_sillas > 0)
);

-- =====================================================
-- TABLA: mesas
-- =====================================================
CREATE TABLE IF NOT EXISTS public.mesas (
    id_mesa SERIAL PRIMARY KEY,
    id_tipo_mesa INTEGER NOT NULL,
    estado VARCHAR(20) DEFAULT 'disponible' NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    CONSTRAINT mesas_estado_check CHECK (estado IN ('disponible', 'ocupada', 'reservada'))
);

-- =====================================================
-- TABLA: reservaciones
-- =====================================================
CREATE TABLE IF NOT EXISTS public.reservaciones (
    id_reserva SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL,
    telefono VARCHAR(50),
    cantidad_personas INTEGER NOT NULL,
    fecha DATE NOT NULL,
    hora TIME WITHOUT TIME ZONE NOT NULL,
    id_mesa INTEGER,
    estado VARCHAR(20) DEFAULT 'pendiente',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    CONSTRAINT reservaciones_cantidad_personas_check CHECK (cantidad_personas > 0),
    CONSTRAINT reservaciones_estado_check CHECK (estado IN ('pendiente', 'confirmada', 'cancelada', 'completada'))
);

-- =====================================================
-- TABLA: usuarios_admin
-- =====================================================
CREATE TABLE IF NOT EXISTS public.usuarios_admin (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol VARCHAR(30) DEFAULT 'admin',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    CONSTRAINT usuarios_admin_rol_check CHECK (rol IN ('admin', 'superadmin', 'staff'))
);

-- =====================================================
-- FOREIGN KEYS
-- =====================================================
ALTER TABLE public.mesas
    ADD CONSTRAINT mesas_id_tipo_mesa_fkey 
    FOREIGN KEY (id_tipo_mesa) 
    REFERENCES public.tipo_mesa(id_tipo_mesa) 
    ON DELETE RESTRICT;

ALTER TABLE public.reservaciones
    ADD CONSTRAINT reservaciones_id_mesa_fkey 
    FOREIGN KEY (id_mesa) 
    REFERENCES public.mesas(id_mesa) 
    ON DELETE SET NULL;

-- =====================================================
-- INDEXES
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_mesas_estado ON public.mesas USING btree (estado);
CREATE INDEX IF NOT EXISTS idx_mesas_tipo ON public.mesas USING btree (id_tipo_mesa);
CREATE INDEX IF NOT EXISTS idx_reservaciones_fecha ON public.reservaciones USING btree (fecha, hora);
CREATE INDEX IF NOT EXISTS idx_reservaciones_estado ON public.reservaciones USING btree (estado);
CREATE INDEX IF NOT EXISTS idx_reservaciones_correo ON public.reservaciones USING btree (correo);
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON public.usuarios_admin USING btree (email);
CREATE INDEX IF NOT EXISTS idx_usuarios_active ON public.usuarios_admin USING btree (is_active);

-- =====================================================
-- COMPLETED
-- =====================================================