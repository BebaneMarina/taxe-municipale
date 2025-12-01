-- Mettre à jour la colonne geom des contribuables à partir de latitude/longitude
UPDATE contribuable
SET geom = ST_SetSRID(ST_MakePoint(longitude::float, latitude::float), 4326)
WHERE latitude IS NOT NULL 
  AND longitude IS NOT NULL 
  AND geom IS NULL
  AND latitude BETWEEN -5 AND 5
  AND longitude BETWEEN 6 AND 16;

-- Afficher le nombre de contribuables mis à jour
SELECT COUNT(*) AS contribuables_mis_a_jour
FROM contribuable
WHERE geom IS NOT NULL;

