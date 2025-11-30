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
-- Name: cartographie_contribuable_view; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.cartographie_contribuable_view AS
 WITH collectes_stats AS (
         SELECT ic.contribuable_id,
            count(*) FILTER (WHERE ((ic.statut = 'completed'::public.statut_collecte_enum) AND (ic.annule = false))) AS nombre_collectes,
            (COALESCE(sum(
                CASE
                    WHEN ((ic.statut = 'completed'::public.statut_collecte_enum) AND (ic.annule = false)) THEN ic.montant
                    ELSE (0)::numeric
                END), (0)::numeric))::numeric(12,2) AS total_collecte,
            max(
                CASE
                    WHEN ((ic.statut = 'completed'::public.statut_collecte_enum) AND (ic.annule = false)) THEN ic.date_collecte
                    ELSE NULL::timestamp without time zone
                END) AS derniere_collecte,
            bool_or(((ic.statut = 'completed'::public.statut_collecte_enum) AND (ic.annule = false) AND (ic.date_collecte >= date_trunc('month'::text, now())))) AS a_paye
           FROM public.info_collecte ic
          GROUP BY ic.contribuable_id
        ), taxes_impayees AS (
         SELECT at.contribuable_id,
            json_agg(DISTINCT t.nom) AS taxes
           FROM (public.affectation_taxe at
             JOIN public.taxe t ON ((t.id = at.taxe_id)))
          WHERE (at.actif = true)
          GROUP BY at.contribuable_id
        ), base_contribuables AS (
         SELECT c.id,
            c.nom,
            c.prenom,
            c.nom_activite,
            c.telephone,
            c.adresse,
                CASE
                    WHEN (((c.latitude >= ('-5'::integer)::numeric) AND (c.latitude <= (5)::numeric)) AND ((c.longitude >= (6)::numeric) AND (c.longitude <= (16)::numeric))) THEN (c.latitude)::double precision
                    WHEN (q.geom IS NOT NULL) THEN public.st_y(q.geom)
                    ELSE NULL::double precision
                END AS latitude,
                CASE
                    WHEN (((c.latitude >= ('-5'::integer)::numeric) AND (c.latitude <= (5)::numeric)) AND ((c.longitude >= (6)::numeric) AND (c.longitude <= (16)::numeric))) THEN (c.longitude)::double precision
                    WHEN (q.geom IS NOT NULL) THEN public.st_x(q.geom)
                    ELSE NULL::double precision
                END AS longitude,
            c.photo_url,
            c.actif,
            tc.nom AS type_contribuable,
            q.nom AS quartier,
            z.nom AS zone,
            concat(cl.nom, ' ', COALESCE(cl.prenom, ''::character varying)) AS collecteur
           FROM ((((public.contribuable c
             LEFT JOIN public.quartier q ON ((q.id = c.quartier_id)))
             LEFT JOIN public.zone z ON ((z.id = q.zone_id)))
             LEFT JOIN public.type_contribuable tc ON ((tc.id = c.type_contribuable_id)))
             LEFT JOIN public.collecteur cl ON ((cl.id = c.collecteur_id)))
        )
 SELECT bc.id,
    bc.nom,
    bc.prenom,
    bc.nom_activite,
    bc.telephone,
    bc.adresse,
    bc.latitude,
    bc.longitude,
    bc.photo_url,
    bc.actif,
    bc.type_contribuable,
    bc.quartier,
    bc.zone,
    bc.collecteur,
    COALESCE(cs.a_paye, false) AS a_paye,
    (COALESCE(cs.total_collecte, (0)::numeric))::numeric(12,2) AS total_collecte,
    COALESCE(cs.nombre_collectes, (0)::bigint) AS nombre_collectes,
    cs.derniere_collecte,
    COALESCE(ti.taxes, '[]'::json) AS taxes_impayees
   FROM ((base_contribuables bc
     LEFT JOIN collectes_stats cs ON ((cs.contribuable_id = bc.id)))
     LEFT JOIN taxes_impayees ti ON ((ti.contribuable_id = bc.id)))
  WHERE ((bc.latitude IS NOT NULL) AND (bc.longitude IS NOT NULL));


ALTER VIEW public.cartographie_contribuable_view OWNER TO postgres;

--
-- PostgreSQL database dump complete
--

