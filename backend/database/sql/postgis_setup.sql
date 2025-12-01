-- Initialisation PostGIS pour e_taxe

-- 1. Activer l'extension PostGIS (à exécuter une seule fois)
CREATE EXTENSION IF NOT EXISTS postgis;

-- 2. Ajouter les colonnes geometry
ALTER TABLE zone_geographique
    ADD COLUMN IF NOT EXISTS geom geometry(MultiPolygon, 4326);

ALTER TABLE contribuable
    ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326);

ALTER TABLE collecteur
    ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326);

ALTER TABLE quartier
    ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326);

-- 3. Synchroniser les anciennes données
-- Zones : convertir le GeoJSON stocké en JSON vers geometry
UPDATE zone_geographique
SET geom = ST_SetSRID(ST_GeomFromGeoJSON(geometry::text), 4326)
WHERE geometry IS NOT NULL;

-- Contribuables : créer un point à partir de longitude / latitude
UPDATE contribuable
SET geom = ST_SetSRID(ST_MakePoint(longitude::float, latitude::float), 4326)
WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

-- Collecteurs
UPDATE collecteur
SET geom = ST_SetSRID(ST_MakePoint(longitude::float, latitude::float), 4326)
WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

-- Quartiers : utiliser latitude/longitude si disponibles, sinon NULL
UPDATE quartier
SET geom = ST_SetSRID(ST_MakePoint(longitude::float, latitude::float), 4326)
WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

