DROP VIEW IF EXISTS cartographie_contribuable_view;

CREATE OR REPLACE VIEW cartographie_contribuable_view AS
WITH collectes_stats AS (
    SELECT
        ic.contribuable_id,
        COUNT(*) FILTER (WHERE ic.statut = 'completed' AND ic.annule = FALSE) AS nombre_collectes,
        COALESCE(SUM(CASE WHEN ic.statut = 'completed' AND ic.annule = FALSE THEN ic.montant ELSE 0 END), 0)::numeric(12,2) AS total_collecte,
        MAX(CASE WHEN ic.statut = 'completed' AND ic.annule = FALSE THEN ic.date_collecte END) AS derniere_collecte,
        BOOL_OR(
            ic.statut = 'completed'
            AND ic.annule = FALSE
            AND ic.date_collecte >= date_trunc('month', now())
        ) AS a_paye
    FROM info_collecte ic
    GROUP BY ic.contribuable_id
),
taxes_impayees AS (
    SELECT
        at.contribuable_id,
        json_agg(DISTINCT t.nom) AS taxes
    FROM affectation_taxe at
    JOIN taxe t ON t.id = at.taxe_id
    WHERE at.actif = TRUE
    GROUP BY at.contribuable_id
)
SELECT
    c.id,
    c.nom,
    c.prenom,
    c.nom_activite,
    c.telephone,
    c.adresse,
    c.latitude::float AS latitude,
    c.longitude::float AS longitude,
    c.photo_url,
    c.actif,
    tc.nom AS type_contribuable,
    q.nom AS quartier,
    z.nom AS zone,
    CONCAT(cl.nom, ' ', COALESCE(cl.prenom, '')) AS collecteur,
    COALESCE(cs.a_paye, FALSE) AS a_paye,
    COALESCE(cs.total_collecte, 0)::numeric(12,2) AS total_collecte,
    COALESCE(cs.nombre_collectes, 0) AS nombre_collectes,
    cs.derniere_collecte,
    COALESCE(ti.taxes, '[]'::json) AS taxes_impayees
FROM contribuable c
LEFT JOIN collectes_stats cs ON cs.contribuable_id = c.id
LEFT JOIN taxes_impayees ti ON ti.contribuable_id = c.id
LEFT JOIN quartier q ON q.id = c.quartier_id
LEFT JOIN zone z ON z.id = q.zone_id
LEFT JOIN type_contribuable tc ON tc.id = c.type_contribuable_id
LEFT JOIN collecteur cl ON cl.id = c.collecteur_id
WHERE c.latitude IS NOT NULL AND c.longitude IS NOT NULL;

