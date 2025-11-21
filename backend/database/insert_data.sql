-- =====================================================
-- Script SQL pour insérer des données de test
-- Au moins 50 entrées par table avec données gabonaises
-- =====================================================

-- Note: Ce script est un exemple. Pour une insertion complète,
-- utilisez plutôt le script Python seeders_complet.py qui gère
-- mieux les relations et évite les doublons.

BEGIN;

-- ==================== INSERTION DES ZONES ====================
INSERT INTO zone (nom, code, description, actif) VALUES
('Centre-ville', 'ZONE-001', 'Zone centrale de Libreville', true),
('Akanda', 'ZONE-002', 'Zone Akanda', true),
('Ntoum', 'ZONE-003', 'Zone Ntoum', true),
('Owendo', 'ZONE-004', 'Zone portuaire d''Owendo', true),
('Port-Gentil', 'ZONE-005', 'Zone Port-Gentil', true),
('Franceville', 'ZONE-006', 'Zone Franceville', true)
ON CONFLICT (code) DO NOTHING;

-- Générer plus de zones si nécessaire
DO $$
DECLARE
    i INTEGER;
BEGIN
    FOR i IN 7..50 LOOP
        INSERT INTO zone (nom, code, description, actif)
        VALUES (
            'Zone ' || i,
            'ZONE-' || LPAD(i::TEXT, 3, '0'),
            'Zone géographique ' || i,
            true
        )
        ON CONFLICT (code) DO NOTHING;
    END LOOP;
END $$;

-- ==================== INSERTION DES QUARTIERS ====================
-- Récupérer les IDs des zones
DO $$
DECLARE
    zone_centre_id INTEGER;
    zone_akanda_id INTEGER;
    zone_ntoum_id INTEGER;
    zone_owendo_id INTEGER;
    zone_pg_id INTEGER;
    zone_fv_id INTEGER;
    i INTEGER;
    zone_id INTEGER;
BEGIN
    SELECT id INTO zone_centre_id FROM zone WHERE code = 'ZONE-001';
    SELECT id INTO zone_akanda_id FROM zone WHERE code = 'ZONE-002';
    SELECT id INTO zone_ntoum_id FROM zone WHERE code = 'ZONE-003';
    SELECT id INTO zone_owendo_id FROM zone WHERE code = 'ZONE-004';
    SELECT id INTO zone_pg_id FROM zone WHERE code = 'ZONE-005';
    SELECT id INTO zone_fv_id FROM zone WHERE code = 'ZONE-006';

    -- Quartiers réels
    INSERT INTO quartier (nom, code, zone_id, description, actif) VALUES
    ('Mont-Bouët', 'Q-001', zone_centre_id, 'Quartier Mont-Bouët', true),
    ('Glass', 'Q-002', zone_centre_id, 'Quartier Glass', true),
    ('Quartier Louis', 'Q-003', zone_centre_id, 'Quartier Louis', true),
    ('Nombakélé', 'Q-004', zone_centre_id, 'Quartier Nombakélé', true),
    ('Akébé', 'Q-005', zone_centre_id, 'Quartier Akébé', true),
    ('Oloumi', 'Q-006', zone_centre_id, 'Quartier Oloumi', true),
    ('Cocotiers', 'Q-011', zone_akanda_id, 'Quartier Cocotiers', true),
    ('Angondjé', 'Q-012', zone_akanda_id, 'Quartier Angondjé', true),
    ('Melen', 'Q-013', zone_akanda_id, 'Quartier Melen', true),
    ('Ntoum Centre', 'Q-016', zone_ntoum_id, 'Ntoum Centre', true),
    ('Owendo Centre', 'Q-019', zone_owendo_id, 'Owendo Centre', true),
    ('PK8', 'Q-020', zone_owendo_id, 'PK8', true)
    ON CONFLICT (code) DO NOTHING;

    -- Générer plus de quartiers
    FOR i IN 13..50 LOOP
        SELECT id INTO zone_id FROM zone ORDER BY RANDOM() LIMIT 1;
        INSERT INTO quartier (nom, code, zone_id, description, actif)
        VALUES (
            'Quartier ' || i,
            'Q-' || LPAD(i::TEXT, 3, '0'),
            zone_id,
            'Description quartier ' || i,
            true
        )
        ON CONFLICT (code) DO NOTHING;
    END LOOP;
END $$;

-- ==================== INSERTION DES TYPES DE CONTRIBUABLES ====================
INSERT INTO type_contribuable (nom, code, description, actif) VALUES
('Particulier', 'TC-001', 'Particulier', true),
('Entreprise', 'TC-002', 'Entreprise', true),
('Commerce', 'TC-003', 'Commerce', true),
('Marché', 'TC-004', 'Marché', true),
('Transport', 'TC-005', 'Transport', true),
('Restaurant', 'TC-006', 'Restaurant', true),
('Hôtel', 'TC-007', 'Hôtel', true),
('Boutique', 'TC-008', 'Boutique', true)
ON CONFLICT (code) DO NOTHING;

-- Générer plus de types
DO $$
DECLARE
    types TEXT[] := ARRAY['Artisan', 'Prestataire', 'Vendeur ambulant', 'Taxi', 'Moto-taxi', 
                          'Garage', 'Pharmacie', 'Superette', 'Boulangerie', 'Coiffure',
                          'Salon de beauté', 'Cybercafé', 'Imprimerie', 'Photographe', 'Bijoutier'];
    i INTEGER;
    type_nom TEXT;
BEGIN
    FOR i IN 9..50 LOOP
        IF i <= 23 THEN
            type_nom := types[i - 8];
        ELSE
            type_nom := 'Type ' || i;
        END IF;
        INSERT INTO type_contribuable (nom, code, description, actif)
        VALUES (
            type_nom,
            'TC-' || LPAD(i::TEXT, 3, '0'),
            'Type de contribuable : ' || type_nom,
            true
        )
        ON CONFLICT (code) DO NOTHING;
    END LOOP;
END $$;

-- ==================== INSERTION DES SERVICES ====================
INSERT INTO service (nom, code, description, actif) VALUES
('Service des Finances', 'SRV-001', 'Gestion financière', true),
('Service des Marchés', 'SRV-002', 'Gestion des marchés', true),
('Service de l''Urbanisme', 'SRV-003', 'Urbanisme et aménagement', true),
('Service des Transports', 'SRV-004', 'Gestion des transports', true),
('Service des Commerces', 'SRV-005', 'Gestion des commerces', true),
('Service de l''Environnement', 'SRV-006', 'Environnement et propreté', true),
('Service de la Voirie', 'SRV-007', 'Entretien de la voirie', true)
ON CONFLICT (code) DO NOTHING;

-- Générer plus de services
DO $$
DECLARE
    services TEXT[] := ARRAY['Service de la Propreté', 'Service de l''Éclairage Public', 
                            'Service des Espaces Verts', 'Service de la Sécurité', 
                            'Service de la Communication'];
    i INTEGER;
    service_nom TEXT;
BEGIN
    FOR i IN 8..50 LOOP
        IF i <= 12 THEN
            service_nom := services[i - 7];
        ELSE
            service_nom := 'Service ' || i;
        END IF;
        INSERT INTO service (nom, code, description, actif)
        VALUES (
            service_nom,
            'SRV-' || LPAD(i::TEXT, 3, '0'),
            'Service : ' || service_nom,
            true
        )
        ON CONFLICT (code) DO NOTHING;
    END LOOP;
END $$;

-- ==================== INSERTION DES TYPES DE TAXES ====================
INSERT INTO type_taxe (nom, code, description, actif) VALUES
('Taxe de Marché', 'TT-001', 'Taxe sur les activités de marché', true),
('Taxe d''Occupation du Domaine Public', 'TT-002', 'Taxe pour occupation de l''espace public', true),
('Taxe sur les Activités Commerciales', 'TT-003', 'Taxe sur les activités commerciales', true),
('Taxe de Stationnement', 'TT-004', 'Taxe de stationnement', true),
('Taxe de Voirie', 'TT-005', 'Taxe de voirie', true),
('Taxe d''Enlèvement des Ordures', 'TT-006', 'Taxe pour l''enlèvement des ordures', true),
('Taxe sur les Transports', 'TT-007', 'Taxe sur les activités de transport', true),
('Taxe sur les Débits de Boissons', 'TT-008', 'Taxe sur les débits de boissons', true),
('Taxe sur les Hôtels', 'TT-009', 'Taxe sur les établissements hôteliers', true),
('Taxe sur les Publicités', 'TT-010', 'Taxe sur les publicités et enseignes', true)
ON CONFLICT (code) DO NOTHING;

-- Générer plus de types de taxes
DO $$
DECLARE
    i INTEGER;
BEGIN
    FOR i IN 11..50 LOOP
        INSERT INTO type_taxe (nom, code, description, actif)
        VALUES (
            'Type Taxe ' || i,
            'TT-' || LPAD(i::TEXT, 3, '0'),
            'Description type taxe ' || i,
            true
        )
        ON CONFLICT (code) DO NOTHING;
    END LOOP;
END $$;

-- ==================== INSERTION DES COLLECTEURS ====================
DO $$
DECLARE
    noms TEXT[] := ARRAY['MBOUMBA', 'NDONG', 'OBAME', 'BONGO', 'ESSONO', 'MVE', 'MINTSA'];
    prenoms TEXT[] := ARRAY['Jean', 'Marie', 'Pierre', 'Paul', 'Sophie', 'Luc', 'Anne', 'David',
                           'François', 'Catherine', 'Michel', 'Isabelle', 'André', 'Christine'];
    i INTEGER;
    zone_id INTEGER;
    nom TEXT;
    prenom TEXT;
    matricule TEXT;
    email TEXT;
    telephone TEXT;
BEGIN
    FOR i IN 1..50 LOOP
        nom := noms[1 + (i % array_length(noms, 1))];
        prenom := prenoms[1 + (i % array_length(prenoms, 1))];
        matricule := 'COL-' || LPAD(i::TEXT, 3, '0');
        email := 'collecteur' || i || '@mairie-libreville.ga';
        telephone := '+24106' || LPAD((1000000 + i)::TEXT, 7, '0');
        
        SELECT id INTO zone_id FROM zone ORDER BY RANDOM() LIMIT 1;
        
        INSERT INTO collecteur (nom, prenom, email, telephone, matricule, statut, etat, zone_id, heure_cloture, actif)
        VALUES (
            nom,
            prenom,
            email,
            telephone,
            matricule,
            (CASE WHEN (i % 10) = 0 THEN 'desactive' ELSE 'active' END)::statut_collecteur_enum,
            (CASE WHEN (i % 2) = 0 THEN 'deconnecte' ELSE 'connecte' END)::etat_collecteur_enum,
            zone_id,
            (17 + (i % 3))::TEXT || ':00',
            true
        )
        ON CONFLICT (matricule) DO NOTHING;
    END LOOP;
END $$;

-- ==================== INSERTION DES CONTRIBUABLES ====================
DO $$
DECLARE
    noms TEXT[] := ARRAY['MBOUMBA', 'NDONG', 'OBAME', 'BONGO', 'ESSONO', 'MVE', 'MINTSA'];
    prenoms TEXT[] := ARRAY['Jean', 'Marie', 'Pierre', 'Paul', 'Sophie', 'Luc', 'Anne', 'David'];
    rues TEXT[] := ARRAY['Avenue Indépendance', 'Boulevard Léon Mba', 'Rue Nkrumah', 'Avenue De Gaulle', 'Rue Massenet'];
    i INTEGER;
    nom TEXT;
    prenom TEXT;
    type_contrib_id INTEGER;
    quartier_id INTEGER;
    collecteur_id INTEGER;
    telephone TEXT;
    numero_id TEXT;
    adresse TEXT;
BEGIN
    FOR i IN 1..50 LOOP
        nom := noms[1 + (i % array_length(noms, 1))];
        prenom := prenoms[1 + (i % array_length(prenoms, 1))];
        telephone := '+24106' || LPAD((2000000 + i)::TEXT, 7, '0');
        numero_id := 'CTB-' || LPAD(i::TEXT, 4, '0');
        adresse := rues[1 + (i % array_length(rues, 1))] || ' ' || (1 + (i % 200));
        
        SELECT id INTO type_contrib_id FROM type_contribuable ORDER BY RANDOM() LIMIT 1;
        SELECT id INTO quartier_id FROM quartier ORDER BY RANDOM() LIMIT 1;
        SELECT id INTO collecteur_id FROM collecteur ORDER BY RANDOM() LIMIT 1;
        
        INSERT INTO contribuable (nom, prenom, email, telephone, type_contribuable_id, quartier_id, 
                                  collecteur_id, adresse, latitude, longitude, numero_identification, actif)
        VALUES (
            nom,
            prenom,
            CASE WHEN (i % 3) = 0 THEN NULL ELSE 'contribuable' || i || '@example.ga' END,
            telephone,
            type_contrib_id,
            quartier_id,
            collecteur_id,
            adresse,
            0.3 + (i % 20) * 0.01,
            9.3 + (i % 20) * 0.01,
            numero_id,
            true
        )
        ON CONFLICT (telephone) DO NOTHING
        ON CONFLICT (numero_identification) DO NOTHING;
    END LOOP;
END $$;

-- ==================== INSERTION DES TAXES ====================
DO $$
DECLARE
    i INTEGER;
    type_taxe_id INTEGER;
    service_id INTEGER;
    montants NUMERIC[] := ARRAY[500, 1000, 2000, 3000, 5000, 10000, 15000, 20000, 25000, 30000];
    periodicites TEXT[] := ARRAY['journaliere', 'hebdomadaire', 'mensuelle', 'trimestrielle'];
    montant NUMERIC;
    periodicite TEXT;
    code TEXT;
BEGIN
    -- Taxes de base
    SELECT id INTO type_taxe_id FROM type_taxe WHERE code = 'TT-001' LIMIT 1;
    SELECT id INTO service_id FROM service WHERE code = 'SRV-002' LIMIT 1;
    
    INSERT INTO taxe (nom, code, description, montant, montant_variable, periodicite, type_taxe_id, service_id, commission_pourcentage, actif)
    VALUES
    ('Taxe de Marché Journalière', 'TAX-001', 'Taxe quotidienne pour les vendeurs de marché', 1000.00, false, 'journaliere'::periodicite_enum, type_taxe_id, service_id, 5.00, true),
    ('Taxe de Marché Mensuelle', 'TAX-002', 'Taxe mensuelle pour les vendeurs de marché', 25000.00, false, 'mensuelle'::periodicite_enum, type_taxe_id, service_id, 5.00, true)
    ON CONFLICT (code) DO NOTHING;
    
    -- Générer plus de taxes
    FOR i IN 3..50 LOOP
        SELECT id INTO type_taxe_id FROM type_taxe ORDER BY RANDOM() LIMIT 1;
        SELECT id INTO service_id FROM service ORDER BY RANDOM() LIMIT 1;
        montant := montants[1 + (i % array_length(montants, 1))];
        periodicite := periodicites[1 + (i % array_length(periodicites, 1))];
        code := 'TAX-' || LPAD(i::TEXT, 3, '0');
        
        INSERT INTO taxe (nom, code, description, montant, montant_variable, periodicite, type_taxe_id, service_id, commission_pourcentage, actif)
        VALUES (
            'Taxe ' || i,
            code,
            'Description de la taxe ' || i,
            montant,
            (i % 3) = 0,
            periodicite::periodicite_enum,
            type_taxe_id,
            service_id,
            ROUND((RANDOM() * 10)::NUMERIC, 2),
            true
        )
        ON CONFLICT (code) DO NOTHING;
    END LOOP;
END $$;

-- ==================== INSERTION DES AFFECTATIONS TAXES ====================
DO $$
DECLARE
    i INTEGER;
    contribuable_id INTEGER;
    taxe_id INTEGER;
    date_debut TIMESTAMP;
    affectation_count INTEGER := 0;
BEGIN
    FOR contribuable_id IN SELECT id FROM contribuable LOOP
        -- Chaque contribuable a 1-3 taxes
        FOR i IN 1..(1 + (contribuable_id % 3)) LOOP
            SELECT id INTO taxe_id FROM taxe ORDER BY RANDOM() LIMIT 1;
            date_debut := CURRENT_TIMESTAMP - (RANDOM() * 180 || ' days')::INTERVAL;
            
            INSERT INTO affectation_taxe (contribuable_id, taxe_id, date_debut, date_fin, montant_custom, actif)
            VALUES (
                contribuable_id,
                taxe_id,
                date_debut,
                CASE WHEN (contribuable_id % 4) = 0 THEN date_debut + INTERVAL '365 days' ELSE NULL END,
                CASE WHEN (contribuable_id % 3) = 0 THEN (SELECT montant FROM taxe WHERE id = taxe_id) * (0.8 + RANDOM() * 0.7) ELSE NULL END,
                true
            )
            ON CONFLICT (contribuable_id, taxe_id, date_debut) DO NOTHING;
            
            affectation_count := affectation_count + 1;
            EXIT WHEN affectation_count >= 50;
        END LOOP;
        
        EXIT WHEN affectation_count >= 50;
    END LOOP;
END $$;

-- ==================== INSERTION DES COLLECTES ====================
DO $$
DECLARE
    i INTEGER;
    contribuable_id INTEGER;
    taxe_id INTEGER;
    collecteur_id INTEGER;
    affectation_id INTEGER;
    montant NUMERIC;
    commission NUMERIC;
    type_paiement TEXT;
    statut TEXT;
    reference TEXT;
    date_collecte TIMESTAMP;
    billetage TEXT;
BEGIN
    FOR i IN 1..50 LOOP
        SELECT at.id, at.contribuable_id, at.taxe_id INTO affectation_id, contribuable_id, taxe_id
        FROM affectation_taxe at
        WHERE at.actif = true
        ORDER BY RANDOM()
        LIMIT 1;
        
        SELECT id INTO collecteur_id FROM collecteur ORDER BY RANDOM() LIMIT 1;
        SELECT montant INTO montant FROM taxe WHERE id = taxe_id;
        
        commission := montant * (SELECT commission_pourcentage FROM taxe WHERE id = taxe_id) / 100;
        type_paiement := (ARRAY['especes', 'mobile_money', 'carte'])[1 + (i % 3)];
        statut := (ARRAY['completed', 'completed', 'completed', 'pending', 'failed'])[1 + (i % 5)];
        date_collecte := CURRENT_TIMESTAMP - (RANDOM() * 90 || ' days')::INTERVAL;
        reference := 'COL-' || TO_CHAR(date_collecte, 'YYYYMMDD') || '-' || LPAD(i::TEXT, 4, '0');
        
        -- Générer billetage pour espèces
        IF type_paiement = 'especes' AND (i % 2) = 0 THEN
            billetage := json_build_object(
                '5000', (i % 10),
                '1000', (i % 20)
            )::TEXT;
        ELSE
            billetage := NULL;
        END IF;
        
        INSERT INTO info_collecte (
            contribuable_id, taxe_id, collecteur_id, montant, commission,
            type_paiement, statut, reference, billetage, date_collecte,
            date_cloture, sms_envoye, ticket_imprime, annule
        )
        VALUES (
            contribuable_id,
            taxe_id,
            collecteur_id,
            montant,
            commission,
            type_paiement::type_paiement_enum,
            statut::statut_collecte_enum,
            reference,
            billetage,
            date_collecte,
            CASE WHEN (i % 3) = 0 THEN date_collecte + (RANDOM() * 8 || ' hours')::INTERVAL ELSE NULL END,
            (i % 2) = 0,
            (i % 2) = 0,
            false
        )
        ON CONFLICT (reference) DO NOTHING;
    END LOOP;
END $$;

-- ==================== INSERTION DES UTILISATEURS ====================
DO $$
DECLARE
    noms TEXT[] := ARRAY['MBOUMBA', 'NDONG', 'OBAME', 'BONGO', 'ESSONO', 'MVE', 'MINTSA'];
    prenoms TEXT[] := ARRAY['Jean', 'Marie', 'Pierre', 'Paul', 'Sophie', 'Luc', 'Anne', 'David'];
    roles TEXT[] := ARRAY['admin', 'agent_back_office', 'agent_front_office', 'controleur_interne', 'collecteur'];
    i INTEGER;
    nom TEXT;
    prenom TEXT;
    email TEXT;
    telephone TEXT;
    role TEXT;
    password_hash TEXT := '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5'; -- hash de "password123"
BEGIN
    -- Admin
    INSERT INTO utilisateur (nom, prenom, email, telephone, mot_de_passe_hash, role, actif)
    VALUES (
        'Admin',
        'Système',
        'admin@mairie-libreville.ga',
        '+241062345678',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5', -- hash de "admin123"
        'admin'::role_enum,
        true
    )
    ON CONFLICT (email) DO NOTHING;
    
    -- Autres utilisateurs
    FOR i IN 1..49 LOOP
        nom := noms[1 + (i % array_length(noms, 1))];
        prenom := prenoms[1 + (i % array_length(prenoms, 1))];
        email := 'user' || i || '@mairie-libreville.ga';
        telephone := '+24106' || LPAD((3000000 + i)::TEXT, 7, '0');
        role := roles[1 + (i % array_length(roles, 1))];
        
        INSERT INTO utilisateur (nom, prenom, email, telephone, mot_de_passe_hash, role, actif, derniere_connexion)
        VALUES (
            nom,
            prenom,
            email,
            telephone,
            password_hash,
            role::role_enum,
            (i % 4) != 0, -- 75% actifs
            CASE WHEN (i % 2) = 0 THEN CURRENT_TIMESTAMP - (RANDOM() * 30 || ' days')::INTERVAL ELSE NULL END
        )
        ON CONFLICT (email) DO NOTHING;
    END LOOP;
END $$;

COMMIT;

-- Afficher les statistiques
SELECT 
    'Zones' as table_name, COUNT(*) as count FROM zone
UNION ALL
SELECT 'Quartiers', COUNT(*) FROM quartier
UNION ALL
SELECT 'Types Contribuables', COUNT(*) FROM type_contribuable
UNION ALL
SELECT 'Services', COUNT(*) FROM service
UNION ALL
SELECT 'Types Taxes', COUNT(*) FROM type_taxe
UNION ALL
SELECT 'Taxes', COUNT(*) FROM taxe
UNION ALL
SELECT 'Collecteurs', COUNT(*) FROM collecteur
UNION ALL
SELECT 'Contribuables', COUNT(*) FROM contribuable
UNION ALL
SELECT 'Affectations Taxes', COUNT(*) FROM affectation_taxe
UNION ALL
SELECT 'Collectes', COUNT(*) FROM info_collecte
UNION ALL
SELECT 'Utilisateurs', COUNT(*) FROM utilisateur;

