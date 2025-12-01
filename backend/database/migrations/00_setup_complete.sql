-- ============================================================
-- SCRIPT DE MIGRATION COMPLET - ORDRE D'EXÉCUTION
-- ============================================================
-- Ce script doit être exécuté EN PREMIER pour initialiser
-- la base de données avec PostGIS et toutes les colonnes nécessaires
-- ============================================================

BEGIN;

-- 1. Activer PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

-- 2. Ajouter les colonnes geometry à toutes les tables nécessaires
ALTER TABLE zone_geographique
    ADD COLUMN IF NOT EXISTS geom geometry(MultiPolygon, 4326);

ALTER TABLE contribuable
    ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326);

ALTER TABLE collecteur
    ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326);

ALTER TABLE quartier
    ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326);

-- 3. Synchroniser les données existantes
-- Zones : convertir le GeoJSON stocké en JSON vers geometry
UPDATE zone_geographique
SET geom = ST_SetSRID(ST_GeomFromGeoJSON(geometry::text), 4326)
WHERE geometry IS NOT NULL AND geom IS NULL;

-- Contribuables : créer un point à partir de longitude / latitude
UPDATE contribuable
SET geom = ST_SetSRID(ST_MakePoint(longitude::float, latitude::float), 4326)
WHERE latitude IS NOT NULL AND longitude IS NOT NULL AND geom IS NULL;

-- Collecteurs
UPDATE collecteur
SET geom = ST_SetSRID(ST_MakePoint(longitude::float, latitude::float), 4326)
WHERE latitude IS NOT NULL AND longitude IS NOT NULL AND geom IS NULL;

-- Quartiers : utiliser latitude/longitude si disponibles (mais la table n'a pas ces colonnes)
-- Cette partie sera gérée par le script generate_fake_coordinates.py

COMMIT;

-- ============================================================
-- ORDRE D'EXÉCUTION RECOMMANDÉ :
-- ============================================================
-- 1. psql -U postgres -d taxe_municipale -f database/migrations/00_setup_complete.sql
-- 2. psql -U postgres -d taxe_municipale -f database/migrations/create_view_cartographie_contribuable.sql
-- 3. python scripts/generate_fake_coordinates.py (pour générer les geom des quartiers)
-- ============================================================

