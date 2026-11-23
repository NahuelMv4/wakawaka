--
-- PostgreSQL database dump
--

\restrict YpDktaOC7bJKz62QnI5qh8RLQ4ZhtOi3cHIZgwNfLsf2hkhCy153Zet7eT2Jq4N

-- Dumped from database version 16.14
-- Dumped by pg_dump version 16.14

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public."USUARIO" DROP CONSTRAINT IF EXISTS "USUARIO_sector_id_fkey";
ALTER TABLE IF EXISTS ONLY public."USUARIO" DROP CONSTRAINT IF EXISTS "USUARIO_rol_id_fkey";
ALTER TABLE IF EXISTS ONLY public."SOLICITUD_COMIDA" DROP CONSTRAINT IF EXISTS "SOLICITUD_COMIDA_tipo_menu_id_fkey";
ALTER TABLE IF EXISTS ONLY public."SOLICITUD_COMIDA" DROP CONSTRAINT IF EXISTS "SOLICITUD_COMIDA_personal_id_fkey";
ALTER TABLE IF EXISTS ONLY public."SOLICITUD_COMIDA" DROP CONSTRAINT IF EXISTS "SOLICITUD_COMIDA_pedido_id_fkey";
ALTER TABLE IF EXISTS ONLY public."SOLICITUD_COMIDA" DROP CONSTRAINT IF EXISTS "SOLICITUD_COMIDA_entrega_id_fkey";
ALTER TABLE IF EXISTS ONLY public."ROL_PERMISO" DROP CONSTRAINT IF EXISTS "ROL_PERMISO_rol_id_fkey";
ALTER TABLE IF EXISTS ONLY public."ROL_PERMISO" DROP CONSTRAINT IF EXISTS "ROL_PERMISO_permiso_id_fkey";
ALTER TABLE IF EXISTS ONLY public."REVISION" DROP CONSTRAINT IF EXISTS "REVISION_usuario_id_fkey";
ALTER TABLE IF EXISTS ONLY public."REVISION" DROP CONSTRAINT IF EXISTS "REVISION_pedido_id_fkey";
ALTER TABLE IF EXISTS ONLY public."REGISTRO_CUPO" DROP CONSTRAINT IF EXISTS "REGISTRO_CUPO_solicitud_comida_id_fkey";
ALTER TABLE IF EXISTS ONLY public."REGISTRO_CUPO" DROP CONSTRAINT IF EXISTS "REGISTRO_CUPO_cupo_id_fkey";
ALTER TABLE IF EXISTS ONLY public."PERSONAL" DROP CONSTRAINT IF EXISTS "PERSONAL_tipo_personal_id_fkey";
ALTER TABLE IF EXISTS ONLY public."PERSONAL" DROP CONSTRAINT IF EXISTS "PERSONAL_tipo_menu_id_fkey";
ALTER TABLE IF EXISTS ONLY public."PERSONAL" DROP CONSTRAINT IF EXISTS "PERSONAL_sector_id_fkey";
ALTER TABLE IF EXISTS ONLY public."PEDIDO" DROP CONSTRAINT IF EXISTS "PEDIDO_usuario_id_fkey";
ALTER TABLE IF EXISTS ONLY public."PEDIDO" DROP CONSTRAINT IF EXISTS "PEDIDO_tipo_comida_id_fkey";
ALTER TABLE IF EXISTS ONLY public."PEDIDO" DROP CONSTRAINT IF EXISTS "PEDIDO_sector_id_fkey";
ALTER TABLE IF EXISTS ONLY public."ENTREGA" DROP CONSTRAINT IF EXISTS "ENTREGA_personal_id_fkey";
ALTER TABLE IF EXISTS ONLY public."CUPO" DROP CONSTRAINT IF EXISTS "CUPO_tipo_comida_id_fkey";
ALTER TABLE IF EXISTS ONLY public."CUPO" DROP CONSTRAINT IF EXISTS "CUPO_sector_id_fkey";
ALTER TABLE IF EXISTS ONLY public."CONFIGURACION_SISTEMA" DROP CONSTRAINT IF EXISTS "CONFIGURACION_SISTEMA_actualizado_por_usuario_id_fkey";
ALTER TABLE IF EXISTS ONLY public."USUARIO" DROP CONSTRAINT IF EXISTS "USUARIO_pkey";
ALTER TABLE IF EXISTS ONLY public."USUARIO" DROP CONSTRAINT IF EXISTS "USUARIO_email_key";
ALTER TABLE IF EXISTS ONLY public."USUARIO" DROP CONSTRAINT IF EXISTS "USUARIO_dni_key";
ALTER TABLE IF EXISTS ONLY public."TIPO_PERSONAL" DROP CONSTRAINT IF EXISTS "TIPO_PERSONAL_pkey";
ALTER TABLE IF EXISTS ONLY public."TIPO_PERSONAL" DROP CONSTRAINT IF EXISTS "TIPO_PERSONAL_nombre_key";
ALTER TABLE IF EXISTS ONLY public."TIPO_MENU" DROP CONSTRAINT IF EXISTS "TIPO_MENU_pkey";
ALTER TABLE IF EXISTS ONLY public."TIPO_MENU" DROP CONSTRAINT IF EXISTS "TIPO_MENU_nombre_key";
ALTER TABLE IF EXISTS ONLY public."TIPO_COMIDA" DROP CONSTRAINT IF EXISTS "TIPO_COMIDA_pkey";
ALTER TABLE IF EXISTS ONLY public."TIPO_COMIDA" DROP CONSTRAINT IF EXISTS "TIPO_COMIDA_nombre_key";
ALTER TABLE IF EXISTS ONLY public."SOLICITUD_COMIDA" DROP CONSTRAINT IF EXISTS "SOLICITUD_COMIDA_pkey";
ALTER TABLE IF EXISTS ONLY public."SECTOR" DROP CONSTRAINT IF EXISTS "SECTOR_pkey";
ALTER TABLE IF EXISTS ONLY public."ROL" DROP CONSTRAINT IF EXISTS "ROL_pkey";
ALTER TABLE IF EXISTS ONLY public."ROL" DROP CONSTRAINT IF EXISTS "ROL_nombre_key";
ALTER TABLE IF EXISTS ONLY public."ROL_PERMISO" DROP CONSTRAINT IF EXISTS "ROL_PERMISO_pkey";
ALTER TABLE IF EXISTS ONLY public."REVISION" DROP CONSTRAINT IF EXISTS "REVISION_pkey";
ALTER TABLE IF EXISTS ONLY public."REGISTRO_CUPO" DROP CONSTRAINT IF EXISTS "REGISTRO_CUPO_solicitud_comida_id_key";
ALTER TABLE IF EXISTS ONLY public."REGISTRO_CUPO" DROP CONSTRAINT IF EXISTS "REGISTRO_CUPO_pkey";
ALTER TABLE IF EXISTS ONLY public."PERSONAL" DROP CONSTRAINT IF EXISTS "PERSONAL_pkey";
ALTER TABLE IF EXISTS ONLY public."PERSONAL" DROP CONSTRAINT IF EXISTS "PERSONAL_dni_key";
ALTER TABLE IF EXISTS ONLY public."PERMISO" DROP CONSTRAINT IF EXISTS "PERMISO_pkey";
ALTER TABLE IF EXISTS ONLY public."PERMISO" DROP CONSTRAINT IF EXISTS "PERMISO_codigo_key";
ALTER TABLE IF EXISTS ONLY public."PEDIDO" DROP CONSTRAINT IF EXISTS "PEDIDO_pkey";
ALTER TABLE IF EXISTS ONLY public."ENTREGA" DROP CONSTRAINT IF EXISTS "ENTREGA_pkey";
ALTER TABLE IF EXISTS ONLY public."CUPO" DROP CONSTRAINT IF EXISTS "CUPO_pkey";
ALTER TABLE IF EXISTS ONLY public."CONFIGURACION_SISTEMA" DROP CONSTRAINT IF EXISTS "CONFIGURACION_SISTEMA_pkey";
ALTER TABLE IF EXISTS ONLY public."CONFIGURACION_SISTEMA" DROP CONSTRAINT IF EXISTS "CONFIGURACION_SISTEMA_clave_key";
ALTER TABLE IF EXISTS public."USUARIO" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public."TIPO_PERSONAL" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public."TIPO_MENU" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public."TIPO_COMIDA" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public."SOLICITUD_COMIDA" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public."SECTOR" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public."ROL" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public."REVISION" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public."REGISTRO_CUPO" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public."PERSONAL" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public."PERMISO" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public."PEDIDO" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public."ENTREGA" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public."CUPO" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public."CONFIGURACION_SISTEMA" ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public."USUARIO_id_seq";
DROP TABLE IF EXISTS public."USUARIO";
DROP SEQUENCE IF EXISTS public."TIPO_PERSONAL_id_seq";
DROP TABLE IF EXISTS public."TIPO_PERSONAL";
DROP SEQUENCE IF EXISTS public."TIPO_MENU_id_seq";
DROP TABLE IF EXISTS public."TIPO_MENU";
DROP SEQUENCE IF EXISTS public."TIPO_COMIDA_id_seq";
DROP TABLE IF EXISTS public."TIPO_COMIDA";
DROP SEQUENCE IF EXISTS public."SOLICITUD_COMIDA_id_seq";
DROP TABLE IF EXISTS public."SOLICITUD_COMIDA";
DROP SEQUENCE IF EXISTS public."SECTOR_id_seq";
DROP TABLE IF EXISTS public."SECTOR";
DROP SEQUENCE IF EXISTS public."ROL_id_seq";
DROP TABLE IF EXISTS public."ROL_PERMISO";
DROP TABLE IF EXISTS public."ROL";
DROP SEQUENCE IF EXISTS public."REVISION_id_seq";
DROP TABLE IF EXISTS public."REVISION";
DROP SEQUENCE IF EXISTS public."REGISTRO_CUPO_id_seq";
DROP TABLE IF EXISTS public."REGISTRO_CUPO";
DROP SEQUENCE IF EXISTS public."PERSONAL_id_seq";
DROP TABLE IF EXISTS public."PERSONAL";
DROP SEQUENCE IF EXISTS public."PERMISO_id_seq";
DROP TABLE IF EXISTS public."PERMISO";
DROP SEQUENCE IF EXISTS public."PEDIDO_id_seq";
DROP TABLE IF EXISTS public."PEDIDO";
DROP SEQUENCE IF EXISTS public."ENTREGA_id_seq";
DROP TABLE IF EXISTS public."ENTREGA";
DROP SEQUENCE IF EXISTS public."CUPO_id_seq";
DROP TABLE IF EXISTS public."CUPO";
DROP SEQUENCE IF EXISTS public."CONFIGURACION_SISTEMA_id_seq";
DROP TABLE IF EXISTS public."CONFIGURACION_SISTEMA";
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: CONFIGURACION_SISTEMA; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."CONFIGURACION_SISTEMA" (
    id integer NOT NULL,
    clave character varying NOT NULL,
    paginacion integer NOT NULL,
    horario_corte time without time zone NOT NULL,
    mantenimiento boolean NOT NULL,
    mensaje_mantenimiento character varying,
    actualizado_en timestamp without time zone NOT NULL,
    actualizado_por_usuario_id integer
);


--
-- Name: CONFIGURACION_SISTEMA_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."CONFIGURACION_SISTEMA_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: CONFIGURACION_SISTEMA_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."CONFIGURACION_SISTEMA_id_seq" OWNED BY public."CONFIGURACION_SISTEMA".id;


--
-- Name: CUPO; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."CUPO" (
    id integer NOT NULL,
    cantidad integer NOT NULL,
    creado_en timestamp without time zone NOT NULL,
    actualizado_en timestamp without time zone NOT NULL,
    sector_id integer NOT NULL,
    tipo_comida_id integer NOT NULL
);


--
-- Name: CUPO_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."CUPO_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: CUPO_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."CUPO_id_seq" OWNED BY public."CUPO".id;


--
-- Name: ENTREGA; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."ENTREGA" (
    id integer NOT NULL,
    fecha timestamp without time zone NOT NULL,
    personal_id integer NOT NULL
);


--
-- Name: ENTREGA_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."ENTREGA_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ENTREGA_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."ENTREGA_id_seq" OWNED BY public."ENTREGA".id;


--
-- Name: PEDIDO; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."PEDIDO" (
    id integer NOT NULL,
    fecha_desde timestamp without time zone NOT NULL,
    fecha_hasta timestamp without time zone NOT NULL,
    estado character varying NOT NULL,
    motivo_rechazo text,
    creado_en timestamp without time zone NOT NULL,
    actualizado_en timestamp without time zone NOT NULL,
    sector_id integer NOT NULL,
    tipo_comida_id integer NOT NULL,
    usuario_id integer NOT NULL
);


--
-- Name: PEDIDO_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."PEDIDO_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: PEDIDO_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."PEDIDO_id_seq" OWNED BY public."PEDIDO".id;


--
-- Name: PERMISO; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."PERMISO" (
    id integer NOT NULL,
    codigo character varying(22) NOT NULL
);


--
-- Name: PERMISO_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."PERMISO_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: PERMISO_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."PERMISO_id_seq" OWNED BY public."PERMISO".id;


--
-- Name: PERSONAL; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."PERSONAL" (
    id integer NOT NULL,
    nombre character varying NOT NULL,
    apellido character varying NOT NULL,
    dni character varying NOT NULL,
    activo boolean NOT NULL,
    creado_en timestamp without time zone NOT NULL,
    actualizado_en timestamp without time zone NOT NULL,
    tipo_personal_id integer NOT NULL,
    sector_id integer,
    tipo_menu_id integer NOT NULL
);


--
-- Name: PERSONAL_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."PERSONAL_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: PERSONAL_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."PERSONAL_id_seq" OWNED BY public."PERSONAL".id;


--
-- Name: REGISTRO_CUPO; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."REGISTRO_CUPO" (
    id integer NOT NULL,
    estado character varying NOT NULL,
    fecha timestamp without time zone NOT NULL,
    cupo_historico integer NOT NULL,
    cupo_id integer NOT NULL,
    solicitud_comida_id integer NOT NULL
);


--
-- Name: REGISTRO_CUPO_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."REGISTRO_CUPO_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: REGISTRO_CUPO_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."REGISTRO_CUPO_id_seq" OWNED BY public."REGISTRO_CUPO".id;


--
-- Name: REVISION; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."REVISION" (
    id integer NOT NULL,
    estado character varying NOT NULL,
    revisado_en timestamp without time zone NOT NULL,
    observacion character varying,
    usuario_id integer NOT NULL,
    pedido_id integer NOT NULL
);


--
-- Name: REVISION_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."REVISION_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: REVISION_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."REVISION_id_seq" OWNED BY public."REVISION".id;


--
-- Name: ROL; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."ROL" (
    id integer NOT NULL,
    nombre character varying(24) NOT NULL
);


--
-- Name: ROL_PERMISO; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."ROL_PERMISO" (
    rol_id integer NOT NULL,
    permiso_id integer NOT NULL
);


--
-- Name: ROL_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."ROL_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ROL_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."ROL_id_seq" OWNED BY public."ROL".id;


--
-- Name: SECTOR; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."SECTOR" (
    id integer NOT NULL,
    nombre character varying NOT NULL,
    descripcion character varying NOT NULL,
    activo boolean NOT NULL,
    creado_en timestamp without time zone NOT NULL,
    actualizado_en timestamp without time zone NOT NULL
);


--
-- Name: SECTOR_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."SECTOR_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: SECTOR_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."SECTOR_id_seq" OWNED BY public."SECTOR".id;


--
-- Name: SOLICITUD_COMIDA; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."SOLICITUD_COMIDA" (
    id integer NOT NULL,
    fecha_comida date NOT NULL,
    condicion character varying NOT NULL,
    solicitado_en timestamp without time zone NOT NULL,
    autorizada boolean NOT NULL,
    pedido_id integer NOT NULL,
    personal_id integer NOT NULL,
    tipo_menu_id integer NOT NULL,
    entrega_id integer
);


--
-- Name: SOLICITUD_COMIDA_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."SOLICITUD_COMIDA_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: SOLICITUD_COMIDA_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."SOLICITUD_COMIDA_id_seq" OWNED BY public."SOLICITUD_COMIDA".id;


--
-- Name: TIPO_COMIDA; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."TIPO_COMIDA" (
    id integer NOT NULL,
    nombre character varying(8) NOT NULL,
    hora_inicio time without time zone NOT NULL,
    hora_fin time without time zone NOT NULL
);


--
-- Name: TIPO_COMIDA_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."TIPO_COMIDA_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: TIPO_COMIDA_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."TIPO_COMIDA_id_seq" OWNED BY public."TIPO_COMIDA".id;


--
-- Name: TIPO_MENU; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."TIPO_MENU" (
    id integer NOT NULL,
    nombre character varying(11) NOT NULL
);


--
-- Name: TIPO_MENU_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."TIPO_MENU_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: TIPO_MENU_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."TIPO_MENU_id_seq" OWNED BY public."TIPO_MENU".id;


--
-- Name: TIPO_PERSONAL; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."TIPO_PERSONAL" (
    id integer NOT NULL,
    nombre character varying(13) NOT NULL
);


--
-- Name: TIPO_PERSONAL_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."TIPO_PERSONAL_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: TIPO_PERSONAL_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."TIPO_PERSONAL_id_seq" OWNED BY public."TIPO_PERSONAL".id;


--
-- Name: USUARIO; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."USUARIO" (
    id integer NOT NULL,
    email character varying NOT NULL,
    contrasenia character varying NOT NULL,
    nombre character varying NOT NULL,
    apellido character varying NOT NULL,
    dni character varying NOT NULL,
    activo boolean NOT NULL,
    bloqueado boolean NOT NULL,
    creado_en timestamp without time zone NOT NULL,
    actualizado_en timestamp without time zone NOT NULL,
    rol_id integer NOT NULL,
    sector_id integer NOT NULL
);


--
-- Name: USUARIO_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public."USUARIO_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: USUARIO_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public."USUARIO_id_seq" OWNED BY public."USUARIO".id;


--
-- Name: CONFIGURACION_SISTEMA id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."CONFIGURACION_SISTEMA" ALTER COLUMN id SET DEFAULT nextval('public."CONFIGURACION_SISTEMA_id_seq"'::regclass);


--
-- Name: CUPO id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."CUPO" ALTER COLUMN id SET DEFAULT nextval('public."CUPO_id_seq"'::regclass);


--
-- Name: ENTREGA id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."ENTREGA" ALTER COLUMN id SET DEFAULT nextval('public."ENTREGA_id_seq"'::regclass);


--
-- Name: PEDIDO id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."PEDIDO" ALTER COLUMN id SET DEFAULT nextval('public."PEDIDO_id_seq"'::regclass);


--
-- Name: PERMISO id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."PERMISO" ALTER COLUMN id SET DEFAULT nextval('public."PERMISO_id_seq"'::regclass);


--
-- Name: PERSONAL id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."PERSONAL" ALTER COLUMN id SET DEFAULT nextval('public."PERSONAL_id_seq"'::regclass);


--
-- Name: REGISTRO_CUPO id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."REGISTRO_CUPO" ALTER COLUMN id SET DEFAULT nextval('public."REGISTRO_CUPO_id_seq"'::regclass);


--
-- Name: REVISION id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."REVISION" ALTER COLUMN id SET DEFAULT nextval('public."REVISION_id_seq"'::regclass);


--
-- Name: ROL id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."ROL" ALTER COLUMN id SET DEFAULT nextval('public."ROL_id_seq"'::regclass);


--
-- Name: SECTOR id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."SECTOR" ALTER COLUMN id SET DEFAULT nextval('public."SECTOR_id_seq"'::regclass);


--
-- Name: SOLICITUD_COMIDA id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."SOLICITUD_COMIDA" ALTER COLUMN id SET DEFAULT nextval('public."SOLICITUD_COMIDA_id_seq"'::regclass);


--
-- Name: TIPO_COMIDA id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."TIPO_COMIDA" ALTER COLUMN id SET DEFAULT nextval('public."TIPO_COMIDA_id_seq"'::regclass);


--
-- Name: TIPO_MENU id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."TIPO_MENU" ALTER COLUMN id SET DEFAULT nextval('public."TIPO_MENU_id_seq"'::regclass);


--
-- Name: TIPO_PERSONAL id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."TIPO_PERSONAL" ALTER COLUMN id SET DEFAULT nextval('public."TIPO_PERSONAL_id_seq"'::regclass);


--
-- Name: USUARIO id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."USUARIO" ALTER COLUMN id SET DEFAULT nextval('public."USUARIO_id_seq"'::regclass);


--
-- Data for Name: CONFIGURACION_SISTEMA; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public."CONFIGURACION_SISTEMA" VALUES (1, 'sys_config', 25, '18:00:00', false, 'Sistema actualmente en mantenimiento, disculpe las molestias.', '2026-11-21 03:48:36.511131', NULL);


--
-- Data for Name: CUPO; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public."CUPO" VALUES (1, 3, '2026-11-21 03:48:36.584406', '2026-11-21 03:48:36.58441', 6, 1);
INSERT INTO public."CUPO" VALUES (2, 2, '2026-11-21 03:48:36.592277', '2026-11-21 03:48:36.592281', 6, 2);
INSERT INTO public."CUPO" VALUES (3, 3, '2026-11-21 03:48:36.600296', '2026-11-21 03:48:36.6003', 6, 3);
INSERT INTO public."CUPO" VALUES (4, 2, '2026-11-21 03:48:36.610214', '2026-11-21 03:48:36.610218', 6, 4);


--
-- Data for Name: ENTREGA; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: PEDIDO; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public."PEDIDO" VALUES (1, '2026-11-23 00:00:00', '2026-11-23 00:00:00', 'Confirmado', NULL, '2026-11-21 03:48:36.644666', '2026-11-21 03:48:36.64467', 6, 2, 4);
INSERT INTO public."PEDIDO" VALUES (2, '2026-11-21 03:48:36.678202', '2026-11-21 03:48:36.678202', 'autorizado', NULL, '2026-11-21 03:48:36.680433', '2026-11-21 03:48:36.680439', 6, 1, 4);
INSERT INTO public."PEDIDO" VALUES (3, '2026-11-21 03:48:36.678202', '2026-11-21 03:48:36.678202', 'autorizado', NULL, '2026-11-21 03:48:36.682861', '2026-11-21 03:48:36.682865', 6, 2, 4);
INSERT INTO public."PEDIDO" VALUES (4, '2026-11-21 03:48:36.678202', '2026-11-21 03:48:36.678202', 'autorizado', NULL, '2026-11-21 03:48:36.69257', '2026-11-21 03:48:36.692574', 6, 3, 4);
INSERT INTO public."PEDIDO" VALUES (5, '2026-11-21 03:48:36.678202', '2026-11-21 03:48:36.678202', 'autorizado', NULL, '2026-11-21 03:48:36.698679', '2026-11-21 03:48:36.698683', 6, 4, 4);


--
-- Data for Name: PERMISO; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public."PERMISO" VALUES (1, 'user_index');
INSERT INTO public."PERMISO" VALUES (2, 'user_new');
INSERT INTO public."PERMISO" VALUES (3, 'user_show');
INSERT INTO public."PERMISO" VALUES (4, 'user_update');
INSERT INTO public."PERMISO" VALUES (5, 'user_destroy');
INSERT INTO public."PERMISO" VALUES (6, 'user_block');
INSERT INTO public."PERMISO" VALUES (7, 'user_unlock');
INSERT INTO public."PERMISO" VALUES (8, 'config_index');
INSERT INTO public."PERMISO" VALUES (9, 'config_activate');
INSERT INTO public."PERMISO" VALUES (10, 'config_deactivate');
INSERT INTO public."PERMISO" VALUES (11, 'personal_index');
INSERT INTO public."PERMISO" VALUES (12, 'personal_create');
INSERT INTO public."PERMISO" VALUES (13, 'personal_show');
INSERT INTO public."PERMISO" VALUES (14, 'personal_update');
INSERT INTO public."PERMISO" VALUES (15, 'personal_destroy');
INSERT INTO public."PERMISO" VALUES (16, 'personal_csv');
INSERT INTO public."PERMISO" VALUES (17, 'cupo_index');
INSERT INTO public."PERMISO" VALUES (18, 'cupo_show');
INSERT INTO public."PERMISO" VALUES (19, 'cupo_create');
INSERT INTO public."PERMISO" VALUES (20, 'cupo_update');
INSERT INTO public."PERMISO" VALUES (21, 'cupo_destroy');
INSERT INTO public."PERMISO" VALUES (22, 'pedido_index');
INSERT INTO public."PERMISO" VALUES (23, 'pedido_show');
INSERT INTO public."PERMISO" VALUES (24, 'pedido_create');
INSERT INTO public."PERMISO" VALUES (25, 'pedido_update');
INSERT INTO public."PERMISO" VALUES (26, 'pedido_destroy');
INSERT INTO public."PERMISO" VALUES (27, 'sector_index');
INSERT INTO public."PERMISO" VALUES (28, 'sector_update');
INSERT INTO public."PERMISO" VALUES (29, 'sector_create');
INSERT INTO public."PERMISO" VALUES (30, 'sector_activate');
INSERT INTO public."PERMISO" VALUES (31, 'sector_deactivate');
INSERT INTO public."PERMISO" VALUES (32, 'autorizacion_index');
INSERT INTO public."PERMISO" VALUES (33, 'summary_requests');
INSERT INTO public."PERMISO" VALUES (34, 'summary_authorizations');
INSERT INTO public."PERMISO" VALUES (35, 'summary_deliveries');
INSERT INTO public."PERMISO" VALUES (36, 'delivery_summary');


--
-- Data for Name: PERSONAL; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public."PERSONAL" VALUES (1, 'Brian', 'Perez', '37825229', true, '2026-11-21 03:48:36.529738', '2026-11-21 03:48:36.529743', 1, 1, 1);
INSERT INTO public."PERSONAL" VALUES (2, 'Sergui', 'Alvarez', '39015029', true, '2026-11-21 03:48:36.539488', '2026-11-21 03:48:36.539492', 2, NULL, 2);
INSERT INTO public."PERSONAL" VALUES (3, 'Max', 'Holtz', '38385738', true, '2026-11-21 03:48:36.547857', '2026-11-21 03:48:36.547861', 1, 5, 3);
INSERT INTO public."PERSONAL" VALUES (4, 'Sofía', 'Fernández', '35112233', true, '2026-11-21 03:48:36.555527', '2026-11-21 03:48:36.555531', 1, 6, 1);
INSERT INTO public."PERSONAL" VALUES (5, 'Martín', 'Gómez', '36445566', true, '2026-11-21 03:48:36.563343', '2026-11-21 03:48:36.563348', 1, 6, 2);
INSERT INTO public."PERSONAL" VALUES (6, 'Sofía', 'Acosta', '38778899', true, '2026-11-21 03:48:36.572067', '2026-11-21 03:48:36.572072', 1, 6, 3);


--
-- Data for Name: REGISTRO_CUPO; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public."REGISTRO_CUPO" VALUES (1, 'Regular', '2026-11-21 03:48:36.654281', 2, 2, 1);
INSERT INTO public."REGISTRO_CUPO" VALUES (2, 'Regular', '2026-11-21 03:48:36.658615', 2, 2, 2);
INSERT INTO public."REGISTRO_CUPO" VALUES (3, 'Excepción', '2026-11-21 03:48:36.660043', 2, 2, 3);


--
-- Data for Name: REVISION; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: ROL; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public."ROL" VALUES (1, 'Administrador');
INSERT INTO public."ROL" VALUES (2, 'Jefe de Servicio');
INSERT INTO public."ROL" VALUES (3, 'Sector Comedor');
INSERT INTO public."ROL" VALUES (4, 'Servicio de Alimentación');


--
-- Data for Name: ROL_PERMISO; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public."ROL_PERMISO" VALUES (1, 2);
INSERT INTO public."ROL_PERMISO" VALUES (1, 3);
INSERT INTO public."ROL_PERMISO" VALUES (1, 5);
INSERT INTO public."ROL_PERMISO" VALUES (1, 6);
INSERT INTO public."ROL_PERMISO" VALUES (1, 4);
INSERT INTO public."ROL_PERMISO" VALUES (1, 7);
INSERT INTO public."ROL_PERMISO" VALUES (1, 1);
INSERT INTO public."ROL_PERMISO" VALUES (1, 10);
INSERT INTO public."ROL_PERMISO" VALUES (1, 8);
INSERT INTO public."ROL_PERMISO" VALUES (1, 9);
INSERT INTO public."ROL_PERMISO" VALUES (1, 11);
INSERT INTO public."ROL_PERMISO" VALUES (1, 12);
INSERT INTO public."ROL_PERMISO" VALUES (1, 14);
INSERT INTO public."ROL_PERMISO" VALUES (1, 16);
INSERT INTO public."ROL_PERMISO" VALUES (1, 13);
INSERT INTO public."ROL_PERMISO" VALUES (1, 15);
INSERT INTO public."ROL_PERMISO" VALUES (1, 28);
INSERT INTO public."ROL_PERMISO" VALUES (1, 30);
INSERT INTO public."ROL_PERMISO" VALUES (1, 27);
INSERT INTO public."ROL_PERMISO" VALUES (1, 29);
INSERT INTO public."ROL_PERMISO" VALUES (1, 31);
INSERT INTO public."ROL_PERMISO" VALUES (2, 26);
INSERT INTO public."ROL_PERMISO" VALUES (2, 11);
INSERT INTO public."ROL_PERMISO" VALUES (2, 12);
INSERT INTO public."ROL_PERMISO" VALUES (2, 14);
INSERT INTO public."ROL_PERMISO" VALUES (2, 23);
INSERT INTO public."ROL_PERMISO" VALUES (2, 25);
INSERT INTO public."ROL_PERMISO" VALUES (2, 18);
INSERT INTO public."ROL_PERMISO" VALUES (2, 13);
INSERT INTO public."ROL_PERMISO" VALUES (2, 22);
INSERT INTO public."ROL_PERMISO" VALUES (2, 15);
INSERT INTO public."ROL_PERMISO" VALUES (2, 24);
INSERT INTO public."ROL_PERMISO" VALUES (2, 17);
INSERT INTO public."ROL_PERMISO" VALUES (2, 33);
INSERT INTO public."ROL_PERMISO" VALUES (3, 11);
INSERT INTO public."ROL_PERMISO" VALUES (3, 12);
INSERT INTO public."ROL_PERMISO" VALUES (3, 14);
INSERT INTO public."ROL_PERMISO" VALUES (3, 16);
INSERT INTO public."ROL_PERMISO" VALUES (3, 36);
INSERT INTO public."ROL_PERMISO" VALUES (3, 13);
INSERT INTO public."ROL_PERMISO" VALUES (3, 15);
INSERT INTO public."ROL_PERMISO" VALUES (4, 19);
INSERT INTO public."ROL_PERMISO" VALUES (4, 11);
INSERT INTO public."ROL_PERMISO" VALUES (4, 12);
INSERT INTO public."ROL_PERMISO" VALUES (4, 35);
INSERT INTO public."ROL_PERMISO" VALUES (4, 21);
INSERT INTO public."ROL_PERMISO" VALUES (4, 33);
INSERT INTO public."ROL_PERMISO" VALUES (4, 14);
INSERT INTO public."ROL_PERMISO" VALUES (4, 16);
INSERT INTO public."ROL_PERMISO" VALUES (4, 32);
INSERT INTO public."ROL_PERMISO" VALUES (4, 34);
INSERT INTO public."ROL_PERMISO" VALUES (4, 18);
INSERT INTO public."ROL_PERMISO" VALUES (4, 20);
INSERT INTO public."ROL_PERMISO" VALUES (4, 36);
INSERT INTO public."ROL_PERMISO" VALUES (4, 13);
INSERT INTO public."ROL_PERMISO" VALUES (4, 15);
INSERT INTO public."ROL_PERMISO" VALUES (4, 17);


--
-- Data for Name: SECTOR; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public."SECTOR" VALUES (1, 'Quirófanos', 'Salas de cirugía general, cirugías programadas y de urgencia.', true, '2026-11-21 03:48:34.463242', '2026-11-21 03:48:34.463248');
INSERT INTO public."SECTOR" VALUES (2, 'Guardia', ' Sector destinado a la atención de urgencias, emergencias médicas y traumatológicas con unidades de shockroom y camas de observación.', true, '2026-11-21 03:48:34.4694', '2026-11-21 03:48:34.469403');
INSERT INTO public."SECTOR" VALUES (3, 'Internación', 'Habitaciones generales para pacientes que requieren cuidado continuo, dividido en clínica médica, cirugía, maternidad o áreas críticas.', true, '2026-11-21 03:48:34.47369', '2026-11-21 03:48:34.473694');
INSERT INTO public."SECTOR" VALUES (4, 'Consultorios Externos', 'Área dedicada a la atención programada de diversas especialidades médicas mediante turnos previos.', true, '2026-11-21 03:48:34.478313', '2026-11-21 03:48:34.478316');
INSERT INTO public."SECTOR" VALUES (5, 'Terapia Intensiva y Unidad Coronaria', 'Sectores de alta complejidad equipados con soporte vital para pacientes en estado crítico.', true, '2026-11-21 03:48:34.483155', '2026-11-21 03:48:34.483159');
INSERT INTO public."SECTOR" VALUES (6, 'Diagnóstico por Imágenes', 'Servicios de radiología, ecografía, tomografía computada y mamografías.', true, '2026-11-21 03:48:34.488133', '2026-11-21 03:48:34.488135');


--
-- Data for Name: SOLICITUD_COMIDA; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public."SOLICITUD_COMIDA" VALUES (1, '2026-11-23', 'Regular', '2026-11-21 03:48:36.647602', false, 1, 4, 1, NULL);
INSERT INTO public."SOLICITUD_COMIDA" VALUES (2, '2026-11-23', 'Regular', '2026-11-21 03:48:36.651911', false, 1, 5, 2, NULL);
INSERT INTO public."SOLICITUD_COMIDA" VALUES (3, '2026-11-23', 'Excepción', '2026-11-21 03:48:36.657155', false, 1, 6, 3, NULL);
INSERT INTO public."SOLICITUD_COMIDA" VALUES (4, '2026-11-21', 'autorizado', '2026-11-21 03:48:36.685695', false, 2, 4, 1, NULL);
INSERT INTO public."SOLICITUD_COMIDA" VALUES (5, '2026-11-21', 'autorizado', '2026-11-21 03:48:36.685699', false, 2, 5, 2, NULL);
INSERT INTO public."SOLICITUD_COMIDA" VALUES (6, '2026-11-21', 'autorizado', '2026-11-21 03:48:36.6857', false, 2, 6, 3, NULL);
INSERT INTO public."SOLICITUD_COMIDA" VALUES (7, '2026-11-21', 'autorizado', '2026-11-21 03:48:36.68857', false, 3, 4, 1, NULL);
INSERT INTO public."SOLICITUD_COMIDA" VALUES (8, '2026-11-21', 'autorizado', '2026-11-21 03:48:36.688574', false, 3, 5, 2, NULL);
INSERT INTO public."SOLICITUD_COMIDA" VALUES (9, '2026-11-21', 'autorizado', '2026-11-21 03:48:36.694588', false, 4, 4, 1, NULL);
INSERT INTO public."SOLICITUD_COMIDA" VALUES (10, '2026-11-21', 'autorizado', '2026-11-21 03:48:36.694591', false, 4, 5, 2, NULL);
INSERT INTO public."SOLICITUD_COMIDA" VALUES (11, '2026-11-21', 'autorizado', '2026-11-21 03:48:36.694592', false, 4, 6, 3, NULL);
INSERT INTO public."SOLICITUD_COMIDA" VALUES (12, '2026-11-21', 'autorizado', '2026-11-21 03:48:36.701238', false, 5, 4, 1, NULL);
INSERT INTO public."SOLICITUD_COMIDA" VALUES (13, '2026-11-21', 'autorizado', '2026-11-21 03:48:36.701244', false, 5, 6, 3, NULL);


--
-- Data for Name: TIPO_COMIDA; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public."TIPO_COMIDA" VALUES (1, 'Desayuno', '08:00:00', '12:00:00');
INSERT INTO public."TIPO_COMIDA" VALUES (2, 'Almuerzo', '12:00:00', '15:00:00');
INSERT INTO public."TIPO_COMIDA" VALUES (3, 'Merienda', '15:00:00', '20:00:00');
INSERT INTO public."TIPO_COMIDA" VALUES (4, 'Cena', '20:00:00', '23:00:00');


--
-- Data for Name: TIPO_MENU; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public."TIPO_MENU" VALUES (1, 'General');
INSERT INTO public."TIPO_MENU" VALUES (2, 'Vegetariano');
INSERT INTO public."TIPO_MENU" VALUES (3, 'Celiaco');


--
-- Data for Name: TIPO_PERSONAL; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public."TIPO_PERSONAL" VALUES (1, 'Personal Fijo');
INSERT INTO public."TIPO_PERSONAL" VALUES (2, 'Residente');


--
-- Data for Name: USUARIO; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public."USUARIO" VALUES (1, 'user1@gmail.com', '$2b$12$II79nopRoYN.xiK1io8HIuVrPhdi2TFZKU.b0yRmxGe.IBwGlHe/S', 'Brian', 'Perez', '37825229', true, false, '2026-11-21 03:48:35.383849', '2026-11-21 03:48:35.383854', 1, 2);
INSERT INTO public."USUARIO" VALUES (2, 'user2@gmail.com', '$2b$12$CZIFvdSWdyfP70ttYveLMeRvizKKnPhWpNnmlxGYF5py9dGGJhzoO', 'Julian', 'Alvarez', '40875269', true, false, '2026-11-21 03:48:35.663251', '2026-11-21 03:48:35.663258', 4, 3);
INSERT INTO public."USUARIO" VALUES (3, 'user3@gmail.com', '$2b$12$UjXmLadIV18KUcToNSqPqeQQ04mbn8M7JM.jxJj2uvzGZP8GYo/By', 'Lisandro', 'Quiroga', '34811322', true, false, '2026-11-21 03:48:35.927365', '2026-11-21 03:48:35.927368', 3, 6);
INSERT INTO public."USUARIO" VALUES (4, 'user4@gmail.com', '$2b$12$SgHFclYPHIMGiG9hoRkUVep0T6SUdUJDgQVfq22t1KB1CHdVskN4e', 'Enzo', 'Almeida', '40234768', true, false, '2026-11-21 03:48:36.236805', '2026-11-21 03:48:36.236808', 2, 6);
INSERT INTO public."USUARIO" VALUES (5, 'ezequielb.perez@gmail.com', '$2b$12$ezaePyT0TEaQR1R2zOOj1ufFeA7klBULBBEg8S7Y9TtkSCVzNW.c2', 'Brian', 'Perez', '37234768', true, false, '2026-11-21 03:48:36.506297', '2026-11-21 03:48:36.5063', 2, 6);


--
-- Name: CONFIGURACION_SISTEMA_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public."CONFIGURACION_SISTEMA_id_seq"', 1, true);


--
-- Name: CUPO_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public."CUPO_id_seq"', 4, true);


--
-- Name: ENTREGA_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public."ENTREGA_id_seq"', 1, false);


--
-- Name: PEDIDO_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public."PEDIDO_id_seq"', 5, true);


--
-- Name: PERMISO_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public."PERMISO_id_seq"', 36, true);


--
-- Name: PERSONAL_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public."PERSONAL_id_seq"', 6, true);


--
-- Name: REGISTRO_CUPO_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public."REGISTRO_CUPO_id_seq"', 3, true);


--
-- Name: REVISION_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public."REVISION_id_seq"', 1, false);


--
-- Name: ROL_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public."ROL_id_seq"', 4, true);


--
-- Name: SECTOR_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public."SECTOR_id_seq"', 6, true);


--
-- Name: SOLICITUD_COMIDA_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public."SOLICITUD_COMIDA_id_seq"', 13, true);


--
-- Name: TIPO_COMIDA_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public."TIPO_COMIDA_id_seq"', 4, true);


--
-- Name: TIPO_MENU_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public."TIPO_MENU_id_seq"', 3, true);


--
-- Name: TIPO_PERSONAL_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public."TIPO_PERSONAL_id_seq"', 2, true);


--
-- Name: USUARIO_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public."USUARIO_id_seq"', 5, true);


--
-- Name: CONFIGURACION_SISTEMA CONFIGURACION_SISTEMA_clave_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."CONFIGURACION_SISTEMA"
    ADD CONSTRAINT "CONFIGURACION_SISTEMA_clave_key" UNIQUE (clave);


--
-- Name: CONFIGURACION_SISTEMA CONFIGURACION_SISTEMA_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."CONFIGURACION_SISTEMA"
    ADD CONSTRAINT "CONFIGURACION_SISTEMA_pkey" PRIMARY KEY (id);


--
-- Name: CUPO CUPO_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."CUPO"
    ADD CONSTRAINT "CUPO_pkey" PRIMARY KEY (id);


--
-- Name: ENTREGA ENTREGA_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."ENTREGA"
    ADD CONSTRAINT "ENTREGA_pkey" PRIMARY KEY (id);


--
-- Name: PEDIDO PEDIDO_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."PEDIDO"
    ADD CONSTRAINT "PEDIDO_pkey" PRIMARY KEY (id);


--
-- Name: PERMISO PERMISO_codigo_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."PERMISO"
    ADD CONSTRAINT "PERMISO_codigo_key" UNIQUE (codigo);


--
-- Name: PERMISO PERMISO_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."PERMISO"
    ADD CONSTRAINT "PERMISO_pkey" PRIMARY KEY (id);


--
-- Name: PERSONAL PERSONAL_dni_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."PERSONAL"
    ADD CONSTRAINT "PERSONAL_dni_key" UNIQUE (dni);


--
-- Name: PERSONAL PERSONAL_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."PERSONAL"
    ADD CONSTRAINT "PERSONAL_pkey" PRIMARY KEY (id);


--
-- Name: REGISTRO_CUPO REGISTRO_CUPO_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."REGISTRO_CUPO"
    ADD CONSTRAINT "REGISTRO_CUPO_pkey" PRIMARY KEY (id);


--
-- Name: REGISTRO_CUPO REGISTRO_CUPO_solicitud_comida_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."REGISTRO_CUPO"
    ADD CONSTRAINT "REGISTRO_CUPO_solicitud_comida_id_key" UNIQUE (solicitud_comida_id);


--
-- Name: REVISION REVISION_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."REVISION"
    ADD CONSTRAINT "REVISION_pkey" PRIMARY KEY (id);


--
-- Name: ROL_PERMISO ROL_PERMISO_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."ROL_PERMISO"
    ADD CONSTRAINT "ROL_PERMISO_pkey" PRIMARY KEY (rol_id, permiso_id);


--
-- Name: ROL ROL_nombre_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."ROL"
    ADD CONSTRAINT "ROL_nombre_key" UNIQUE (nombre);


--
-- Name: ROL ROL_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."ROL"
    ADD CONSTRAINT "ROL_pkey" PRIMARY KEY (id);


--
-- Name: SECTOR SECTOR_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."SECTOR"
    ADD CONSTRAINT "SECTOR_pkey" PRIMARY KEY (id);


--
-- Name: SOLICITUD_COMIDA SOLICITUD_COMIDA_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."SOLICITUD_COMIDA"
    ADD CONSTRAINT "SOLICITUD_COMIDA_pkey" PRIMARY KEY (id);


--
-- Name: TIPO_COMIDA TIPO_COMIDA_nombre_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."TIPO_COMIDA"
    ADD CONSTRAINT "TIPO_COMIDA_nombre_key" UNIQUE (nombre);


--
-- Name: TIPO_COMIDA TIPO_COMIDA_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."TIPO_COMIDA"
    ADD CONSTRAINT "TIPO_COMIDA_pkey" PRIMARY KEY (id);


--
-- Name: TIPO_MENU TIPO_MENU_nombre_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."TIPO_MENU"
    ADD CONSTRAINT "TIPO_MENU_nombre_key" UNIQUE (nombre);


--
-- Name: TIPO_MENU TIPO_MENU_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."TIPO_MENU"
    ADD CONSTRAINT "TIPO_MENU_pkey" PRIMARY KEY (id);


--
-- Name: TIPO_PERSONAL TIPO_PERSONAL_nombre_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."TIPO_PERSONAL"
    ADD CONSTRAINT "TIPO_PERSONAL_nombre_key" UNIQUE (nombre);


--
-- Name: TIPO_PERSONAL TIPO_PERSONAL_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."TIPO_PERSONAL"
    ADD CONSTRAINT "TIPO_PERSONAL_pkey" PRIMARY KEY (id);


--
-- Name: USUARIO USUARIO_dni_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."USUARIO"
    ADD CONSTRAINT "USUARIO_dni_key" UNIQUE (dni);


--
-- Name: USUARIO USUARIO_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."USUARIO"
    ADD CONSTRAINT "USUARIO_email_key" UNIQUE (email);


--
-- Name: USUARIO USUARIO_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."USUARIO"
    ADD CONSTRAINT "USUARIO_pkey" PRIMARY KEY (id);


--
-- Name: CONFIGURACION_SISTEMA CONFIGURACION_SISTEMA_actualizado_por_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."CONFIGURACION_SISTEMA"
    ADD CONSTRAINT "CONFIGURACION_SISTEMA_actualizado_por_usuario_id_fkey" FOREIGN KEY (actualizado_por_usuario_id) REFERENCES public."USUARIO"(id);


--
-- Name: CUPO CUPO_sector_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."CUPO"
    ADD CONSTRAINT "CUPO_sector_id_fkey" FOREIGN KEY (sector_id) REFERENCES public."SECTOR"(id);


--
-- Name: CUPO CUPO_tipo_comida_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."CUPO"
    ADD CONSTRAINT "CUPO_tipo_comida_id_fkey" FOREIGN KEY (tipo_comida_id) REFERENCES public."TIPO_COMIDA"(id);


--
-- Name: ENTREGA ENTREGA_personal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."ENTREGA"
    ADD CONSTRAINT "ENTREGA_personal_id_fkey" FOREIGN KEY (personal_id) REFERENCES public."PERSONAL"(id);


--
-- Name: PEDIDO PEDIDO_sector_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."PEDIDO"
    ADD CONSTRAINT "PEDIDO_sector_id_fkey" FOREIGN KEY (sector_id) REFERENCES public."SECTOR"(id);


--
-- Name: PEDIDO PEDIDO_tipo_comida_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."PEDIDO"
    ADD CONSTRAINT "PEDIDO_tipo_comida_id_fkey" FOREIGN KEY (tipo_comida_id) REFERENCES public."TIPO_COMIDA"(id);


--
-- Name: PEDIDO PEDIDO_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."PEDIDO"
    ADD CONSTRAINT "PEDIDO_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES public."USUARIO"(id);


--
-- Name: PERSONAL PERSONAL_sector_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."PERSONAL"
    ADD CONSTRAINT "PERSONAL_sector_id_fkey" FOREIGN KEY (sector_id) REFERENCES public."SECTOR"(id);


--
-- Name: PERSONAL PERSONAL_tipo_menu_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."PERSONAL"
    ADD CONSTRAINT "PERSONAL_tipo_menu_id_fkey" FOREIGN KEY (tipo_menu_id) REFERENCES public."TIPO_MENU"(id);


--
-- Name: PERSONAL PERSONAL_tipo_personal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."PERSONAL"
    ADD CONSTRAINT "PERSONAL_tipo_personal_id_fkey" FOREIGN KEY (tipo_personal_id) REFERENCES public."TIPO_PERSONAL"(id);


--
-- Name: REGISTRO_CUPO REGISTRO_CUPO_cupo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."REGISTRO_CUPO"
    ADD CONSTRAINT "REGISTRO_CUPO_cupo_id_fkey" FOREIGN KEY (cupo_id) REFERENCES public."CUPO"(id);


--
-- Name: REGISTRO_CUPO REGISTRO_CUPO_solicitud_comida_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."REGISTRO_CUPO"
    ADD CONSTRAINT "REGISTRO_CUPO_solicitud_comida_id_fkey" FOREIGN KEY (solicitud_comida_id) REFERENCES public."SOLICITUD_COMIDA"(id);


--
-- Name: REVISION REVISION_pedido_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."REVISION"
    ADD CONSTRAINT "REVISION_pedido_id_fkey" FOREIGN KEY (pedido_id) REFERENCES public."PEDIDO"(id);


--
-- Name: REVISION REVISION_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."REVISION"
    ADD CONSTRAINT "REVISION_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES public."USUARIO"(id);


--
-- Name: ROL_PERMISO ROL_PERMISO_permiso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."ROL_PERMISO"
    ADD CONSTRAINT "ROL_PERMISO_permiso_id_fkey" FOREIGN KEY (permiso_id) REFERENCES public."PERMISO"(id);


--
-- Name: ROL_PERMISO ROL_PERMISO_rol_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."ROL_PERMISO"
    ADD CONSTRAINT "ROL_PERMISO_rol_id_fkey" FOREIGN KEY (rol_id) REFERENCES public."ROL"(id);


--
-- Name: SOLICITUD_COMIDA SOLICITUD_COMIDA_entrega_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."SOLICITUD_COMIDA"
    ADD CONSTRAINT "SOLICITUD_COMIDA_entrega_id_fkey" FOREIGN KEY (entrega_id) REFERENCES public."ENTREGA"(id);


--
-- Name: SOLICITUD_COMIDA SOLICITUD_COMIDA_pedido_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."SOLICITUD_COMIDA"
    ADD CONSTRAINT "SOLICITUD_COMIDA_pedido_id_fkey" FOREIGN KEY (pedido_id) REFERENCES public."PEDIDO"(id);


--
-- Name: SOLICITUD_COMIDA SOLICITUD_COMIDA_personal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."SOLICITUD_COMIDA"
    ADD CONSTRAINT "SOLICITUD_COMIDA_personal_id_fkey" FOREIGN KEY (personal_id) REFERENCES public."PERSONAL"(id);


--
-- Name: SOLICITUD_COMIDA SOLICITUD_COMIDA_tipo_menu_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."SOLICITUD_COMIDA"
    ADD CONSTRAINT "SOLICITUD_COMIDA_tipo_menu_id_fkey" FOREIGN KEY (tipo_menu_id) REFERENCES public."TIPO_MENU"(id);


--
-- Name: USUARIO USUARIO_rol_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."USUARIO"
    ADD CONSTRAINT "USUARIO_rol_id_fkey" FOREIGN KEY (rol_id) REFERENCES public."ROL"(id);


--
-- Name: USUARIO USUARIO_sector_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."USUARIO"
    ADD CONSTRAINT "USUARIO_sector_id_fkey" FOREIGN KEY (sector_id) REFERENCES public."SECTOR"(id);


--
-- PostgreSQL database dump complete
--

\unrestrict YpDktaOC7bJKz62QnI5qh8RLQ4ZhtOi3cHIZgwNfLsf2hkhCy153Zet7eT2Jq4N
