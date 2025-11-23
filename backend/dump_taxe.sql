--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

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
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: etat_collecteur_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.etat_collecteur_enum AS ENUM (
    'connecte',
    'deconnecte'
);


ALTER TYPE public.etat_collecteur_enum OWNER TO postgres;

--
-- Name: periodicite_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.periodicite_enum AS ENUM (
    'journaliere',
    'hebdomadaire',
    'mensuelle',
    'trimestrielle'
);


ALTER TYPE public.periodicite_enum OWNER TO postgres;

--
-- Name: role_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.role_enum AS ENUM (
    'admin',
    'agent_back_office',
    'agent_front_office',
    'controleur_interne',
    'collecteur'
);


ALTER TYPE public.role_enum OWNER TO postgres;

--
-- Name: statut_collecte_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.statut_collecte_enum AS ENUM (
    'pending',
    'completed',
    'failed',
    'cancelled'
);


ALTER TYPE public.statut_collecte_enum OWNER TO postgres;

--
-- Name: statut_collecteur_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.statut_collecteur_enum AS ENUM (
    'active',
    'desactive'
);


ALTER TYPE public.statut_collecteur_enum OWNER TO postgres;

--
-- Name: type_paiement_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.type_paiement_enum AS ENUM (
    'especes',
    'mobile_money',
    'carte'
);


ALTER TYPE public.type_paiement_enum OWNER TO postgres;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: affectation_taxe; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.affectation_taxe (
    id integer NOT NULL,
    contribuable_id integer NOT NULL,
    taxe_id integer NOT NULL,
    date_debut timestamp without time zone NOT NULL,
    date_fin timestamp without time zone,
    montant_custom numeric(12,2),
    actif boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.affectation_taxe OWNER TO postgres;

--
-- Name: TABLE affectation_taxe; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.affectation_taxe IS 'Affectation d''une taxe Ã  un contribuable';


--
-- Name: affectation_taxe_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.affectation_taxe_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.affectation_taxe_id_seq OWNER TO postgres;

--
-- Name: affectation_taxe_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.affectation_taxe_id_seq OWNED BY public.affectation_taxe.id;


--
-- Name: arrondissement; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.arrondissement (
    id integer NOT NULL,
    nom character varying(100) NOT NULL,
    code character varying(20) NOT NULL,
    commune_id integer NOT NULL,
    description text,
    actif boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.arrondissement OWNER TO postgres;

--
-- Name: arrondissement_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.arrondissement_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.arrondissement_id_seq OWNER TO postgres;

--
-- Name: arrondissement_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.arrondissement_id_seq OWNED BY public.arrondissement.id;


--
-- Name: collecteur; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.collecteur (
    id integer NOT NULL,
    nom character varying(100) NOT NULL,
    prenom character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    telephone character varying(20) NOT NULL,
    matricule character varying(50) NOT NULL,
    statut public.statut_collecteur_enum DEFAULT 'active'::public.statut_collecteur_enum,
    etat public.etat_collecteur_enum DEFAULT 'deconnecte'::public.etat_collecteur_enum,
    zone_id integer,
    date_derniere_connexion timestamp without time zone,
    date_derniere_deconnexion timestamp without time zone,
    heure_cloture character varying(5),
    actif boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    geom public.geometry(Point,4326),
    latitude numeric(10,8),
    longitude numeric(11,8)
);


ALTER TABLE public.collecteur OWNER TO postgres;

--
-- Name: TABLE collecteur; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.collecteur IS 'Collecteurs de taxes';


--
-- Name: collecteur_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.collecteur_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.collecteur_id_seq OWNER TO postgres;

--
-- Name: collecteur_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.collecteur_id_seq OWNED BY public.collecteur.id;


--
-- Name: commune; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.commune (
    id integer NOT NULL,
    nom character varying(100) NOT NULL,
    code character varying(20) NOT NULL,
    ville_id integer NOT NULL,
    description text,
    actif boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.commune OWNER TO postgres;

--
-- Name: commune_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.commune_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.commune_id_seq OWNER TO postgres;

--
-- Name: commune_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.commune_id_seq OWNED BY public.commune.id;


--
-- Name: contribuable; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contribuable (
    id integer NOT NULL,
    nom character varying(100) NOT NULL,
    prenom character varying(100),
    email character varying(100),
    telephone character varying(20) NOT NULL,
    type_contribuable_id integer NOT NULL,
    quartier_id integer NOT NULL,
    collecteur_id integer NOT NULL,
    adresse text,
    latitude numeric(10,8),
    longitude numeric(11,8),
    numero_identification character varying(50),
    actif boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    nom_activite character varying(200),
    photo_url character varying(500),
    geom public.geometry(Point,4326)
);


ALTER TABLE public.contribuable OWNER TO postgres;

--
-- Name: TABLE contribuable; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.contribuable IS 'Contribuables (clients)';


--
-- Name: contribuable_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.contribuable_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.contribuable_id_seq OWNER TO postgres;

--
-- Name: contribuable_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.contribuable_id_seq OWNED BY public.contribuable.id;


--
-- Name: info_collecte; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.info_collecte (
    id integer NOT NULL,
    contribuable_id integer NOT NULL,
    taxe_id integer NOT NULL,
    collecteur_id integer NOT NULL,
    montant numeric(12,2) NOT NULL,
    commission numeric(12,2) DEFAULT 0.00,
    type_paiement public.type_paiement_enum NOT NULL,
    statut public.statut_collecte_enum DEFAULT 'pending'::public.statut_collecte_enum,
    reference character varying(50) NOT NULL,
    billetage text,
    date_collecte timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    date_cloture timestamp without time zone,
    sms_envoye boolean DEFAULT false,
    ticket_imprime boolean DEFAULT false,
    annule boolean DEFAULT false,
    raison_annulation text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.info_collecte OWNER TO postgres;

--
-- Name: TABLE info_collecte; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.info_collecte IS 'Informations sur les collectes effectuÃ©es';


--
-- Name: info_collecte_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.info_collecte_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.info_collecte_id_seq OWNER TO postgres;

--
-- Name: info_collecte_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.info_collecte_id_seq OWNED BY public.info_collecte.id;


--
-- Name: quartier; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quartier (
    id integer NOT NULL,
    nom character varying(100) NOT NULL,
    code character varying(20) NOT NULL,
    zone_id integer NOT NULL,
    description text,
    actif boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.quartier OWNER TO postgres;

--
-- Name: TABLE quartier; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.quartier IS 'Quartiers de Libreville';


--
-- Name: quartier_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quartier_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quartier_id_seq OWNER TO postgres;

--
-- Name: quartier_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quartier_id_seq OWNED BY public.quartier.id;


--
-- Name: quartier_parametrage; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quartier_parametrage (
    id integer NOT NULL,
    nom character varying(100) NOT NULL,
    code character varying(20) NOT NULL,
    arrondissement_id integer,
    zone_id integer,
    description text,
    actif boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.quartier_parametrage OWNER TO postgres;

--
-- Name: quartier_parametrage_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quartier_parametrage_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quartier_parametrage_id_seq OWNER TO postgres;

--
-- Name: quartier_parametrage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quartier_parametrage_id_seq OWNED BY public.quartier_parametrage.id;


--
-- Name: role; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role (
    id integer NOT NULL,
    nom character varying(100) NOT NULL,
    code character varying(50) NOT NULL,
    description text,
    permissions text,
    actif boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.role OWNER TO postgres;

--
-- Name: role_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.role_id_seq OWNER TO postgres;

--
-- Name: role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.role_id_seq OWNED BY public.role.id;


--
-- Name: secteur_activite; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.secteur_activite (
    id integer NOT NULL,
    nom character varying(100) NOT NULL,
    code character varying(50) NOT NULL,
    description text,
    actif boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.secteur_activite OWNER TO postgres;

--
-- Name: secteur_activite_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.secteur_activite_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.secteur_activite_id_seq OWNER TO postgres;

--
-- Name: secteur_activite_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.secteur_activite_id_seq OWNED BY public.secteur_activite.id;


--
-- Name: service; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.service (
    id integer NOT NULL,
    nom character varying(100) NOT NULL,
    description text,
    code character varying(20) NOT NULL,
    actif boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.service OWNER TO postgres;

--
-- Name: TABLE service; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.service IS 'Services de la mairie';


--
-- Name: service_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.service_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.service_id_seq OWNER TO postgres;

--
-- Name: service_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.service_id_seq OWNED BY public.service.id;


--
-- Name: taxe; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.taxe (
    id integer NOT NULL,
    nom character varying(100) NOT NULL,
    code character varying(20) NOT NULL,
    description text,
    montant numeric(12,2) NOT NULL,
    montant_variable boolean DEFAULT false,
    periodicite public.periodicite_enum NOT NULL,
    type_taxe_id integer NOT NULL,
    service_id integer NOT NULL,
    commission_pourcentage numeric(5,2) DEFAULT 0.00,
    actif boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.taxe OWNER TO postgres;

--
-- Name: TABLE taxe; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.taxe IS 'Taxes municipales';


--
-- Name: taxe_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.taxe_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.taxe_id_seq OWNER TO postgres;

--
-- Name: taxe_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.taxe_id_seq OWNED BY public.taxe.id;


--
-- Name: type_contribuable; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.type_contribuable (
    id integer NOT NULL,
    nom character varying(50) NOT NULL,
    code character varying(20) NOT NULL,
    description text,
    actif boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.type_contribuable OWNER TO postgres;

--
-- Name: TABLE type_contribuable; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.type_contribuable IS 'Types de contribuables';


--
-- Name: type_contribuable_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.type_contribuable_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.type_contribuable_id_seq OWNER TO postgres;

--
-- Name: type_contribuable_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.type_contribuable_id_seq OWNED BY public.type_contribuable.id;


--
-- Name: type_taxe; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.type_taxe (
    id integer NOT NULL,
    nom character varying(100) NOT NULL,
    code character varying(20) NOT NULL,
    description text,
    actif boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.type_taxe OWNER TO postgres;

--
-- Name: TABLE type_taxe; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.type_taxe IS 'Types de taxes municipales';


--
-- Name: type_taxe_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.type_taxe_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.type_taxe_id_seq OWNER TO postgres;

--
-- Name: type_taxe_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.type_taxe_id_seq OWNED BY public.type_taxe.id;


--
-- Name: utilisateur; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.utilisateur (
    id integer NOT NULL,
    nom character varying(100) NOT NULL,
    prenom character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    telephone character varying(20),
    mot_de_passe_hash character varying(255) NOT NULL,
    role public.role_enum DEFAULT 'agent_back_office'::public.role_enum NOT NULL,
    actif boolean DEFAULT true,
    derniere_connexion timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.utilisateur OWNER TO postgres;

--
-- Name: TABLE utilisateur; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.utilisateur IS 'Utilisateurs du systÃ¨me (authentification)';


--
-- Name: utilisateur_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.utilisateur_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.utilisateur_id_seq OWNER TO postgres;

--
-- Name: utilisateur_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.utilisateur_id_seq OWNED BY public.utilisateur.id;


--
-- Name: ville; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ville (
    id integer NOT NULL,
    nom character varying(100) NOT NULL,
    code character varying(20) NOT NULL,
    description text,
    pays character varying(50),
    actif boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.ville OWNER TO postgres;

--
-- Name: ville_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ville_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ville_id_seq OWNER TO postgres;

--
-- Name: ville_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ville_id_seq OWNED BY public.ville.id;


--
-- Name: zone; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.zone (
    id integer NOT NULL,
    nom character varying(100) NOT NULL,
    code character varying(20) NOT NULL,
    description text,
    actif boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.zone OWNER TO postgres;

--
-- Name: TABLE zone; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.zone IS 'Zones gÃ©ographiques de Libreville';


--
-- Name: zone_geographique; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.zone_geographique (
    id integer NOT NULL,
    nom character varying(100) NOT NULL,
    type_zone character varying(50) NOT NULL,
    code character varying(50),
    geometry json NOT NULL,
    properties json,
    quartier_id integer,
    actif boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    geom public.geometry(MultiPolygon,4326)
);


ALTER TABLE public.zone_geographique OWNER TO postgres;

--
-- Name: zone_geographique_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.zone_geographique_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.zone_geographique_id_seq OWNER TO postgres;

--
-- Name: zone_geographique_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.zone_geographique_id_seq OWNED BY public.zone_geographique.id;


--
-- Name: zone_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.zone_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.zone_id_seq OWNER TO postgres;

--
-- Name: zone_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.zone_id_seq OWNED BY public.zone.id;


--
-- Name: affectation_taxe id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.affectation_taxe ALTER COLUMN id SET DEFAULT nextval('public.affectation_taxe_id_seq'::regclass);


--
-- Name: arrondissement id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.arrondissement ALTER COLUMN id SET DEFAULT nextval('public.arrondissement_id_seq'::regclass);


--
-- Name: collecteur id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collecteur ALTER COLUMN id SET DEFAULT nextval('public.collecteur_id_seq'::regclass);


--
-- Name: commune id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commune ALTER COLUMN id SET DEFAULT nextval('public.commune_id_seq'::regclass);


--
-- Name: contribuable id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contribuable ALTER COLUMN id SET DEFAULT nextval('public.contribuable_id_seq'::regclass);


--
-- Name: info_collecte id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.info_collecte ALTER COLUMN id SET DEFAULT nextval('public.info_collecte_id_seq'::regclass);


--
-- Name: quartier id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quartier ALTER COLUMN id SET DEFAULT nextval('public.quartier_id_seq'::regclass);


--
-- Name: quartier_parametrage id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quartier_parametrage ALTER COLUMN id SET DEFAULT nextval('public.quartier_parametrage_id_seq'::regclass);


--
-- Name: role id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role ALTER COLUMN id SET DEFAULT nextval('public.role_id_seq'::regclass);


--
-- Name: secteur_activite id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.secteur_activite ALTER COLUMN id SET DEFAULT nextval('public.secteur_activite_id_seq'::regclass);


--
-- Name: service id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service ALTER COLUMN id SET DEFAULT nextval('public.service_id_seq'::regclass);


--
-- Name: taxe id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxe ALTER COLUMN id SET DEFAULT nextval('public.taxe_id_seq'::regclass);


--
-- Name: type_contribuable id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_contribuable ALTER COLUMN id SET DEFAULT nextval('public.type_contribuable_id_seq'::regclass);


--
-- Name: type_taxe id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_taxe ALTER COLUMN id SET DEFAULT nextval('public.type_taxe_id_seq'::regclass);


--
-- Name: utilisateur id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.utilisateur ALTER COLUMN id SET DEFAULT nextval('public.utilisateur_id_seq'::regclass);


--
-- Name: ville id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ville ALTER COLUMN id SET DEFAULT nextval('public.ville_id_seq'::regclass);


--
-- Name: zone id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zone ALTER COLUMN id SET DEFAULT nextval('public.zone_id_seq'::regclass);


--
-- Name: zone_geographique id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zone_geographique ALTER COLUMN id SET DEFAULT nextval('public.zone_geographique_id_seq'::regclass);


--
-- Data for Name: affectation_taxe; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.affectation_taxe (id, contribuable_id, taxe_id, date_debut, date_fin, montant_custom, actif, created_at, updated_at) FROM stdin;
51	251	3	2025-10-19 23:32:52.971408	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
52	251	82	2025-10-15 17:39:10.472585	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
53	251	56	2025-05-31 10:29:44.361536	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
54	252	44	2025-11-14 07:18:04.506818	2026-11-14 07:18:04.506818	35113.11	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
55	253	29	2025-09-03 15:42:53.324267	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
56	253	45	2025-06-29 06:29:00.805789	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
57	254	1	2025-11-15 09:58:12.100597	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
58	254	70	2025-07-01 13:07:21.656773	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
59	254	90	2025-11-16 16:25:09.564287	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
60	255	28	2025-06-29 21:39:03.153336	\N	14625.01	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
61	256	9	2025-09-08 21:33:10.543792	2026-09-08 21:33:10.543792	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
62	256	52	2025-05-31 07:49:40.969189	2026-05-31 07:49:40.969189	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
63	257	46	2025-06-16 21:07:54.874696	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
64	257	80	2025-06-05 01:54:05.376968	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
65	257	58	2025-08-04 06:03:48.346275	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
66	258	2	2025-08-09 04:51:09.560321	\N	25656.63	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
67	259	57	2025-09-26 23:47:42.14542	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
68	259	92	2025-11-05 10:36:12.877877	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
69	260	93	2025-10-10 06:43:49.575687	2026-10-10 06:43:49.575687	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
70	260	87	2025-10-24 16:03:28.538919	2026-10-24 16:03:28.538919	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
71	260	53	2025-08-14 15:06:19.387576	2026-08-14 15:06:19.387576	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
72	261	37	2025-09-30 18:06:01.483255	\N	10964.63	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
73	262	34	2025-11-08 18:33:22.167749	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
74	262	57	2025-07-23 03:12:43.984448	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
75	263	62	2025-11-01 19:47:56.025701	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
76	263	67	2025-10-27 07:26:39.502975	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
77	263	75	2025-11-17 18:25:27.577323	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
78	264	13	2025-11-05 15:16:54.332683	2026-11-05 15:16:54.332683	12061.58	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
79	265	8	2025-10-09 13:27:21.17565	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
80	265	4	2025-11-04 02:49:51.226436	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
81	266	82	2025-09-20 07:10:55.763929	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
82	266	64	2025-06-17 04:04:46.135971	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
83	266	38	2025-08-18 22:41:54.526973	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
84	267	85	2025-10-16 13:09:33.421988	\N	30231.43	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
85	268	16	2025-07-27 07:25:57.935136	2026-07-27 07:25:57.935136	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
86	268	29	2025-10-21 10:45:33.739488	2026-10-21 10:45:33.739488	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
87	269	7	2025-07-23 08:10:38.93112	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
88	269	99	2025-07-07 21:37:38.733422	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
89	269	17	2025-06-15 03:33:32.325808	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
90	270	78	2025-06-16 22:47:35.488038	\N	4182.49	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
91	271	96	2025-11-06 22:50:03.160787	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
92	271	90	2025-07-07 01:09:50.035908	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
93	272	21	2025-06-25 21:00:40.806695	2026-06-25 21:00:40.806695	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
94	272	51	2025-08-17 04:35:12.502434	2026-08-17 04:35:12.502434	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
95	272	35	2025-09-04 08:56:12.739965	2026-09-04 08:56:12.739965	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
96	273	41	2025-08-20 18:09:03.458821	\N	1151.42	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
97	274	2	2025-07-20 04:31:34.463447	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
98	274	58	2025-11-03 05:38:59.740851	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
99	275	7	2025-10-22 14:19:51.625655	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
100	275	57	2025-09-19 23:30:52.138368	\N	\N	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
\.


--
-- Data for Name: arrondissement; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.arrondissement (id, nom, code, commune_id, description, actif, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: collecteur; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.collecteur (id, nom, prenom, email, telephone, matricule, statut, etat, zone_id, date_derniere_connexion, date_derniere_deconnexion, heure_cloture, actif, created_at, updated_at, geom, latitude, longitude) FROM stdin;
351	NDONG	Marie	collecteur1@mairie-libreville.ga	+241061000001	COL-001	active	connecte	374	\N	\N	18:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
352	OBAME	Pierre	collecteur2@mairie-libreville.ga	+241061000002	COL-002	active	deconnecte	308	\N	\N	19:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
353	BONGO	Paul	collecteur3@mairie-libreville.ga	+241061000003	COL-003	active	connecte	368	\N	\N	17:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
354	ESSONO	Sophie	collecteur4@mairie-libreville.ga	+241061000004	COL-004	active	deconnecte	314	\N	\N	18:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
355	MVE	Luc	collecteur5@mairie-libreville.ga	+241061000005	COL-005	active	connecte	337	\N	\N	19:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
356	MINTSA	Anne	collecteur6@mairie-libreville.ga	+241061000006	COL-006	active	deconnecte	347	\N	\N	17:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
357	MBOUMBA	David	collecteur7@mairie-libreville.ga	+241061000007	COL-007	active	connecte	324	\N	\N	18:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
358	NDONG	FranÃ§ois	collecteur8@mairie-libreville.ga	+241061000008	COL-008	active	deconnecte	322	\N	\N	19:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
359	OBAME	Catherine	collecteur9@mairie-libreville.ga	+241061000009	COL-009	active	connecte	348	\N	\N	17:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
360	BONGO	Michel	collecteur10@mairie-libreville.ga	+241061000010	COL-010	desactive	deconnecte	334	\N	\N	18:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
361	ESSONO	Isabelle	collecteur11@mairie-libreville.ga	+241061000011	COL-011	active	connecte	357	\N	\N	19:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
362	MVE	AndrÃ©	collecteur12@mairie-libreville.ga	+241061000012	COL-012	active	deconnecte	305	\N	\N	17:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
363	MINTSA	Christine	collecteur13@mairie-libreville.ga	+241061000013	COL-013	active	connecte	384	\N	\N	18:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
364	MBOUMBA	Jean	collecteur14@mairie-libreville.ga	+241061000014	COL-014	active	deconnecte	341	\N	\N	19:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
365	NDONG	Marie	collecteur15@mairie-libreville.ga	+241061000015	COL-015	active	connecte	398	\N	\N	17:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
366	OBAME	Pierre	collecteur16@mairie-libreville.ga	+241061000016	COL-016	active	deconnecte	340	\N	\N	18:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
367	BONGO	Paul	collecteur17@mairie-libreville.ga	+241061000017	COL-017	active	connecte	306	\N	\N	19:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
368	ESSONO	Sophie	collecteur18@mairie-libreville.ga	+241061000018	COL-018	active	deconnecte	374	\N	\N	17:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
369	MVE	Luc	collecteur19@mairie-libreville.ga	+241061000019	COL-019	active	connecte	317	\N	\N	18:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
370	MINTSA	Anne	collecteur20@mairie-libreville.ga	+241061000020	COL-020	desactive	deconnecte	385	\N	\N	19:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
371	MBOUMBA	David	collecteur21@mairie-libreville.ga	+241061000021	COL-021	active	connecte	311	\N	\N	17:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
372	NDONG	FranÃ§ois	collecteur22@mairie-libreville.ga	+241061000022	COL-022	active	deconnecte	375	\N	\N	18:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
373	OBAME	Catherine	collecteur23@mairie-libreville.ga	+241061000023	COL-023	active	connecte	325	\N	\N	19:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
374	BONGO	Michel	collecteur24@mairie-libreville.ga	+241061000024	COL-024	active	deconnecte	386	\N	\N	17:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
375	ESSONO	Isabelle	collecteur25@mairie-libreville.ga	+241061000025	COL-025	active	connecte	310	\N	\N	18:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
376	MVE	AndrÃ©	collecteur26@mairie-libreville.ga	+241061000026	COL-026	active	deconnecte	397	\N	\N	19:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
377	MINTSA	Christine	collecteur27@mairie-libreville.ga	+241061000027	COL-027	active	connecte	308	\N	\N	17:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
378	MBOUMBA	Jean	collecteur28@mairie-libreville.ga	+241061000028	COL-028	active	deconnecte	379	\N	\N	18:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
379	NDONG	Marie	collecteur29@mairie-libreville.ga	+241061000029	COL-029	active	connecte	383	\N	\N	19:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
380	OBAME	Pierre	collecteur30@mairie-libreville.ga	+241061000030	COL-030	desactive	deconnecte	308	\N	\N	17:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
381	BONGO	Paul	collecteur31@mairie-libreville.ga	+241061000031	COL-031	active	connecte	356	\N	\N	18:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
382	ESSONO	Sophie	collecteur32@mairie-libreville.ga	+241061000032	COL-032	active	deconnecte	320	\N	\N	19:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
383	MVE	Luc	collecteur33@mairie-libreville.ga	+241061000033	COL-033	active	connecte	371	\N	\N	17:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
384	MINTSA	Anne	collecteur34@mairie-libreville.ga	+241061000034	COL-034	active	deconnecte	310	\N	\N	18:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
385	MBOUMBA	David	collecteur35@mairie-libreville.ga	+241061000035	COL-035	active	connecte	383	\N	\N	19:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
386	NDONG	FranÃ§ois	collecteur36@mairie-libreville.ga	+241061000036	COL-036	active	deconnecte	402	\N	\N	17:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
387	OBAME	Catherine	collecteur37@mairie-libreville.ga	+241061000037	COL-037	active	connecte	317	\N	\N	18:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
388	BONGO	Michel	collecteur38@mairie-libreville.ga	+241061000038	COL-038	active	deconnecte	337	\N	\N	19:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
389	ESSONO	Isabelle	collecteur39@mairie-libreville.ga	+241061000039	COL-039	active	connecte	340	\N	\N	17:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
390	MVE	AndrÃ©	collecteur40@mairie-libreville.ga	+241061000040	COL-040	desactive	deconnecte	365	\N	\N	18:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
391	MINTSA	Christine	collecteur41@mairie-libreville.ga	+241061000041	COL-041	active	connecte	368	\N	\N	19:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
392	MBOUMBA	Jean	collecteur42@mairie-libreville.ga	+241061000042	COL-042	active	deconnecte	376	\N	\N	17:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
393	NDONG	Marie	collecteur43@mairie-libreville.ga	+241061000043	COL-043	active	connecte	352	\N	\N	18:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
394	OBAME	Pierre	collecteur44@mairie-libreville.ga	+241061000044	COL-044	active	deconnecte	400	\N	\N	19:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
395	BONGO	Paul	collecteur45@mairie-libreville.ga	+241061000045	COL-045	active	connecte	374	\N	\N	17:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
396	ESSONO	Sophie	collecteur46@mairie-libreville.ga	+241061000046	COL-046	active	deconnecte	349	\N	\N	18:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
397	MVE	Luc	collecteur47@mairie-libreville.ga	+241061000047	COL-047	active	connecte	388	\N	\N	19:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
398	MINTSA	Anne	collecteur48@mairie-libreville.ga	+241061000048	COL-048	active	deconnecte	371	\N	\N	17:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
399	MBOUMBA	David	collecteur49@mairie-libreville.ga	+241061000049	COL-049	active	connecte	337	\N	\N	18:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
400	NDONG	FranÃ§ois	collecteur50@mairie-libreville.ga	+241061000050	COL-050	desactive	deconnecte	383	\N	\N	19:00	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041	\N	\N	\N
\.


--
-- Data for Name: commune; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.commune (id, nom, code, ville_id, description, actif, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: contribuable; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.contribuable (id, nom, prenom, email, telephone, type_contribuable_id, quartier_id, collecteur_id, adresse, latitude, longitude, numero_identification, actif, created_at, updated_at, nom_activite, photo_url, geom) FROM stdin;
255	MVE	Luc	contribuable5@example.ga	+241062000005	165	355	378	Avenue IndÃ©pendance 6	0.35000000	9.35000000	CTB-0005	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E61000003333333333B32240666666666666D63F
256	MINTSA	Anne	\N	+241062000006	618	343	361	Boulevard LÃ©on Mba 7	0.36000000	9.36000000	CTB-0006	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000B81E85EB51B822400AD7A3703D0AD73F
257	MBOUMBA	David	contribuable7@example.ga	+241062000007	165	394	395	Rue Nkrumah 8	0.37000000	9.37000000	CTB-0007	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E61000003D0AD7A370BD2240AE47E17A14AED73F
258	NDONG	Jean	contribuable8@example.ga	+241062000008	606	333	399	Avenue De Gaulle 9	0.38000000	9.38000000	CTB-0008	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000C3F5285C8FC2224052B81E85EB51D83F
259	OBAME	Marie	\N	+241062000009	620	358	383	Rue Massenet 10	0.39000000	9.39000000	CTB-0009	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E610000048E17A14AEC72240F6285C8FC2F5D83F
260	BONGO	Pierre	contribuable10@example.ga	+241062000010	611	315	388	Avenue IndÃ©pendance 11	0.40000000	9.40000000	CTB-0010	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000CDCCCCCCCCCC22409A9999999999D93F
261	ESSONO	Paul	contribuable11@example.ga	+241062000011	597	399	360	Boulevard LÃ©on Mba 12	0.41000000	9.41000000	CTB-0011	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E610000052B81E85EBD122403D0AD7A3703DDA3F
262	MVE	Sophie	\N	+241062000012	619	347	387	Rue Nkrumah 13	0.42000000	9.42000000	CTB-0012	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000D7A3703D0AD72240E17A14AE47E1DA3F
263	MINTSA	Luc	contribuable13@example.ga	+241062000013	151	337	355	Avenue De Gaulle 14	0.43000000	9.43000000	CTB-0013	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E61000005C8FC2F528DC224085EB51B81E85DB3F
264	MBOUMBA	Anne	contribuable14@example.ga	+241062000014	155	381	370	Rue Massenet 15	0.44000000	9.44000000	CTB-0014	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000E17A14AE47E12240295C8FC2F528DC3F
265	NDONG	David	\N	+241062000015	170	387	387	Avenue IndÃ©pendance 16	0.45000000	9.45000000	CTB-0015	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E61000006666666666E62240CDCCCCCCCCCCDC3F
266	OBAME	Jean	contribuable16@example.ga	+241062000016	610	396	372	Boulevard LÃ©on Mba 17	0.46000000	9.46000000	CTB-0016	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000EC51B81E85EB2240713D0AD7A370DD3F
267	BONGO	Marie	contribuable17@example.ga	+241062000017	151	321	375	Rue Nkrumah 18	0.47000000	9.47000000	CTB-0017	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000713D0AD7A3F0224014AE47E17A14DE3F
268	ESSONO	Pierre	\N	+241062000018	161	392	386	Avenue De Gaulle 19	0.48000000	9.48000000	CTB-0018	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000F6285C8FC2F52240B81E85EB51B8DE3F
269	MVE	Paul	contribuable19@example.ga	+241062000019	611	351	366	Rue Massenet 20	0.49000000	9.49000000	CTB-0019	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E61000007B14AE47E1FA22405C8FC2F5285CDF3F
270	MINTSA	Sophie	contribuable20@example.ga	+241062000020	608	398	390	Avenue IndÃ©pendance 21	0.30000000	9.30000000	CTB-0020	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E61000009A99999999992240333333333333D33F
271	MBOUMBA	Luc	\N	+241062000021	596	369	351	Boulevard LÃ©on Mba 22	0.31000000	9.31000000	CTB-0021	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E61000001F85EB51B89E2240D7A3703D0AD7D33F
272	NDONG	Anne	contribuable22@example.ga	+241062000022	150	331	366	Rue Nkrumah 23	0.32000000	9.32000000	CTB-0022	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000A4703D0AD7A322407B14AE47E17AD43F
273	OBAME	David	contribuable23@example.ga	+241062000023	597	368	362	Avenue De Gaulle 24	0.33000000	9.33000000	CTB-0023	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000295C8FC2F5A822401F85EB51B81ED53F
274	BONGO	Jean	\N	+241062000024	597	338	351	Rue Massenet 25	0.34000000	9.34000000	CTB-0024	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000AE47E17A14AE2240C3F5285C8FC2D53F
275	ESSONO	Marie	contribuable25@example.ga	+241062000025	597	313	389	Avenue IndÃ©pendance 26	0.35000000	9.35000000	CTB-0025	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E61000003333333333B32240666666666666D63F
276	MVE	Pierre	contribuable26@example.ga	+241062000026	611	322	368	Boulevard LÃ©on Mba 27	0.36000000	9.36000000	CTB-0026	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000B81E85EB51B822400AD7A3703D0AD73F
277	MINTSA	Paul	\N	+241062000027	597	381	391	Rue Nkrumah 28	0.37000000	9.37000000	CTB-0027	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E61000003D0AD7A370BD2240AE47E17A14AED73F
278	MBOUMBA	Sophie	contribuable28@example.ga	+241062000028	616	387	370	Avenue De Gaulle 29	0.38000000	9.38000000	CTB-0028	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000C3F5285C8FC2224052B81E85EB51D83F
279	NDONG	Luc	contribuable29@example.ga	+241062000029	605	387	393	Rue Massenet 30	0.39000000	9.39000000	CTB-0029	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E610000048E17A14AEC72240F6285C8FC2F5D83F
280	OBAME	Anne	\N	+241062000030	596	387	359	Avenue IndÃ©pendance 31	0.40000000	9.40000000	CTB-0030	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000CDCCCCCCCCCC22409A9999999999D93F
281	BONGO	David	contribuable31@example.ga	+241062000031	617	369	394	Boulevard LÃ©on Mba 32	0.41000000	9.41000000	CTB-0031	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E610000052B81E85EBD122403D0AD7A3703DDA3F
282	ESSONO	Jean	contribuable32@example.ga	+241062000032	162	369	390	Rue Nkrumah 33	0.42000000	9.42000000	CTB-0032	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000D7A3703D0AD72240E17A14AE47E1DA3F
283	MVE	Marie	\N	+241062000033	618	367	381	Avenue De Gaulle 34	0.43000000	9.43000000	CTB-0033	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E61000005C8FC2F528DC224085EB51B81E85DB3F
284	MINTSA	Pierre	contribuable34@example.ga	+241062000034	159	348	399	Rue Massenet 35	0.44000000	9.44000000	CTB-0034	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000E17A14AE47E12240295C8FC2F528DC3F
285	MBOUMBA	Paul	contribuable35@example.ga	+241062000035	165	393	391	Avenue IndÃ©pendance 36	0.45000000	9.45000000	CTB-0035	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E61000006666666666E62240CDCCCCCCCCCCDC3F
286	NDONG	Sophie	\N	+241062000036	149	340	384	Boulevard LÃ©on Mba 37	0.46000000	9.46000000	CTB-0036	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000EC51B81E85EB2240713D0AD7A370DD3F
287	OBAME	Luc	contribuable37@example.ga	+241062000037	597	308	367	Rue Nkrumah 38	0.47000000	9.47000000	CTB-0037	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000713D0AD7A3F0224014AE47E17A14DE3F
288	BONGO	Anne	contribuable38@example.ga	+241062000038	170	311	357	Avenue De Gaulle 39	0.48000000	9.48000000	CTB-0038	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000F6285C8FC2F52240B81E85EB51B8DE3F
289	ESSONO	David	\N	+241062000039	161	304	394	Rue Massenet 40	0.49000000	9.49000000	CTB-0039	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E61000007B14AE47E1FA22405C8FC2F5285CDF3F
290	MVE	Jean	contribuable40@example.ga	+241062000040	162	302	372	Avenue IndÃ©pendance 41	0.30000000	9.30000000	CTB-0040	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E61000009A99999999992240333333333333D33F
291	MINTSA	Marie	contribuable41@example.ga	+241062000041	164	367	360	Boulevard LÃ©on Mba 42	0.31000000	9.31000000	CTB-0041	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E61000001F85EB51B89E2240D7A3703D0AD7D33F
292	MBOUMBA	Pierre	\N	+241062000042	152	370	354	Rue Nkrumah 43	0.32000000	9.32000000	CTB-0042	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000A4703D0AD7A322407B14AE47E17AD43F
293	NDONG	Paul	contribuable43@example.ga	+241062000043	603	311	376	Avenue De Gaulle 44	0.33000000	9.33000000	CTB-0043	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000295C8FC2F5A822401F85EB51B81ED53F
294	OBAME	Sophie	contribuable44@example.ga	+241062000044	155	365	394	Rue Massenet 45	0.34000000	9.34000000	CTB-0044	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000AE47E17A14AE2240C3F5285C8FC2D53F
295	BONGO	Luc	\N	+241062000045	605	347	398	Avenue IndÃ©pendance 46	0.35000000	9.35000000	CTB-0045	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E61000003333333333B32240666666666666D63F
296	ESSONO	Anne	contribuable46@example.ga	+241062000046	598	395	379	Boulevard LÃ©on Mba 47	0.36000000	9.36000000	CTB-0046	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000B81E85EB51B822400AD7A3703D0AD73F
251	NDONG	Marie	contribuable1@example.ga	+241062000001	602	363	393	Boulevard LÃ©on Mba 2	0.31000000	9.31000000	CTB-0001	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E61000001F85EB51B89E2240D7A3703D0AD7D33F
252	OBAME	Pierre	contribuable2@example.ga	+241062000002	149	377	396	Rue Nkrumah 3	0.32000000	9.32000000	CTB-0002	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000A4703D0AD7A322407B14AE47E17AD43F
253	BONGO	Paul	\N	+241062000003	166	320	355	Avenue De Gaulle 4	0.33000000	9.33000000	CTB-0003	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000295C8FC2F5A822401F85EB51B81ED53F
254	ESSONO	Sophie	contribuable4@example.ga	+241062000004	169	365	364	Rue Massenet 5	0.34000000	9.34000000	CTB-0004	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000AE47E17A14AE2240C3F5285C8FC2D53F
297	MVE	David	contribuable47@example.ga	+241062000047	608	303	363	Rue Nkrumah 48	0.37000000	9.37000000	CTB-0047	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E61000003D0AD7A370BD2240AE47E17A14AED73F
298	MINTSA	Jean	\N	+241062000048	602	367	390	Avenue De Gaulle 49	0.38000000	9.38000000	CTB-0048	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000C3F5285C8FC2224052B81E85EB51D83F
299	MBOUMBA	Marie	contribuable49@example.ga	+241062000049	160	360	354	Rue Massenet 50	0.39000000	9.39000000	CTB-0049	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E610000048E17A14AEC72240F6285C8FC2F5D83F
300	NDONG	Pierre	contribuable50@example.ga	+241062000050	614	335	381	Avenue IndÃ©pendance 51	0.40000000	9.40000000	CTB-0050	t	2025-11-20 22:59:10.253041	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000CDCCCCCCCCCC22409A9999999999D93F
301	BEBANE MOUKOUMBI	MARINA BRUNELLE	\N	+24107861364	151	305	355	nombakélé	0.36902397	9.48005731	79551545	t	2025-11-20 23:47:39.858586	2025-11-21 08:18:51.261054	\N	\N	0101000020E6100000BC4F5D12CAF52240F4C3A5B6169ED73F
\.


--
-- Data for Name: info_collecte; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.info_collecte (id, contribuable_id, taxe_id, collecteur_id, montant, commission, type_paiement, statut, reference, billetage, date_collecte, date_cloture, sms_envoye, ticket_imprime, annule, raison_annulation, created_at, updated_at) FROM stdin;
51	254	1	378	1000.00	50.00	mobile_money	completed	COL-20251022-0001	\N	2025-10-22 19:35:01.4232	\N	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
52	261	37	392	10000.00	974.00	carte	completed	COL-20250905-0002	\N	2025-09-05 16:35:16.313203	\N	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
53	257	58	395	25000.00	190.00	especes	pending	COL-20250903-0003	\N	2025-09-03 04:04:52.405054	2025-09-03 04:25:13.380593	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
54	263	67	366	25000.00	1362.50	mobile_money	failed	COL-20250926-0004	\N	2025-09-26 03:17:04.2157	\N	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
55	253	29	389	10000.00	296.00	carte	completed	COL-20251110-0005	\N	2025-11-10 06:59:00.669669	\N	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
56	262	57	388	15000.00	706.50	especes	completed	COL-20251024-0006	{"5000" : 6, "1000" : 6}	2025-10-24 01:36:34.392902	2025-10-24 06:01:50.742308	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
57	263	75	356	2000.00	56.80	mobile_money	completed	COL-20251105-0007	\N	2025-11-05 15:15:59.223944	\N	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
58	269	7	394	2000.00	41.20	carte	pending	COL-20251013-0008	\N	2025-10-13 04:25:34.071749	\N	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
59	266	38	356	2000.00	35.20	especes	failed	COL-20251028-0009	\N	2025-10-28 01:36:39.135233	2025-10-28 07:19:17.651615	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
60	272	35	369	10000.00	368.00	mobile_money	completed	COL-20250928-0010	\N	2025-09-28 21:26:59.295893	\N	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
61	254	90	378	30000.00	1926.00	carte	completed	COL-20250906-0011	\N	2025-09-06 12:10:39.120626	\N	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
62	268	29	362	10000.00	296.00	especes	completed	COL-20250915-0012	{"5000" : 2, "1000" : 12}	2025-09-15 01:05:35.168148	2025-09-15 07:47:13.021287	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
63	272	35	363	10000.00	368.00	mobile_money	pending	COL-20250929-0013	\N	2025-09-29 07:38:24.999414	\N	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
64	254	90	358	30000.00	1926.00	carte	failed	COL-20251017-0014	\N	2025-10-17 00:03:26.963089	\N	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
65	263	62	393	15000.00	592.50	especes	completed	COL-20251016-0015	\N	2025-10-16 20:37:06.085224	2025-10-17 02:22:03.218418	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
66	268	16	384	30000.00	543.00	mobile_money	completed	COL-20251023-0016	\N	2025-10-23 06:00:39.893199	\N	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
67	269	17	369	20000.00	1414.00	carte	completed	COL-20250828-0017	\N	2025-08-28 11:33:09.684128	\N	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
68	274	58	353	25000.00	190.00	especes	pending	COL-20251118-0018	{"5000" : 8, "1000" : 18}	2025-11-18 04:57:14.312933	2025-11-18 10:47:12.829179	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
69	269	99	396	15000.00	763.50	mobile_money	failed	COL-20251115-0019	\N	2025-11-15 17:01:43.948056	\N	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
70	256	9	355	30000.00	2370.00	carte	completed	COL-20251029-0020	\N	2025-10-29 04:24:02.105094	\N	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
71	271	96	368	500.00	21.30	especes	completed	COL-20250929-0021	\N	2025-09-29 03:45:33.226162	2025-09-29 04:29:40.623182	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
72	256	9	358	30000.00	2370.00	mobile_money	completed	COL-20251020-0022	\N	2025-10-20 16:05:30.127434	\N	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
73	260	87	392	500.00	28.10	carte	pending	COL-20250930-0023	\N	2025-09-30 03:16:00.101825	\N	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
74	256	52	394	1000.00	94.00	especes	failed	COL-20251109-0024	{"5000" : 4, "1000" : 4}	2025-11-09 12:45:03.760266	2025-11-09 18:01:56.245707	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
75	257	80	369	10000.00	547.00	mobile_money	completed	COL-20251008-0025	\N	2025-10-08 10:43:48.254514	\N	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
76	262	34	397	30000.00	519.00	carte	completed	COL-20251022-0026	\N	2025-10-22 06:29:43.263858	\N	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
77	257	80	390	10000.00	547.00	especes	completed	COL-20251002-0027	\N	2025-10-02 00:15:00.2336	2025-10-02 03:51:05.214849	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
78	257	58	371	25000.00	190.00	mobile_money	pending	COL-20251107-0028	\N	2025-11-07 13:03:35.4582	\N	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
79	265	4	391	15000.00	600.00	carte	failed	COL-20251116-0029	\N	2025-11-16 06:00:34.753911	\N	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
80	256	9	388	30000.00	2370.00	especes	completed	COL-20250923-0030	{"5000" : 0, "1000" : 10}	2025-09-23 21:58:04.46501	2025-09-24 05:27:31.269091	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
81	265	4	360	15000.00	600.00	mobile_money	completed	COL-20251120-0031	\N	2025-11-20 13:30:28.843512	\N	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
82	271	90	388	30000.00	1926.00	carte	completed	COL-20251012-0032	\N	2025-10-12 17:54:31.988303	\N	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
83	257	46	397	500.00	49.80	especes	pending	COL-20251001-0033	\N	2025-10-01 01:56:44.051218	2025-10-01 02:42:33.356225	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
84	263	75	369	2000.00	56.80	mobile_money	failed	COL-20250924-0034	\N	2025-09-24 17:24:15.954807	\N	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
85	254	1	379	1000.00	50.00	carte	completed	COL-20251007-0035	\N	2025-10-07 09:56:59.735989	\N	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
86	269	17	357	20000.00	1414.00	especes	completed	COL-20251113-0036	{"5000" : 6, "1000" : 16}	2025-11-13 11:59:48.741197	2025-11-13 16:30:13.644482	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
87	258	2	381	25000.00	1250.00	mobile_money	completed	COL-20250922-0037	\N	2025-09-22 19:29:30.420596	\N	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
88	260	53	365	25000.00	10.00	carte	pending	COL-20251007-0038	\N	2025-10-07 03:59:14.929317	\N	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
89	254	70	389	30000.00	339.00	especes	failed	COL-20250829-0039	\N	2025-08-29 14:28:27.744597	2025-08-29 18:51:05.333083	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
90	268	16	394	30000.00	543.00	mobile_money	completed	COL-20251006-0040	\N	2025-10-06 23:04:28.807814	\N	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
91	256	9	378	30000.00	2370.00	carte	completed	COL-20250917-0041	\N	2025-09-17 20:59:08.43451	\N	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
92	253	45	353	20000.00	70.00	especes	completed	COL-20250902-0042	{"5000" : 2, "1000" : 2}	2025-09-02 01:35:13.092118	2025-09-02 01:52:48.972549	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
93	253	29	367	10000.00	296.00	mobile_money	pending	COL-20250929-0043	\N	2025-09-29 18:08:25.464494	\N	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
94	275	7	368	2000.00	41.20	carte	failed	COL-20250929-0044	\N	2025-09-29 16:59:07.800279	\N	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
95	265	8	369	25000.00	2240.00	especes	completed	COL-20250826-0045	\N	2025-08-26 08:00:16.976428	2025-08-26 11:04:57.029665	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
96	265	8	361	25000.00	2240.00	mobile_money	completed	COL-20250917-0046	\N	2025-09-17 02:28:16.321617	\N	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
97	261	37	400	10000.00	974.00	carte	completed	COL-20250907-0047	\N	2025-09-07 17:29:07.449112	\N	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
98	274	58	392	25000.00	190.00	especes	pending	COL-20250902-0048	{"5000" : 8, "1000" : 8}	2025-09-02 09:22:40.692876	2025-09-02 11:34:44.851824	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
99	259	92	397	25000.00	1980.00	mobile_money	failed	COL-20250928-0049	\N	2025-09-28 16:49:08.301356	\N	f	f	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
100	268	29	376	10000.00	296.00	carte	completed	COL-20251011-0050	\N	2025-10-11 17:06:18.947849	\N	t	t	f	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
\.


--
-- Data for Name: quartier; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quartier (id, nom, code, zone_id, description, actif, created_at, updated_at) FROM stdin;
302	Mont-Bouët	Q-001	303	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
303	Glass	Q-002	303	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
304	Quartier Louis	Q-003	303	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
305	Nombakélé	Q-004	303	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
306	Akébé	Q-005	303	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
307	Oloumi	Q-006	303	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
308	Batterie IV	Q-007	303	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
309	Derrière la Prison	Q-008	303	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
310	Charbonnages	Q-009	303	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
311	Lalala	Q-010	303	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
312	Cocotiers	Q-011	304	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
313	Angondjé	Q-012	304	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
314	Melen	Q-013	304	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
315	Nkoltang	Q-014	304	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
316	Minko	Q-015	304	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
317	Ntoum Centre	Q-016	305	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
318	Mveng	Q-017	305	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
319	Mvouli	Q-018	305	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
320	Owendo Centre	Q-019	306	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
321	PK8	Q-020	306	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
322	PK12	Q-021	306	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
323	PK15	Q-022	306	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
324	Port-Gentil Centre	Q-023	307	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
325	Ivea	Q-024	307	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
326	Nzeng-Ayong	Q-025	307	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
327	Franceville Centre	Q-026	308	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
328	Mounana	Q-027	308	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
329	Okondja	Q-028	308	\N	t	2025-11-20 21:29:20.082486	2025-11-20 21:29:20.082486
330	Quartier 29	Q-029	348	Quartier 29 de Zone 46	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
331	Quartier 30	Q-030	357	Quartier 30 de Zone 55	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
332	Quartier 31	Q-031	350	Quartier 31 de Zone 48	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
333	Quartier 32	Q-032	325	Quartier 32 de Zone 23	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
334	Quartier 33	Q-033	392	Quartier 33 de Zone 90	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
335	Quartier 34	Q-034	308	Quartier 34 de Franceville	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
336	Quartier 35	Q-035	389	Quartier 35 de Zone 87	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
337	Quartier 36	Q-036	388	Quartier 36 de Zone 86	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
338	Quartier 37	Q-037	358	Quartier 37 de Zone 56	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
339	Quartier 38	Q-038	362	Quartier 38 de Zone 60	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
340	Quartier 39	Q-039	388	Quartier 39 de Zone 86	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
341	Quartier 40	Q-040	372	Quartier 40 de Zone 70	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
342	Quartier 41	Q-041	351	Quartier 41 de Zone 49	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
343	Quartier 42	Q-042	354	Quartier 42 de Zone 52	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
344	Quartier 43	Q-043	362	Quartier 43 de Zone 60	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
345	Quartier 44	Q-044	371	Quartier 44 de Zone 69	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
346	Quartier 45	Q-045	378	Quartier 45 de Zone 76	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
347	Quartier 46	Q-046	361	Quartier 46 de Zone 59	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
348	Quartier 47	Q-047	362	Quartier 47 de Zone 60	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
349	Quartier 48	Q-048	309	Quartier 48 de Zone 7	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
350	Quartier 49	Q-049	399	Quartier 49 de Zone 97	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
351	Quartier 50	Q-050	342	Quartier 50 de Zone 40	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
352	Quartier 51	Q-051	332	Quartier 51 de Zone 30	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
353	Quartier 52	Q-052	353	Quartier 52 de Zone 51	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
354	Quartier 53	Q-053	399	Quartier 53 de Zone 97	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
355	Quartier 54	Q-054	383	Quartier 54 de Zone 81	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
356	Quartier 55	Q-055	347	Quartier 55 de Zone 45	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
357	Quartier 56	Q-056	356	Quartier 56 de Zone 54	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
358	Quartier 57	Q-057	379	Quartier 57 de Zone 77	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
359	Quartier 58	Q-058	341	Quartier 58 de Zone 39	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
360	Quartier 59	Q-059	339	Quartier 59 de Zone 37	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
361	Quartier 60	Q-060	336	Quartier 60 de Zone 34	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
362	Quartier 61	Q-061	380	Quartier 61 de Zone 78	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
363	Quartier 62	Q-062	398	Quartier 62 de Zone 96	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
364	Quartier 63	Q-063	380	Quartier 63 de Zone 78	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
365	Quartier 64	Q-064	311	Quartier 64 de Zone 9	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
366	Quartier 65	Q-065	391	Quartier 65 de Zone 89	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
367	Quartier 66	Q-066	397	Quartier 66 de Zone 95	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
368	Quartier 67	Q-067	321	Quartier 67 de Zone 19	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
369	Quartier 68	Q-068	311	Quartier 68 de Zone 9	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
370	Quartier 69	Q-069	349	Quartier 69 de Zone 47	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
371	Quartier 70	Q-070	372	Quartier 70 de Zone 70	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
372	Quartier 71	Q-071	388	Quartier 71 de Zone 86	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
373	Quartier 72	Q-072	317	Quartier 72 de Zone 15	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
374	Quartier 73	Q-073	376	Quartier 73 de Zone 74	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
375	Quartier 74	Q-074	400	Quartier 74 de Zone 98	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
376	Quartier 75	Q-075	370	Quartier 75 de Zone 68	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
377	Quartier 76	Q-076	385	Quartier 76 de Zone 83	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
378	Quartier 77	Q-077	310	Quartier 77 de Zone 8	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
379	Quartier 78	Q-078	382	Quartier 78 de Zone 80	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
380	Quartier 79	Q-079	336	Quartier 79 de Zone 34	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
381	Quartier 80	Q-080	370	Quartier 80 de Zone 68	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
382	Quartier 81	Q-081	330	Quartier 81 de Zone 28	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
383	Quartier 82	Q-082	372	Quartier 82 de Zone 70	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
384	Quartier 83	Q-083	385	Quartier 83 de Zone 83	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
385	Quartier 84	Q-084	327	Quartier 84 de Zone 25	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
386	Quartier 85	Q-085	382	Quartier 85 de Zone 80	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
387	Quartier 86	Q-086	352	Quartier 86 de Zone 50	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
388	Quartier 87	Q-087	325	Quartier 87 de Zone 23	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
389	Quartier 88	Q-088	349	Quartier 88 de Zone 47	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
390	Quartier 89	Q-089	373	Quartier 89 de Zone 71	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
391	Quartier 90	Q-090	324	Quartier 90 de Zone 22	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
392	Quartier 91	Q-091	310	Quartier 91 de Zone 8	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
393	Quartier 92	Q-092	401	Quartier 92 de Zone 99	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
394	Quartier 93	Q-093	367	Quartier 93 de Zone 65	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
395	Quartier 94	Q-094	357	Quartier 94 de Zone 55	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
396	Quartier 95	Q-095	394	Quartier 95 de Zone 92	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
397	Quartier 96	Q-096	336	Quartier 96 de Zone 34	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
398	Quartier 97	Q-097	320	Quartier 97 de Zone 18	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
399	Quartier 98	Q-098	379	Quartier 98 de Zone 77	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
400	Quartier 99	Q-099	339	Quartier 99 de Zone 37	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
401	Quartier 100	Q-100	384	Quartier 100 de Zone 82	t	2025-11-20 21:29:20.093978	2025-11-20 21:29:20.093978
\.


--
-- Data for Name: quartier_parametrage; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quartier_parametrage (id, nom, code, arrondissement_id, zone_id, description, actif, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: role; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.role (id, nom, code, description, permissions, actif, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: secteur_activite; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.secteur_activite (id, nom, code, description, actif, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: service; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.service (id, nom, description, code, actif, created_at, updated_at) FROM stdin;
133	Service des Finances	Gestion financière	SRV-001	t	2025-11-20 21:29:20.136877	2025-11-20 21:29:20.136877
134	Service des Marchés	Gestion des marchés	SRV-002	t	2025-11-20 21:29:20.136877	2025-11-20 21:29:20.136877
135	Service de l'Urbanisme	Urbanisme et aménagement	SRV-003	t	2025-11-20 21:29:20.136877	2025-11-20 21:29:20.136877
136	Service des Transports	Gestion des transports	SRV-004	t	2025-11-20 21:29:20.136877	2025-11-20 21:29:20.136877
137	Service des Commerces	Gestion des commerces	SRV-005	t	2025-11-20 21:29:20.136877	2025-11-20 21:29:20.136877
138	Service de l'Environnement	Environnement et propreté	SRV-006	t	2025-11-20 21:29:20.136877	2025-11-20 21:29:20.136877
139	Service de la Voirie	Entretien de la voirie	SRV-007	t	2025-11-20 21:29:20.136877	2025-11-20 21:29:20.136877
140	Service de la Propreté	Service : Service de la Propreté	SRV-008	t	2025-11-20 21:29:20.143267	2025-11-20 21:29:20.143267
141	Service de l'Éclairage Public	Service : Service de l'Éclairage Public	SRV-009	t	2025-11-20 21:29:20.143267	2025-11-20 21:29:20.143267
142	Service des Espaces Verts	Service : Service des Espaces Verts	SRV-010	t	2025-11-20 21:29:20.143267	2025-11-20 21:29:20.143267
143	Service de la Sécurité	Service : Service de la Sécurité	SRV-011	t	2025-11-20 21:29:20.143267	2025-11-20 21:29:20.143267
144	Service de la Communication	Service : Service de la Communication	SRV-012	t	2025-11-20 21:29:20.143267	2025-11-20 21:29:20.143267
145	Service des Archives	Service : Service des Archives	SRV-013	t	2025-11-20 21:29:20.143267	2025-11-20 21:29:20.143267
146	Service de l'État Civil	Service : Service de l'État Civil	SRV-014	t	2025-11-20 21:29:20.143267	2025-11-20 21:29:20.143267
147	Service de la Population	Service : Service de la Population	SRV-015	t	2025-11-20 21:29:20.143267	2025-11-20 21:29:20.143267
148	Service de l'Action Sociale	Service : Service de l'Action Sociale	SRV-016	t	2025-11-20 21:29:20.143267	2025-11-20 21:29:20.143267
565	Service 17	Service : Service 17	SRV-017	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
566	Service 18	Service : Service 18	SRV-018	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
567	Service 19	Service : Service 19	SRV-019	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
568	Service 20	Service : Service 20	SRV-020	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
569	Service 21	Service : Service 21	SRV-021	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
570	Service 22	Service : Service 22	SRV-022	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
571	Service 23	Service : Service 23	SRV-023	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
572	Service 24	Service : Service 24	SRV-024	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
573	Service 25	Service : Service 25	SRV-025	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
574	Service 26	Service : Service 26	SRV-026	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
575	Service 27	Service : Service 27	SRV-027	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
576	Service 28	Service : Service 28	SRV-028	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
577	Service 29	Service : Service 29	SRV-029	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
578	Service 30	Service : Service 30	SRV-030	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
579	Service 31	Service : Service 31	SRV-031	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
580	Service 32	Service : Service 32	SRV-032	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
581	Service 33	Service : Service 33	SRV-033	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
582	Service 34	Service : Service 34	SRV-034	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
583	Service 35	Service : Service 35	SRV-035	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
584	Service 36	Service : Service 36	SRV-036	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
585	Service 37	Service : Service 37	SRV-037	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
586	Service 38	Service : Service 38	SRV-038	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
587	Service 39	Service : Service 39	SRV-039	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
588	Service 40	Service : Service 40	SRV-040	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
589	Service 41	Service : Service 41	SRV-041	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
590	Service 42	Service : Service 42	SRV-042	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
591	Service 43	Service : Service 43	SRV-043	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
592	Service 44	Service : Service 44	SRV-044	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
593	Service 45	Service : Service 45	SRV-045	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
594	Service 46	Service : Service 46	SRV-046	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
595	Service 47	Service : Service 47	SRV-047	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
596	Service 48	Service : Service 48	SRV-048	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
597	Service 49	Service : Service 49	SRV-049	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
598	Service 50	Service : Service 50	SRV-050	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
\.


--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- Data for Name: taxe; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.taxe (id, nom, code, description, montant, montant_variable, periodicite, type_taxe_id, service_id, commission_pourcentage, actif, created_at, updated_at) FROM stdin;
1	Taxe de Marché Journalière	TAX-001	Taxe quotidienne pour les vendeurs de marché	1000.00	f	journaliere	139	134	5.00	t	2025-11-20 21:29:20.202685	2025-11-20 21:29:20.202685
2	Taxe de Marché Mensuelle	TAX-002	Taxe mensuelle pour les vendeurs de marché	25000.00	f	mensuelle	139	134	5.00	t	2025-11-20 21:29:20.202685	2025-11-20 21:29:20.202685
3	Taxe d'Occupation Domaine Public	TAX-003	Taxe pour occupation de l'espace public	5000.00	t	mensuelle	139	134	3.00	t	2025-11-20 21:29:20.202685	2025-11-20 21:29:20.202685
4	Taxe Commerciale Mensuelle	TAX-004	Taxe sur les activités commerciales	15000.00	f	mensuelle	139	134	4.00	t	2025-11-20 21:29:20.202685	2025-11-20 21:29:20.202685
5	Taxe de Stationnement	TAX-005	Taxe de stationnement journalière	500.00	f	journaliere	139	134	2.00	t	2025-11-20 21:29:20.202685	2025-11-20 21:29:20.202685
6	Taxe d'Enlèvement Ordures	TAX-006	Taxe pour l'enlèvement des ordures ménagères	3000.00	f	mensuelle	139	134	0.00	t	2025-11-20 21:29:20.202685	2025-11-20 21:29:20.202685
7	Taxe 7	TAX-007	Description de la taxe 7	2000.00	t	hebdomadaire	150	144	2.06	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
8	Taxe 8	TAX-008	Description de la taxe 8	25000.00	t	trimestrielle	153	135	8.96	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
9	Taxe 9	TAX-009	Description de la taxe 9	30000.00	t	journaliere	153	138	7.90	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
10	Taxe 10	TAX-010	Description de la taxe 10	2000.00	t	hebdomadaire	154	134	1.02	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
11	Taxe 11	TAX-011	Description de la taxe 11	30000.00	f	trimestrielle	157	145	1.83	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
12	Taxe 12	TAX-012	Description de la taxe 12	20000.00	t	mensuelle	142	135	4.62	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
13	Taxe 13	TAX-013	Description de la taxe 13	15000.00	t	mensuelle	141	140	2.91	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
14	Taxe 14	TAX-014	Description de la taxe 14	3000.00	f	hebdomadaire	143	134	6.59	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
15	Taxe 15	TAX-015	Description de la taxe 15	3000.00	f	mensuelle	144	144	1.96	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
16	Taxe 16	TAX-016	Description de la taxe 16	30000.00	f	journaliere	157	136	1.81	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
17	Taxe 17	TAX-017	Description de la taxe 17	20000.00	t	journaliere	154	139	7.07	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
18	Taxe 18	TAX-018	Description de la taxe 18	2000.00	f	trimestrielle	140	138	5.65	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
19	Taxe 19	TAX-019	Description de la taxe 19	10000.00	f	journaliere	149	145	0.21	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
20	Taxe 20	TAX-020	Description de la taxe 20	25000.00	f	journaliere	147	133	9.02	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
21	Taxe 21	TAX-021	Description de la taxe 21	2000.00	f	journaliere	139	139	4.54	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
22	Taxe 22	TAX-022	Description de la taxe 22	3000.00	f	journaliere	154	133	4.41	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
23	Taxe 23	TAX-023	Description de la taxe 23	5000.00	t	hebdomadaire	151	145	9.39	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
24	Taxe 24	TAX-024	Description de la taxe 24	1000.00	f	trimestrielle	157	146	8.51	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
25	Taxe 25	TAX-025	Description de la taxe 25	10000.00	t	hebdomadaire	143	137	0.91	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
26	Taxe 26	TAX-026	Description de la taxe 26	15000.00	f	mensuelle	145	136	0.07	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
27	Taxe 27	TAX-027	Description de la taxe 27	3000.00	t	journaliere	143	134	4.07	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
28	Taxe 28	TAX-028	Description de la taxe 28	10000.00	t	mensuelle	146	140	6.99	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
29	Taxe 29	TAX-029	Description de la taxe 29	10000.00	t	trimestrielle	142	148	2.96	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
30	Taxe 30	TAX-030	Description de la taxe 30	3000.00	t	journaliere	150	143	5.56	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
31	Taxe 31	TAX-031	Description de la taxe 31	5000.00	f	mensuelle	142	135	6.11	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
32	Taxe 32	TAX-032	Description de la taxe 32	500.00	f	trimestrielle	151	137	3.46	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
33	Taxe 33	TAX-033	Description de la taxe 33	10000.00	f	hebdomadaire	140	141	9.47	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
34	Taxe 34	TAX-034	Description de la taxe 34	30000.00	f	journaliere	143	141	1.73	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
35	Taxe 35	TAX-035	Description de la taxe 35	10000.00	f	mensuelle	145	143	3.68	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
36	Taxe 36	TAX-036	Description de la taxe 36	15000.00	t	trimestrielle	150	147	5.59	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
37	Taxe 37	TAX-037	Description de la taxe 37	10000.00	f	trimestrielle	157	136	9.74	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
38	Taxe 38	TAX-038	Description de la taxe 38	2000.00	f	mensuelle	148	146	1.76	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
39	Taxe 39	TAX-039	Description de la taxe 39	20000.00	f	hebdomadaire	149	139	0.95	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
40	Taxe 40	TAX-040	Description de la taxe 40	30000.00	f	mensuelle	156	148	3.74	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
41	Taxe 41	TAX-041	Description de la taxe 41	1000.00	t	hebdomadaire	146	142	7.02	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
42	Taxe 42	TAX-042	Description de la taxe 42	10000.00	f	hebdomadaire	147	135	2.28	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
43	Taxe 43	TAX-043	Description de la taxe 43	15000.00	t	trimestrielle	143	146	8.72	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
44	Taxe 44	TAX-044	Description de la taxe 44	30000.00	t	journaliere	146	135	5.50	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
45	Taxe 45	TAX-045	Description de la taxe 45	20000.00	f	trimestrielle	152	141	0.35	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
46	Taxe 46	TAX-046	Description de la taxe 46	500.00	t	mensuelle	151	137	9.96	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
47	Taxe 47	TAX-047	Description de la taxe 47	15000.00	f	mensuelle	148	134	0.28	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
48	Taxe 48	TAX-048	Description de la taxe 48	10000.00	t	mensuelle	147	144	3.15	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
49	Taxe 49	TAX-049	Description de la taxe 49	3000.00	t	mensuelle	150	135	4.20	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
50	Taxe 50	TAX-050	Description de la taxe 50	500.00	t	journaliere	153	138	4.34	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
51	Taxe 51	TAX-051	Description de la taxe 51	25000.00	t	hebdomadaire	151	148	2.84	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
52	Taxe 52	TAX-052	Description de la taxe 52	1000.00	t	mensuelle	141	139	9.40	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
53	Taxe 53	TAX-053	Description de la taxe 53	25000.00	f	trimestrielle	139	142	0.04	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
54	Taxe 54	TAX-054	Description de la taxe 54	500.00	f	hebdomadaire	148	144	7.08	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
55	Taxe 55	TAX-055	Description de la taxe 55	3000.00	t	journaliere	142	134	7.81	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
56	Taxe 56	TAX-056	Description de la taxe 56	30000.00	t	mensuelle	145	142	8.44	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
57	Taxe 57	TAX-057	Description de la taxe 57	15000.00	t	trimestrielle	141	145	4.71	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
58	Taxe 58	TAX-058	Description de la taxe 58	25000.00	f	hebdomadaire	148	143	0.76	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
59	Taxe 59	TAX-059	Description de la taxe 59	30000.00	t	hebdomadaire	145	143	8.92	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
60	Taxe 60	TAX-060	Description de la taxe 60	20000.00	f	trimestrielle	143	133	0.34	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
61	Taxe 61	TAX-061	Description de la taxe 61	5000.00	f	hebdomadaire	147	145	7.08	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
62	Taxe 62	TAX-062	Description de la taxe 62	15000.00	f	trimestrielle	147	133	3.95	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
63	Taxe 63	TAX-063	Description de la taxe 63	3000.00	t	mensuelle	143	141	6.15	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
64	Taxe 64	TAX-064	Description de la taxe 64	30000.00	t	trimestrielle	142	136	1.33	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
65	Taxe 65	TAX-065	Description de la taxe 65	10000.00	t	trimestrielle	152	137	2.97	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
66	Taxe 66	TAX-066	Description de la taxe 66	20000.00	f	mensuelle	148	136	9.19	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
67	Taxe 67	TAX-067	Description de la taxe 67	25000.00	t	hebdomadaire	150	137	5.45	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
68	Taxe 68	TAX-068	Description de la taxe 68	3000.00	t	hebdomadaire	143	144	3.68	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
69	Taxe 69	TAX-069	Description de la taxe 69	25000.00	t	journaliere	153	147	4.81	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
70	Taxe 70	TAX-070	Description de la taxe 70	30000.00	t	hebdomadaire	147	145	1.13	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
71	Taxe 71	TAX-071	Description de la taxe 71	25000.00	t	trimestrielle	141	147	1.13	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
72	Taxe 72	TAX-072	Description de la taxe 72	2000.00	t	journaliere	149	134	9.18	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
73	Taxe 73	TAX-073	Description de la taxe 73	5000.00	f	mensuelle	139	141	7.17	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
74	Taxe 74	TAX-074	Description de la taxe 74	1000.00	t	mensuelle	142	148	4.66	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
75	Taxe 75	TAX-075	Description de la taxe 75	2000.00	t	journaliere	140	140	2.84	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
76	Taxe 76	TAX-076	Description de la taxe 76	10000.00	t	mensuelle	145	134	8.69	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
77	Taxe 77	TAX-077	Description de la taxe 77	500.00	t	mensuelle	152	134	2.45	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
78	Taxe 78	TAX-078	Description de la taxe 78	3000.00	f	trimestrielle	143	146	5.76	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
79	Taxe 79	TAX-079	Description de la taxe 79	30000.00	f	hebdomadaire	156	147	9.01	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
80	Taxe 80	TAX-080	Description de la taxe 80	10000.00	t	journaliere	151	137	5.47	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
81	Taxe 81	TAX-081	Description de la taxe 81	500.00	t	journaliere	149	145	4.82	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
82	Taxe 82	TAX-082	Description de la taxe 82	3000.00	t	journaliere	143	135	5.02	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
83	Taxe 83	TAX-083	Description de la taxe 83	10000.00	t	mensuelle	156	140	3.08	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
84	Taxe 84	TAX-084	Description de la taxe 84	30000.00	t	hebdomadaire	146	147	9.47	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
85	Taxe 85	TAX-085	Description de la taxe 85	25000.00	t	journaliere	143	137	8.67	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
86	Taxe 86	TAX-086	Description de la taxe 86	3000.00	f	mensuelle	150	144	0.33	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
87	Taxe 87	TAX-087	Description de la taxe 87	500.00	f	mensuelle	157	146	5.62	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
88	Taxe 88	TAX-088	Description de la taxe 88	10000.00	t	trimestrielle	148	140	8.67	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
89	Taxe 89	TAX-089	Description de la taxe 89	500.00	t	journaliere	145	138	8.63	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
90	Taxe 90	TAX-090	Description de la taxe 90	30000.00	f	mensuelle	152	133	6.42	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
91	Taxe 91	TAX-091	Description de la taxe 91	500.00	f	mensuelle	153	144	3.76	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
92	Taxe 92	TAX-092	Description de la taxe 92	25000.00	t	trimestrielle	152	146	7.92	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
93	Taxe 93	TAX-093	Description de la taxe 93	1000.00	t	journaliere	152	148	5.69	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
94	Taxe 94	TAX-094	Description de la taxe 94	500.00	t	trimestrielle	146	145	6.02	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
95	Taxe 95	TAX-095	Description de la taxe 95	2000.00	f	mensuelle	149	143	0.67	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
96	Taxe 96	TAX-096	Description de la taxe 96	500.00	f	journaliere	154	135	4.26	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
97	Taxe 97	TAX-097	Description de la taxe 97	2000.00	t	trimestrielle	156	143	9.06	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
98	Taxe 98	TAX-098	Description de la taxe 98	5000.00	t	trimestrielle	140	143	0.24	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
99	Taxe 99	TAX-099	Description de la taxe 99	15000.00	t	hebdomadaire	144	139	5.09	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
100	Taxe 100	TAX-100	Description de la taxe 100	15000.00	t	journaliere	150	141	2.55	t	2025-11-20 21:29:20.212912	2025-11-20 21:29:20.212912
\.


--
-- Data for Name: type_contribuable; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.type_contribuable (id, nom, code, description, actif, created_at, updated_at) FROM stdin;
149	Particulier	TC-001	\N	t	2025-11-20 21:29:20.117482	2025-11-20 21:29:20.117482
150	Entreprise	TC-002	\N	t	2025-11-20 21:29:20.117482	2025-11-20 21:29:20.117482
151	Commerce	TC-003	\N	t	2025-11-20 21:29:20.117482	2025-11-20 21:29:20.117482
152	Marché	TC-004	\N	t	2025-11-20 21:29:20.117482	2025-11-20 21:29:20.117482
153	Transport	TC-005	\N	t	2025-11-20 21:29:20.117482	2025-11-20 21:29:20.117482
154	Restaurant	TC-006	\N	t	2025-11-20 21:29:20.117482	2025-11-20 21:29:20.117482
155	Hôtel	TC-007	\N	t	2025-11-20 21:29:20.117482	2025-11-20 21:29:20.117482
156	Boutique	TC-008	\N	t	2025-11-20 21:29:20.117482	2025-11-20 21:29:20.117482
157	Artisan	TC-009	Type de contribuable : Artisan	t	2025-11-20 21:29:20.124481	2025-11-20 21:29:20.124481
158	Prestataire	TC-010	Type de contribuable : Prestataire	t	2025-11-20 21:29:20.124481	2025-11-20 21:29:20.124481
159	Vendeur ambulant	TC-011	Type de contribuable : Vendeur ambulant	t	2025-11-20 21:29:20.124481	2025-11-20 21:29:20.124481
160	Taxi	TC-012	Type de contribuable : Taxi	t	2025-11-20 21:29:20.124481	2025-11-20 21:29:20.124481
161	Moto-taxi	TC-013	Type de contribuable : Moto-taxi	t	2025-11-20 21:29:20.124481	2025-11-20 21:29:20.124481
162	Garage	TC-014	Type de contribuable : Garage	t	2025-11-20 21:29:20.124481	2025-11-20 21:29:20.124481
163	Pharmacie	TC-015	Type de contribuable : Pharmacie	t	2025-11-20 21:29:20.124481	2025-11-20 21:29:20.124481
164	Superette	TC-016	Type de contribuable : Superette	t	2025-11-20 21:29:20.124481	2025-11-20 21:29:20.124481
165	Boulangerie	TC-017	Type de contribuable : Boulangerie	t	2025-11-20 21:29:20.124481	2025-11-20 21:29:20.124481
166	Coiffure	TC-018	Type de contribuable : Coiffure	t	2025-11-20 21:29:20.124481	2025-11-20 21:29:20.124481
167	Salon de beauté	TC-019	Type de contribuable : Salon de beauté	t	2025-11-20 21:29:20.124481	2025-11-20 21:29:20.124481
168	Cybercafé	TC-020	Type de contribuable : Cybercafé	t	2025-11-20 21:29:20.124481	2025-11-20 21:29:20.124481
169	Imprimerie	TC-021	Type de contribuable : Imprimerie	t	2025-11-20 21:29:20.124481	2025-11-20 21:29:20.124481
170	Photographe	TC-022	Type de contribuable : Photographe	t	2025-11-20 21:29:20.124481	2025-11-20 21:29:20.124481
171	Bijoutier	TC-023	Type de contribuable : Bijoutier	t	2025-11-20 21:29:20.124481	2025-11-20 21:29:20.124481
596	Type 24	TC-024	Type de contribuable : Type 24	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
597	Type 25	TC-025	Type de contribuable : Type 25	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
598	Type 26	TC-026	Type de contribuable : Type 26	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
599	Type 27	TC-027	Type de contribuable : Type 27	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
600	Type 28	TC-028	Type de contribuable : Type 28	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
601	Type 29	TC-029	Type de contribuable : Type 29	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
602	Type 30	TC-030	Type de contribuable : Type 30	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
603	Type 31	TC-031	Type de contribuable : Type 31	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
604	Type 32	TC-032	Type de contribuable : Type 32	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
605	Type 33	TC-033	Type de contribuable : Type 33	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
606	Type 34	TC-034	Type de contribuable : Type 34	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
607	Type 35	TC-035	Type de contribuable : Type 35	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
608	Type 36	TC-036	Type de contribuable : Type 36	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
609	Type 37	TC-037	Type de contribuable : Type 37	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
610	Type 38	TC-038	Type de contribuable : Type 38	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
611	Type 39	TC-039	Type de contribuable : Type 39	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
612	Type 40	TC-040	Type de contribuable : Type 40	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
613	Type 41	TC-041	Type de contribuable : Type 41	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
614	Type 42	TC-042	Type de contribuable : Type 42	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
615	Type 43	TC-043	Type de contribuable : Type 43	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
616	Type 44	TC-044	Type de contribuable : Type 44	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
617	Type 45	TC-045	Type de contribuable : Type 45	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
618	Type 46	TC-046	Type de contribuable : Type 46	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
619	Type 47	TC-047	Type de contribuable : Type 47	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
620	Type 48	TC-048	Type de contribuable : Type 48	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
621	Type 49	TC-049	Type de contribuable : Type 49	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
622	Type 50	TC-050	Type de contribuable : Type 50	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
\.


--
-- Data for Name: type_taxe; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.type_taxe (id, nom, code, description, actif, created_at, updated_at) FROM stdin;
139	Taxe de Marché	TT-001	Taxe sur les activités de marché	t	2025-11-20 21:29:20.165491	2025-11-20 21:29:20.165491
140	Taxe d'Occupation du Domaine Public	TT-002	Taxe pour occupation de l'espace public	t	2025-11-20 21:29:20.165491	2025-11-20 21:29:20.165491
141	Taxe sur les Activités Commerciales	TT-003	Taxe sur les activités commerciales	t	2025-11-20 21:29:20.165491	2025-11-20 21:29:20.165491
142	Taxe de Stationnement	TT-004	Taxe de stationnement	t	2025-11-20 21:29:20.165491	2025-11-20 21:29:20.165491
143	Taxe de Voirie	TT-005	Taxe de voirie	t	2025-11-20 21:29:20.165491	2025-11-20 21:29:20.165491
144	Taxe d'Enlèvement des Ordures	TT-006	Taxe pour l'enlèvement des ordures	t	2025-11-20 21:29:20.165491	2025-11-20 21:29:20.165491
145	Taxe sur les Transports	TT-007	Taxe sur les activités de transport	t	2025-11-20 21:29:20.165491	2025-11-20 21:29:20.165491
146	Taxe sur les Débits de Boissons	TT-008	Taxe sur les débits de boissons	t	2025-11-20 21:29:20.165491	2025-11-20 21:29:20.165491
147	Taxe sur les Hôtels	TT-009	Taxe sur les établissements hôteliers	t	2025-11-20 21:29:20.165491	2025-11-20 21:29:20.165491
148	Taxe sur les Publicités	TT-010	Taxe sur les publicités et enseignes	t	2025-11-20 21:29:20.165491	2025-11-20 21:29:20.165491
149	Taxe sur les Spectacles	TT-011	Type de taxe : Taxe sur les Spectacles	t	2025-11-20 21:29:20.168505	2025-11-20 21:29:20.168505
150	Taxe sur les Jeux	TT-012	Type de taxe : Taxe sur les Jeux	t	2025-11-20 21:29:20.168505	2025-11-20 21:29:20.168505
151	Taxe sur les Locations	TT-013	Type de taxe : Taxe sur les Locations	t	2025-11-20 21:29:20.168505	2025-11-20 21:29:20.168505
152	Taxe sur les Terrains	TT-014	Type de taxe : Taxe sur les Terrains	t	2025-11-20 21:29:20.168505	2025-11-20 21:29:20.168505
153	Taxe sur les Constructions	TT-015	Type de taxe : Taxe sur les Constructions	t	2025-11-20 21:29:20.168505	2025-11-20 21:29:20.168505
154	Taxe sur les Véhicules	TT-016	Type de taxe : Taxe sur les Véhicules	t	2025-11-20 21:29:20.168505	2025-11-20 21:29:20.168505
155	Taxe sur les Animaux	TT-017	Type de taxe : Taxe sur les Animaux	t	2025-11-20 21:29:20.168505	2025-11-20 21:29:20.168505
156	Taxe sur les Événements	TT-018	Type de taxe : Taxe sur les Événements	t	2025-11-20 21:29:20.168505	2025-11-20 21:29:20.168505
157	Taxe sur les Installations	TT-019	Type de taxe : Taxe sur les Installations	t	2025-11-20 21:29:20.168505	2025-11-20 21:29:20.168505
577	Type Taxe 20	TT-020	Description type taxe 20	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
578	Type Taxe 21	TT-021	Description type taxe 21	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
579	Type Taxe 22	TT-022	Description type taxe 22	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
580	Type Taxe 23	TT-023	Description type taxe 23	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
581	Type Taxe 24	TT-024	Description type taxe 24	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
582	Type Taxe 25	TT-025	Description type taxe 25	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
583	Type Taxe 26	TT-026	Description type taxe 26	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
584	Type Taxe 27	TT-027	Description type taxe 27	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
585	Type Taxe 28	TT-028	Description type taxe 28	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
586	Type Taxe 29	TT-029	Description type taxe 29	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
587	Type Taxe 30	TT-030	Description type taxe 30	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
588	Type Taxe 31	TT-031	Description type taxe 31	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
589	Type Taxe 32	TT-032	Description type taxe 32	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
590	Type Taxe 33	TT-033	Description type taxe 33	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
591	Type Taxe 34	TT-034	Description type taxe 34	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
592	Type Taxe 35	TT-035	Description type taxe 35	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
593	Type Taxe 36	TT-036	Description type taxe 36	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
594	Type Taxe 37	TT-037	Description type taxe 37	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
595	Type Taxe 38	TT-038	Description type taxe 38	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
596	Type Taxe 39	TT-039	Description type taxe 39	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
597	Type Taxe 40	TT-040	Description type taxe 40	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
598	Type Taxe 41	TT-041	Description type taxe 41	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
599	Type Taxe 42	TT-042	Description type taxe 42	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
600	Type Taxe 43	TT-043	Description type taxe 43	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
601	Type Taxe 44	TT-044	Description type taxe 44	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
602	Type Taxe 45	TT-045	Description type taxe 45	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
603	Type Taxe 46	TT-046	Description type taxe 46	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
604	Type Taxe 47	TT-047	Description type taxe 47	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
605	Type Taxe 48	TT-048	Description type taxe 48	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
606	Type Taxe 49	TT-049	Description type taxe 49	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
607	Type Taxe 50	TT-050	Description type taxe 50	t	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
\.


--
-- Data for Name: utilisateur; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.utilisateur (id, nom, prenom, email, telephone, mot_de_passe_hash, role, actif, derniere_connexion, created_at, updated_at) FROM stdin;
2	NDONG	Marie	user1@mairie-libreville.ga	+241063000001	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_back_office	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
3	OBAME	Pierre	user2@mairie-libreville.ga	+241063000002	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_front_office	t	2025-11-15 10:12:42.289681	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
4	BONGO	Paul	user3@mairie-libreville.ga	+241063000003	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	controleur_interne	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
5	ESSONO	Sophie	user4@mairie-libreville.ga	+241063000004	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	collecteur	f	2025-11-04 05:22:45.638806	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
6	MVE	Luc	user5@mairie-libreville.ga	+241063000005	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	admin	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
7	MINTSA	Anne	user6@mairie-libreville.ga	+241063000006	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_back_office	t	2025-10-23 23:48:18.673569	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
8	MBOUMBA	David	user7@mairie-libreville.ga	+241063000007	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_front_office	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
9	NDONG	Jean	user8@mairie-libreville.ga	+241063000008	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	controleur_interne	f	2025-11-15 01:49:33.899711	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
10	OBAME	Marie	user9@mairie-libreville.ga	+241063000009	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	collecteur	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
11	BONGO	Pierre	user10@mairie-libreville.ga	+241063000010	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	admin	t	2025-11-10 13:18:50.768492	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
12	ESSONO	Paul	user11@mairie-libreville.ga	+241063000011	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_back_office	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
13	MVE	Sophie	user12@mairie-libreville.ga	+241063000012	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_front_office	f	2025-11-13 01:58:32.206235	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
14	MINTSA	Luc	user13@mairie-libreville.ga	+241063000013	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	controleur_interne	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
15	MBOUMBA	Anne	user14@mairie-libreville.ga	+241063000014	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	collecteur	t	2025-11-09 00:00:05.130438	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
16	NDONG	David	user15@mairie-libreville.ga	+241063000015	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	admin	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
17	OBAME	Jean	user16@mairie-libreville.ga	+241063000016	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_back_office	f	2025-11-13 22:37:40.954319	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
18	BONGO	Marie	user17@mairie-libreville.ga	+241063000017	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_front_office	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
19	ESSONO	Pierre	user18@mairie-libreville.ga	+241063000018	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	controleur_interne	t	2025-10-31 05:09:22.911137	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
20	MVE	Paul	user19@mairie-libreville.ga	+241063000019	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	collecteur	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
21	MINTSA	Sophie	user20@mairie-libreville.ga	+241063000020	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	admin	f	2025-11-09 03:28:22.269075	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
22	MBOUMBA	Luc	user21@mairie-libreville.ga	+241063000021	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_back_office	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
23	NDONG	Anne	user22@mairie-libreville.ga	+241063000022	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_front_office	t	2025-11-19 22:20:25.102268	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
24	OBAME	David	user23@mairie-libreville.ga	+241063000023	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	controleur_interne	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
25	BONGO	Jean	user24@mairie-libreville.ga	+241063000024	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	collecteur	f	2025-10-26 12:40:29.115204	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
26	ESSONO	Marie	user25@mairie-libreville.ga	+241063000025	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	admin	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
27	MVE	Pierre	user26@mairie-libreville.ga	+241063000026	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_back_office	t	2025-11-09 16:53:24.622753	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
28	MINTSA	Paul	user27@mairie-libreville.ga	+241063000027	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_front_office	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
29	MBOUMBA	Sophie	user28@mairie-libreville.ga	+241063000028	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	controleur_interne	f	2025-11-15 19:03:58.148097	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
30	NDONG	Luc	user29@mairie-libreville.ga	+241063000029	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	collecteur	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
31	OBAME	Anne	user30@mairie-libreville.ga	+241063000030	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	admin	t	2025-10-23 21:52:21.121149	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
32	BONGO	David	user31@mairie-libreville.ga	+241063000031	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_back_office	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
33	ESSONO	Jean	user32@mairie-libreville.ga	+241063000032	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_front_office	f	2025-11-04 23:34:22.727327	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
34	MVE	Marie	user33@mairie-libreville.ga	+241063000033	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	controleur_interne	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
35	MINTSA	Pierre	user34@mairie-libreville.ga	+241063000034	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	collecteur	t	2025-11-05 13:37:27.614067	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
36	MBOUMBA	Paul	user35@mairie-libreville.ga	+241063000035	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	admin	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
37	NDONG	Sophie	user36@mairie-libreville.ga	+241063000036	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_back_office	f	2025-11-16 16:35:16.80156	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
38	OBAME	Luc	user37@mairie-libreville.ga	+241063000037	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_front_office	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
39	BONGO	Anne	user38@mairie-libreville.ga	+241063000038	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	controleur_interne	t	2025-10-22 18:45:03.201236	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
40	ESSONO	David	user39@mairie-libreville.ga	+241063000039	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	collecteur	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
41	MVE	Jean	user40@mairie-libreville.ga	+241063000040	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	admin	f	2025-10-22 08:19:12.265502	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
42	MINTSA	Marie	user41@mairie-libreville.ga	+241063000041	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_back_office	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
43	MBOUMBA	Pierre	user42@mairie-libreville.ga	+241063000042	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_front_office	t	2025-11-07 16:01:33.325985	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
44	NDONG	Paul	user43@mairie-libreville.ga	+241063000043	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	controleur_interne	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
45	OBAME	Sophie	user44@mairie-libreville.ga	+241063000044	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	collecteur	f	2025-11-19 13:24:47.265523	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
46	BONGO	Luc	user45@mairie-libreville.ga	+241063000045	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	admin	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
47	ESSONO	Anne	user46@mairie-libreville.ga	+241063000046	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_back_office	t	2025-11-17 00:00:08.208066	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
48	MVE	David	user47@mairie-libreville.ga	+241063000047	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	agent_front_office	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
49	MINTSA	Jean	user48@mairie-libreville.ga	+241063000048	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	controleur_interne	f	2025-11-19 23:04:51.7253	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
50	MBOUMBA	Marie	user49@mairie-libreville.ga	+241063000049	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5	collecteur	t	\N	2025-11-20 22:59:10.253041	2025-11-20 22:59:10.253041
1	Admin	SystÃ¨me	admin@mairie-libreville.ga	+241062345678	$2b$12$V/uNhcyQKYI9NREdSPaRJ.t54PgS4uUIvwCEVS0uDXxkj9A7O/u9a	admin	t	2025-11-22 09:31:52.675294	2025-11-20 22:59:10.253041	2025-11-22 10:31:52.142727
\.


--
-- Data for Name: ville; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ville (id, nom, code, description, pays, actif, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: zone; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.zone (id, nom, code, description, actif, created_at, updated_at) FROM stdin;
303	Centre-ville	ZONE-001	Zone centrale de Libreville	t	2025-11-20 21:29:19.959435	2025-11-20 21:29:19.959435
304	Akanda	ZONE-002	Zone Akanda	t	2025-11-20 21:29:19.959435	2025-11-20 21:29:19.959435
305	Ntoum	ZONE-003	Zone Ntoum	t	2025-11-20 21:29:19.959435	2025-11-20 21:29:19.959435
306	Owendo	ZONE-004	Zone portuaire d'Owendo	t	2025-11-20 21:29:19.959435	2025-11-20 21:29:19.959435
307	Port-Gentil	ZONE-005	Zone Port-Gentil	t	2025-11-20 21:29:19.959435	2025-11-20 21:29:19.959435
308	Franceville	ZONE-006	Zone Franceville	t	2025-11-20 21:29:19.959435	2025-11-20 21:29:19.959435
309	Zone 7	ZONE-007	Zone géographique 7	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
310	Zone 8	ZONE-008	Zone géographique 8	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
311	Zone 9	ZONE-009	Zone géographique 9	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
312	Zone 10	ZONE-010	Zone géographique 10	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
313	Zone 11	ZONE-011	Zone géographique 11	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
314	Zone 12	ZONE-012	Zone géographique 12	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
315	Zone 13	ZONE-013	Zone géographique 13	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
316	Zone 14	ZONE-014	Zone géographique 14	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
317	Zone 15	ZONE-015	Zone géographique 15	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
318	Zone 16	ZONE-016	Zone géographique 16	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
319	Zone 17	ZONE-017	Zone géographique 17	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
320	Zone 18	ZONE-018	Zone géographique 18	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
321	Zone 19	ZONE-019	Zone géographique 19	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
322	Zone 20	ZONE-020	Zone géographique 20	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
323	Zone 21	ZONE-021	Zone géographique 21	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
324	Zone 22	ZONE-022	Zone géographique 22	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
325	Zone 23	ZONE-023	Zone géographique 23	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
326	Zone 24	ZONE-024	Zone géographique 24	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
327	Zone 25	ZONE-025	Zone géographique 25	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
328	Zone 26	ZONE-026	Zone géographique 26	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
329	Zone 27	ZONE-027	Zone géographique 27	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
330	Zone 28	ZONE-028	Zone géographique 28	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
331	Zone 29	ZONE-029	Zone géographique 29	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
332	Zone 30	ZONE-030	Zone géographique 30	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
333	Zone 31	ZONE-031	Zone géographique 31	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
334	Zone 32	ZONE-032	Zone géographique 32	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
335	Zone 33	ZONE-033	Zone géographique 33	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
336	Zone 34	ZONE-034	Zone géographique 34	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
337	Zone 35	ZONE-035	Zone géographique 35	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
338	Zone 36	ZONE-036	Zone géographique 36	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
339	Zone 37	ZONE-037	Zone géographique 37	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
340	Zone 38	ZONE-038	Zone géographique 38	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
341	Zone 39	ZONE-039	Zone géographique 39	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
342	Zone 40	ZONE-040	Zone géographique 40	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
343	Zone 41	ZONE-041	Zone géographique 41	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
344	Zone 42	ZONE-042	Zone géographique 42	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
345	Zone 43	ZONE-043	Zone géographique 43	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
346	Zone 44	ZONE-044	Zone géographique 44	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
347	Zone 45	ZONE-045	Zone géographique 45	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
348	Zone 46	ZONE-046	Zone géographique 46	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
349	Zone 47	ZONE-047	Zone géographique 47	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
350	Zone 48	ZONE-048	Zone géographique 48	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
351	Zone 49	ZONE-049	Zone géographique 49	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
352	Zone 50	ZONE-050	Zone géographique 50	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
353	Zone 51	ZONE-051	Zone géographique 51	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
354	Zone 52	ZONE-052	Zone géographique 52	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
355	Zone 53	ZONE-053	Zone géographique 53	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
356	Zone 54	ZONE-054	Zone géographique 54	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
357	Zone 55	ZONE-055	Zone géographique 55	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
358	Zone 56	ZONE-056	Zone géographique 56	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
359	Zone 57	ZONE-057	Zone géographique 57	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
360	Zone 58	ZONE-058	Zone géographique 58	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
361	Zone 59	ZONE-059	Zone géographique 59	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
362	Zone 60	ZONE-060	Zone géographique 60	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
363	Zone 61	ZONE-061	Zone géographique 61	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
364	Zone 62	ZONE-062	Zone géographique 62	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
365	Zone 63	ZONE-063	Zone géographique 63	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
366	Zone 64	ZONE-064	Zone géographique 64	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
367	Zone 65	ZONE-065	Zone géographique 65	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
368	Zone 66	ZONE-066	Zone géographique 66	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
369	Zone 67	ZONE-067	Zone géographique 67	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
370	Zone 68	ZONE-068	Zone géographique 68	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
371	Zone 69	ZONE-069	Zone géographique 69	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
372	Zone 70	ZONE-070	Zone géographique 70	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
373	Zone 71	ZONE-071	Zone géographique 71	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
374	Zone 72	ZONE-072	Zone géographique 72	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
375	Zone 73	ZONE-073	Zone géographique 73	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
376	Zone 74	ZONE-074	Zone géographique 74	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
377	Zone 75	ZONE-075	Zone géographique 75	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
378	Zone 76	ZONE-076	Zone géographique 76	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
379	Zone 77	ZONE-077	Zone géographique 77	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
380	Zone 78	ZONE-078	Zone géographique 78	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
381	Zone 79	ZONE-079	Zone géographique 79	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
382	Zone 80	ZONE-080	Zone géographique 80	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
383	Zone 81	ZONE-081	Zone géographique 81	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
384	Zone 82	ZONE-082	Zone géographique 82	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
385	Zone 83	ZONE-083	Zone géographique 83	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
386	Zone 84	ZONE-084	Zone géographique 84	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
387	Zone 85	ZONE-085	Zone géographique 85	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
388	Zone 86	ZONE-086	Zone géographique 86	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
389	Zone 87	ZONE-087	Zone géographique 87	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
390	Zone 88	ZONE-088	Zone géographique 88	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
391	Zone 89	ZONE-089	Zone géographique 89	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
392	Zone 90	ZONE-090	Zone géographique 90	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
393	Zone 91	ZONE-091	Zone géographique 91	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
394	Zone 92	ZONE-092	Zone géographique 92	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
395	Zone 93	ZONE-093	Zone géographique 93	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
396	Zone 94	ZONE-094	Zone géographique 94	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
397	Zone 95	ZONE-095	Zone géographique 95	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
398	Zone 96	ZONE-096	Zone géographique 96	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
399	Zone 97	ZONE-097	Zone géographique 97	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
400	Zone 98	ZONE-098	Zone géographique 98	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
401	Zone 99	ZONE-099	Zone géographique 99	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
402	Zone 100	ZONE-100	Zone géographique 100	t	2025-11-20 21:29:19.962533	2025-11-20 21:29:19.962533
\.


--
-- Data for Name: zone_geographique; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.zone_geographique (id, nom, type_zone, code, geometry, properties, quartier_id, actif, created_at, updated_at, geom) FROM stdin;
\.


--
-- Name: affectation_taxe_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.affectation_taxe_id_seq', 100, true);


--
-- Name: arrondissement_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.arrondissement_id_seq', 1, false);


--
-- Name: collecteur_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.collecteur_id_seq', 400, true);


--
-- Name: commune_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.commune_id_seq', 1, false);


--
-- Name: contribuable_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.contribuable_id_seq', 301, true);


--
-- Name: info_collecte_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.info_collecte_id_seq', 100, true);


--
-- Name: quartier_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quartier_id_seq', 851, true);


--
-- Name: quartier_parametrage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quartier_parametrage_id_seq', 1, false);


--
-- Name: role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.role_id_seq', 1, false);


--
-- Name: secteur_activite_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.secteur_activite_id_seq', 1, false);


--
-- Name: service_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.service_id_seq', 598, true);


--
-- Name: taxe_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.taxe_id_seq', 350, true);


--
-- Name: type_contribuable_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.type_contribuable_id_seq', 622, true);


--
-- Name: type_taxe_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.type_taxe_id_seq', 607, true);


--
-- Name: utilisateur_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.utilisateur_id_seq', 50, true);


--
-- Name: ville_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ville_id_seq', 1, false);


--
-- Name: zone_geographique_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.zone_geographique_id_seq', 1, false);


--
-- Name: zone_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.zone_id_seq', 852, true);


--
-- Name: affectation_taxe affectation_taxe_contribuable_id_taxe_id_date_debut_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.affectation_taxe
    ADD CONSTRAINT affectation_taxe_contribuable_id_taxe_id_date_debut_key UNIQUE (contribuable_id, taxe_id, date_debut);


--
-- Name: affectation_taxe affectation_taxe_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.affectation_taxe
    ADD CONSTRAINT affectation_taxe_pkey PRIMARY KEY (id);


--
-- Name: arrondissement arrondissement_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.arrondissement
    ADD CONSTRAINT arrondissement_code_key UNIQUE (code);


--
-- Name: arrondissement arrondissement_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.arrondissement
    ADD CONSTRAINT arrondissement_pkey PRIMARY KEY (id);


--
-- Name: collecteur collecteur_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collecteur
    ADD CONSTRAINT collecteur_email_key UNIQUE (email);


--
-- Name: collecteur collecteur_matricule_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collecteur
    ADD CONSTRAINT collecteur_matricule_key UNIQUE (matricule);


--
-- Name: collecteur collecteur_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collecteur
    ADD CONSTRAINT collecteur_pkey PRIMARY KEY (id);


--
-- Name: collecteur collecteur_telephone_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collecteur
    ADD CONSTRAINT collecteur_telephone_key UNIQUE (telephone);


--
-- Name: commune commune_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commune
    ADD CONSTRAINT commune_code_key UNIQUE (code);


--
-- Name: commune commune_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commune
    ADD CONSTRAINT commune_pkey PRIMARY KEY (id);


--
-- Name: contribuable contribuable_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contribuable
    ADD CONSTRAINT contribuable_email_key UNIQUE (email);


--
-- Name: contribuable contribuable_numero_identification_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contribuable
    ADD CONSTRAINT contribuable_numero_identification_key UNIQUE (numero_identification);


--
-- Name: contribuable contribuable_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contribuable
    ADD CONSTRAINT contribuable_pkey PRIMARY KEY (id);


--
-- Name: contribuable contribuable_telephone_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contribuable
    ADD CONSTRAINT contribuable_telephone_key UNIQUE (telephone);


--
-- Name: info_collecte info_collecte_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.info_collecte
    ADD CONSTRAINT info_collecte_pkey PRIMARY KEY (id);


--
-- Name: info_collecte info_collecte_reference_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.info_collecte
    ADD CONSTRAINT info_collecte_reference_key UNIQUE (reference);


--
-- Name: quartier quartier_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quartier
    ADD CONSTRAINT quartier_code_key UNIQUE (code);


--
-- Name: quartier_parametrage quartier_parametrage_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quartier_parametrage
    ADD CONSTRAINT quartier_parametrage_code_key UNIQUE (code);


--
-- Name: quartier_parametrage quartier_parametrage_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quartier_parametrage
    ADD CONSTRAINT quartier_parametrage_pkey PRIMARY KEY (id);


--
-- Name: quartier quartier_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quartier
    ADD CONSTRAINT quartier_pkey PRIMARY KEY (id);


--
-- Name: role role_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT role_code_key UNIQUE (code);


--
-- Name: role role_nom_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT role_nom_key UNIQUE (nom);


--
-- Name: role role_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT role_pkey PRIMARY KEY (id);


--
-- Name: secteur_activite secteur_activite_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.secteur_activite
    ADD CONSTRAINT secteur_activite_code_key UNIQUE (code);


--
-- Name: secteur_activite secteur_activite_nom_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.secteur_activite
    ADD CONSTRAINT secteur_activite_nom_key UNIQUE (nom);


--
-- Name: secteur_activite secteur_activite_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.secteur_activite
    ADD CONSTRAINT secteur_activite_pkey PRIMARY KEY (id);


--
-- Name: service service_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service
    ADD CONSTRAINT service_code_key UNIQUE (code);


--
-- Name: service service_nom_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service
    ADD CONSTRAINT service_nom_key UNIQUE (nom);


--
-- Name: service service_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service
    ADD CONSTRAINT service_pkey PRIMARY KEY (id);


--
-- Name: taxe taxe_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxe
    ADD CONSTRAINT taxe_code_key UNIQUE (code);


--
-- Name: taxe taxe_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxe
    ADD CONSTRAINT taxe_pkey PRIMARY KEY (id);


--
-- Name: type_contribuable type_contribuable_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_contribuable
    ADD CONSTRAINT type_contribuable_code_key UNIQUE (code);


--
-- Name: type_contribuable type_contribuable_nom_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_contribuable
    ADD CONSTRAINT type_contribuable_nom_key UNIQUE (nom);


--
-- Name: type_contribuable type_contribuable_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_contribuable
    ADD CONSTRAINT type_contribuable_pkey PRIMARY KEY (id);


--
-- Name: type_taxe type_taxe_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_taxe
    ADD CONSTRAINT type_taxe_code_key UNIQUE (code);


--
-- Name: type_taxe type_taxe_nom_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_taxe
    ADD CONSTRAINT type_taxe_nom_key UNIQUE (nom);


--
-- Name: type_taxe type_taxe_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_taxe
    ADD CONSTRAINT type_taxe_pkey PRIMARY KEY (id);


--
-- Name: utilisateur utilisateur_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.utilisateur
    ADD CONSTRAINT utilisateur_email_key UNIQUE (email);


--
-- Name: utilisateur utilisateur_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.utilisateur
    ADD CONSTRAINT utilisateur_pkey PRIMARY KEY (id);


--
-- Name: utilisateur utilisateur_telephone_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.utilisateur
    ADD CONSTRAINT utilisateur_telephone_key UNIQUE (telephone);


--
-- Name: ville ville_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ville
    ADD CONSTRAINT ville_code_key UNIQUE (code);


--
-- Name: ville ville_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ville
    ADD CONSTRAINT ville_pkey PRIMARY KEY (id);


--
-- Name: zone zone_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zone
    ADD CONSTRAINT zone_code_key UNIQUE (code);


--
-- Name: zone_geographique zone_geographique_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zone_geographique
    ADD CONSTRAINT zone_geographique_pkey PRIMARY KEY (id);


--
-- Name: zone zone_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zone
    ADD CONSTRAINT zone_pkey PRIMARY KEY (id);


--
-- Name: idx_affectation_contribuable; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_affectation_contribuable ON public.affectation_taxe USING btree (contribuable_id);


--
-- Name: idx_affectation_taxe; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_affectation_taxe ON public.affectation_taxe USING btree (taxe_id);


--
-- Name: idx_collecte_collecteur; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collecte_collecteur ON public.info_collecte USING btree (collecteur_id);


--
-- Name: idx_collecte_contribuable; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collecte_contribuable ON public.info_collecte USING btree (contribuable_id);


--
-- Name: idx_collecte_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collecte_date ON public.info_collecte USING btree (date_collecte);


--
-- Name: idx_collecte_reference; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collecte_reference ON public.info_collecte USING btree (reference);


--
-- Name: idx_collecte_statut; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collecte_statut ON public.info_collecte USING btree (statut);


--
-- Name: idx_collecte_taxe; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collecte_taxe ON public.info_collecte USING btree (taxe_id);


--
-- Name: idx_collecteur_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collecteur_email ON public.collecteur USING btree (email);


--
-- Name: idx_collecteur_etat; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collecteur_etat ON public.collecteur USING btree (etat);


--
-- Name: idx_collecteur_matricule; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collecteur_matricule ON public.collecteur USING btree (matricule);


--
-- Name: idx_collecteur_statut; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collecteur_statut ON public.collecteur USING btree (statut);


--
-- Name: idx_collecteur_zone; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collecteur_zone ON public.collecteur USING btree (zone_id);


--
-- Name: idx_contribuable_collecteur; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_contribuable_collecteur ON public.contribuable USING btree (collecteur_id);


--
-- Name: idx_contribuable_numero_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_contribuable_numero_id ON public.contribuable USING btree (numero_identification);


--
-- Name: idx_contribuable_quartier; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_contribuable_quartier ON public.contribuable USING btree (quartier_id);


--
-- Name: idx_contribuable_telephone; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_contribuable_telephone ON public.contribuable USING btree (telephone);


--
-- Name: idx_contribuable_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_contribuable_type ON public.contribuable USING btree (type_contribuable_id);


--
-- Name: idx_taxe_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_taxe_code ON public.taxe USING btree (code);


--
-- Name: idx_taxe_service; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_taxe_service ON public.taxe USING btree (service_id);


--
-- Name: idx_taxe_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_taxe_type ON public.taxe USING btree (type_taxe_id);


--
-- Name: idx_utilisateur_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_utilisateur_email ON public.utilisateur USING btree (email);


--
-- Name: idx_utilisateur_role; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_utilisateur_role ON public.utilisateur USING btree (role);


--
-- Name: ix_arrondissement_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_arrondissement_id ON public.arrondissement USING btree (id);


--
-- Name: ix_commune_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_commune_id ON public.commune USING btree (id);


--
-- Name: ix_quartier_parametrage_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quartier_parametrage_id ON public.quartier_parametrage USING btree (id);


--
-- Name: ix_role_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_role_id ON public.role USING btree (id);


--
-- Name: ix_secteur_activite_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_secteur_activite_id ON public.secteur_activite USING btree (id);


--
-- Name: ix_ville_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ville_id ON public.ville USING btree (id);


--
-- Name: ix_zone_geographique_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_zone_geographique_code ON public.zone_geographique USING btree (code);


--
-- Name: ix_zone_geographique_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_zone_geographique_id ON public.zone_geographique USING btree (id);


--
-- Name: affectation_taxe update_affectation_taxe_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_affectation_taxe_updated_at BEFORE UPDATE ON public.affectation_taxe FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: collecteur update_collecteur_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_collecteur_updated_at BEFORE UPDATE ON public.collecteur FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: contribuable update_contribuable_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_contribuable_updated_at BEFORE UPDATE ON public.contribuable FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: info_collecte update_info_collecte_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_info_collecte_updated_at BEFORE UPDATE ON public.info_collecte FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: quartier update_quartier_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_quartier_updated_at BEFORE UPDATE ON public.quartier FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: service update_service_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_service_updated_at BEFORE UPDATE ON public.service FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: taxe update_taxe_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_taxe_updated_at BEFORE UPDATE ON public.taxe FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: type_contribuable update_type_contribuable_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_type_contribuable_updated_at BEFORE UPDATE ON public.type_contribuable FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: type_taxe update_type_taxe_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_type_taxe_updated_at BEFORE UPDATE ON public.type_taxe FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: utilisateur update_utilisateur_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_utilisateur_updated_at BEFORE UPDATE ON public.utilisateur FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: zone update_zone_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_zone_updated_at BEFORE UPDATE ON public.zone FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: affectation_taxe affectation_taxe_contribuable_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.affectation_taxe
    ADD CONSTRAINT affectation_taxe_contribuable_id_fkey FOREIGN KEY (contribuable_id) REFERENCES public.contribuable(id) ON DELETE CASCADE;


--
-- Name: affectation_taxe affectation_taxe_taxe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.affectation_taxe
    ADD CONSTRAINT affectation_taxe_taxe_id_fkey FOREIGN KEY (taxe_id) REFERENCES public.taxe(id) ON DELETE CASCADE;


--
-- Name: arrondissement arrondissement_commune_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.arrondissement
    ADD CONSTRAINT arrondissement_commune_id_fkey FOREIGN KEY (commune_id) REFERENCES public.commune(id);


--
-- Name: collecteur collecteur_zone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collecteur
    ADD CONSTRAINT collecteur_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES public.zone(id) ON DELETE SET NULL;


--
-- Name: commune commune_ville_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commune
    ADD CONSTRAINT commune_ville_id_fkey FOREIGN KEY (ville_id) REFERENCES public.ville(id);


--
-- Name: contribuable contribuable_collecteur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contribuable
    ADD CONSTRAINT contribuable_collecteur_id_fkey FOREIGN KEY (collecteur_id) REFERENCES public.collecteur(id) ON DELETE RESTRICT;


--
-- Name: contribuable contribuable_quartier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contribuable
    ADD CONSTRAINT contribuable_quartier_id_fkey FOREIGN KEY (quartier_id) REFERENCES public.quartier(id) ON DELETE RESTRICT;


--
-- Name: contribuable contribuable_type_contribuable_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contribuable
    ADD CONSTRAINT contribuable_type_contribuable_id_fkey FOREIGN KEY (type_contribuable_id) REFERENCES public.type_contribuable(id) ON DELETE RESTRICT;


--
-- Name: info_collecte info_collecte_collecteur_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.info_collecte
    ADD CONSTRAINT info_collecte_collecteur_id_fkey FOREIGN KEY (collecteur_id) REFERENCES public.collecteur(id) ON DELETE RESTRICT;


--
-- Name: info_collecte info_collecte_contribuable_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.info_collecte
    ADD CONSTRAINT info_collecte_contribuable_id_fkey FOREIGN KEY (contribuable_id) REFERENCES public.contribuable(id) ON DELETE RESTRICT;


--
-- Name: info_collecte info_collecte_taxe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.info_collecte
    ADD CONSTRAINT info_collecte_taxe_id_fkey FOREIGN KEY (taxe_id) REFERENCES public.taxe(id) ON DELETE RESTRICT;


--
-- Name: quartier_parametrage quartier_parametrage_arrondissement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quartier_parametrage
    ADD CONSTRAINT quartier_parametrage_arrondissement_id_fkey FOREIGN KEY (arrondissement_id) REFERENCES public.arrondissement(id);


--
-- Name: quartier_parametrage quartier_parametrage_zone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quartier_parametrage
    ADD CONSTRAINT quartier_parametrage_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES public.zone(id);


--
-- Name: quartier quartier_zone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quartier
    ADD CONSTRAINT quartier_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES public.zone(id) ON DELETE RESTRICT;


--
-- Name: taxe taxe_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxe
    ADD CONSTRAINT taxe_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.service(id) ON DELETE RESTRICT;


--
-- Name: taxe taxe_type_taxe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxe
    ADD CONSTRAINT taxe_type_taxe_id_fkey FOREIGN KEY (type_taxe_id) REFERENCES public.type_taxe(id) ON DELETE RESTRICT;


--
-- Name: zone_geographique zone_geographique_quartier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zone_geographique
    ADD CONSTRAINT zone_geographique_quartier_id_fkey FOREIGN KEY (quartier_id) REFERENCES public.quartier(id);


--
-- PostgreSQL database dump complete
--

