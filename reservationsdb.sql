--
-- PostgreSQL database dump
--

\restrict H5isupFJpsG7C6udcsUGqPdlMtLTlpcHmdRGQb6srKbbD9Ac75igTwKKTS5IFuU

-- Dumped from database version 18.0
-- Dumped by pg_dump version 18.0

-- Started on 2025-11-22 22:12:12

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

--
-- TOC entry 4 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: pg_database_owner
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO pg_database_owner;

--
-- TOC entry 5060 (class 0 OID 0)
-- Dependencies: 4
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: pg_database_owner
--

COMMENT ON SCHEMA public IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 222 (class 1259 OID 24588)
-- Name: mesas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mesas (
    id_mesa integer NOT NULL,
    id_tipo_mesa integer NOT NULL,
    estado character varying(20) DEFAULT 'disponible'::character varying NOT NULL,
    updated_at timestamp without time zone DEFAULT now(),
    CONSTRAINT mesas_estado_check CHECK (((estado)::text = ANY ((ARRAY['disponible'::character varying, 'ocupada'::character varying, 'reservada'::character varying])::text[])))
);


ALTER TABLE public.mesas OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 24587)
-- Name: mesas_id_mesa_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mesas_id_mesa_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mesas_id_mesa_seq OWNER TO postgres;

--
-- TOC entry 5061 (class 0 OID 0)
-- Dependencies: 221
-- Name: mesas_id_mesa_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mesas_id_mesa_seq OWNED BY public.mesas.id_mesa;


--
-- TOC entry 224 (class 1259 OID 24608)
-- Name: reservaciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reservaciones (
    id_reserva integer NOT NULL,
    nombre character varying(100) NOT NULL,
    apellido character varying(100) NOT NULL,
    correo character varying(150) NOT NULL,
    telefono character varying(50),
    cantidad_personas integer NOT NULL,
    fecha date NOT NULL,
    hora time without time zone NOT NULL,
    id_mesa integer,
    estado character varying(20) DEFAULT 'pendiente'::character varying,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    CONSTRAINT reservaciones_cantidad_personas_check CHECK ((cantidad_personas > 0)),
    CONSTRAINT reservaciones_estado_check CHECK (((estado)::text = ANY ((ARRAY['pendiente'::character varying, 'confirmada'::character varying, 'cancelada'::character varying, 'completada'::character varying])::text[])))
);


ALTER TABLE public.reservaciones OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 24607)
-- Name: reservaciones_id_reserva_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reservaciones_id_reserva_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reservaciones_id_reserva_seq OWNER TO postgres;

--
-- TOC entry 5062 (class 0 OID 0)
-- Dependencies: 223
-- Name: reservaciones_id_reserva_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reservaciones_id_reserva_seq OWNED BY public.reservaciones.id_reserva;


--
-- TOC entry 220 (class 1259 OID 24577)
-- Name: tipo_mesa; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tipo_mesa (
    id_tipo_mesa integer NOT NULL,
    descripcion character varying(50) NOT NULL,
    cantidad_sillas integer NOT NULL,
    CONSTRAINT tipo_mesa_cantidad_sillas_check CHECK ((cantidad_sillas > 0))
);


ALTER TABLE public.tipo_mesa OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 24576)
-- Name: tipo_mesa_id_tipo_mesa_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tipo_mesa_id_tipo_mesa_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tipo_mesa_id_tipo_mesa_seq OWNER TO postgres;

--
-- TOC entry 5063 (class 0 OID 0)
-- Dependencies: 219
-- Name: tipo_mesa_id_tipo_mesa_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tipo_mesa_id_tipo_mesa_seq OWNED BY public.tipo_mesa.id_tipo_mesa;


--
-- TOC entry 226 (class 1259 OID 24635)
-- Name: usuarios_admin; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios_admin (
    id_usuario integer NOT NULL,
    nombre character varying(120) NOT NULL,
    email character varying(150) NOT NULL,
    password_hash text NOT NULL,
    rol character varying(30) DEFAULT 'admin'::character varying,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    CONSTRAINT usuarios_admin_rol_check CHECK (((rol)::text = ANY ((ARRAY['admin'::character varying, 'superadmin'::character varying, 'staff'::character varying])::text[])))
);


ALTER TABLE public.usuarios_admin OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 24634)
-- Name: usuarios_admin_id_usuario_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuarios_admin_id_usuario_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuarios_admin_id_usuario_seq OWNER TO postgres;

--
-- TOC entry 5064 (class 0 OID 0)
-- Dependencies: 225
-- Name: usuarios_admin_id_usuario_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuarios_admin_id_usuario_seq OWNED BY public.usuarios_admin.id_usuario;


--
-- TOC entry 4872 (class 2604 OID 24591)
-- Name: mesas id_mesa; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mesas ALTER COLUMN id_mesa SET DEFAULT nextval('public.mesas_id_mesa_seq'::regclass);


--
-- TOC entry 4875 (class 2604 OID 24611)
-- Name: reservaciones id_reserva; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservaciones ALTER COLUMN id_reserva SET DEFAULT nextval('public.reservaciones_id_reserva_seq'::regclass);


--
-- TOC entry 4871 (class 2604 OID 24580)
-- Name: tipo_mesa id_tipo_mesa; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipo_mesa ALTER COLUMN id_tipo_mesa SET DEFAULT nextval('public.tipo_mesa_id_tipo_mesa_seq'::regclass);


--
-- TOC entry 4879 (class 2604 OID 24638)
-- Name: usuarios_admin id_usuario; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios_admin ALTER COLUMN id_usuario SET DEFAULT nextval('public.usuarios_admin_id_usuario_seq'::regclass);


--
-- TOC entry 4894 (class 2606 OID 24599)
-- Name: mesas mesas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mesas
    ADD CONSTRAINT mesas_pkey PRIMARY KEY (id_mesa);


--
-- TOC entry 4899 (class 2606 OID 24625)
-- Name: reservaciones reservaciones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservaciones
    ADD CONSTRAINT reservaciones_pkey PRIMARY KEY (id_reserva);


--
-- TOC entry 4890 (class 2606 OID 24586)
-- Name: tipo_mesa tipo_mesa_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipo_mesa
    ADD CONSTRAINT tipo_mesa_pkey PRIMARY KEY (id_tipo_mesa);


--
-- TOC entry 4903 (class 2606 OID 24653)
-- Name: usuarios_admin usuarios_admin_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios_admin
    ADD CONSTRAINT usuarios_admin_email_key UNIQUE (email);


--
-- TOC entry 4905 (class 2606 OID 24651)
-- Name: usuarios_admin usuarios_admin_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios_admin
    ADD CONSTRAINT usuarios_admin_pkey PRIMARY KEY (id_usuario);


--
-- TOC entry 4891 (class 1259 OID 24605)
-- Name: idx_mesas_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_mesas_estado ON public.mesas USING btree (estado);


--
-- TOC entry 4892 (class 1259 OID 24606)
-- Name: idx_mesas_tipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_mesas_tipo ON public.mesas USING btree (id_tipo_mesa);


--
-- TOC entry 4895 (class 1259 OID 24633)
-- Name: idx_reservaciones_correo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reservaciones_correo ON public.reservaciones USING btree (correo);


--
-- TOC entry 4896 (class 1259 OID 24632)
-- Name: idx_reservaciones_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reservaciones_estado ON public.reservaciones USING btree (estado);


--
-- TOC entry 4897 (class 1259 OID 24631)
-- Name: idx_reservaciones_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_reservaciones_fecha ON public.reservaciones USING btree (fecha, hora);


--
-- TOC entry 4900 (class 1259 OID 24655)
-- Name: idx_usuarios_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_usuarios_active ON public.usuarios_admin USING btree (is_active);


--
-- TOC entry 4901 (class 1259 OID 24654)
-- Name: idx_usuarios_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_usuarios_email ON public.usuarios_admin USING btree (email);


--
-- TOC entry 4906 (class 2606 OID 24600)
-- Name: mesas mesas_id_tipo_mesa_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mesas
    ADD CONSTRAINT mesas_id_tipo_mesa_fkey FOREIGN KEY (id_tipo_mesa) REFERENCES public.tipo_mesa(id_tipo_mesa) ON DELETE RESTRICT;


--
-- TOC entry 4907 (class 2606 OID 24626)
-- Name: reservaciones reservaciones_id_mesa_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservaciones
    ADD CONSTRAINT reservaciones_id_mesa_fkey FOREIGN KEY (id_mesa) REFERENCES public.mesas(id_mesa) ON DELETE SET NULL;


-- Completed on 2025-11-22 22:12:13

--
-- PostgreSQL database dump complete
--

\unrestrict H5isupFJpsG7C6udcsUGqPdlMtLTlpcHmdRGQb6srKbbD9Ac75igTwKKTS5IFuU

