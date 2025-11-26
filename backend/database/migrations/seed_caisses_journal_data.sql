-- Script SQL pour insérer des données de démonstration
-- Tables: caisse, operation_caisse, journal_travaux, commission_fichier, commission_journaliere
-- Usage: psql -d taxe_municipale -f database/migrations/seed_caisses_journal_data.sql

BEGIN;

-- ==================== CAISSES ====================
-- Créer des caisses pour les 5 premiers collecteurs actifs
DO $$
DECLARE
    collecteur_rec RECORD;
    caisse_count INTEGER := 0;
BEGIN
    FOR collecteur_rec IN 
        SELECT id, nom, prenom, matricule 
        FROM collecteur 
        WHERE actif = true 
        LIMIT 5
    LOOP
        -- Caisse physique
        INSERT INTO caisse (
            collecteur_id, type_caisse, code, nom, 
            solde_initial, solde_actuel, etat, 
            date_ouverture, notes, actif, created_at, updated_at
        )
        SELECT 
            collecteur_rec.id,
            'physique',
            'CAISSE-PHYS-' || collecteur_rec.matricule,
            'Caisse physique ' || collecteur_rec.nom,
            50000.00,
            CASE WHEN caisse_count % 2 = 0 THEN 75000.00 ELSE 45000.00 END,
            CASE WHEN caisse_count % 2 = 0 THEN 'ouverte' ELSE 'fermee' END,
            CASE WHEN caisse_count % 2 = 0 THEN NOW() - INTERVAL '2 hours' ELSE NULL END,
            'Caisse principale pour ' || collecteur_rec.nom || ' ' || collecteur_rec.prenom,
            true,
            NOW(),
            NOW()
        WHERE NOT EXISTS (
            SELECT 1 FROM caisse WHERE code = 'CAISSE-PHYS-' || collecteur_rec.matricule
        );
        
        -- Caisse en ligne
        INSERT INTO caisse (
            collecteur_id, type_caisse, code, nom,
            solde_initial, solde_actuel, etat,
            date_ouverture, notes, actif, created_at, updated_at
        )
        SELECT 
            collecteur_rec.id,
            'en_ligne',
            'CAISSE-ONLINE-' || collecteur_rec.matricule,
            'Caisse mobile ' || collecteur_rec.nom,
            0.00,
            CASE WHEN caisse_count % 2 = 0 THEN 25000.00 ELSE 15000.00 END,
            CASE WHEN caisse_count % 2 = 0 THEN 'ouverte' ELSE 'fermee' END,
            CASE WHEN caisse_count % 2 = 0 THEN NOW() - INTERVAL '1 hour' ELSE NULL END,
            'Caisse mobile money pour ' || collecteur_rec.nom,
            true,
            NOW(),
            NOW()
        WHERE NOT EXISTS (
            SELECT 1 FROM caisse WHERE code = 'CAISSE-ONLINE-' || collecteur_rec.matricule
        );
        
        caisse_count := caisse_count + 1;
    END LOOP;
    
    RAISE NOTICE '✅ Caisses créées';
END $$;

-- ==================== OPÉRATIONS DE CAISSE ====================
DO $$
DECLARE
    caisse_rec RECORD;
    collecteur_rec RECORD;
    op_count INTEGER;
    solde_actuel NUMERIC;
    montant_op NUMERIC;
    today TIMESTAMP;
BEGIN
    today := DATE_TRUNC('day', NOW()) + INTERVAL '8 hours';
    
    FOR caisse_rec IN 
        SELECT c.id, c.collecteur_id, c.code, c.solde_initial, c.etat
        FROM caisse c
        WHERE c.actif = true
    LOOP
        SELECT nom, prenom INTO collecteur_rec FROM collecteur WHERE id = caisse_rec.collecteur_id;
        
        solde_actuel := caisse_rec.solde_initial;
        
        -- Opération d'ouverture si caisse ouverte
        IF caisse_rec.etat = 'ouverte' THEN
            INSERT INTO operation_caisse (
                caisse_id, collecteur_id, type_operation, montant, libelle,
                solde_avant, solde_apres, date_operation, reference, created_at, updated_at
            )
            VALUES (
                caisse_rec.id,
                caisse_rec.collecteur_id,
                'ouverture',
                caisse_rec.solde_initial,
                'Ouverture de caisse - Solde initial',
                0.00,
                caisse_rec.solde_initial,
                today - INTERVAL '2 hours',
                'OP-' || caisse_rec.code || '-' || EXTRACT(EPOCH FROM NOW())::INTEGER,
                NOW(),
                NOW()
            )
            ON CONFLICT (reference) DO NOTHING;
        END IF;
        
        -- Opérations d'entrée (3 à 8 opérations)
        FOR op_count IN 1..(3 + floor(random() * 6)::INTEGER) LOOP
            montant_op := 5000 + floor(random() * 45000)::NUMERIC;
            solde_actuel := solde_actuel + montant_op;
            
            INSERT INTO operation_caisse (
                caisse_id, collecteur_id, type_operation, montant, libelle,
                solde_avant, solde_apres, date_operation, reference, created_at, updated_at
            )
            VALUES (
                caisse_rec.id,
                caisse_rec.collecteur_id,
                'entree',
                montant_op,
                'Collecte #' || op_count || ' - ' || collecteur_rec.nom,
                solde_actuel - montant_op,
                solde_actuel,
                today - INTERVAL '2 hours' + (op_count * INTERVAL '18 minutes'),
                'ENT-' || caisse_rec.code || '-' || op_count || '-' || EXTRACT(EPOCH FROM NOW())::INTEGER,
                NOW(),
                NOW()
            )
            ON CONFLICT (reference) DO NOTHING;
        END LOOP;
        
        -- Opération de sortie (50% de chance)
        IF random() > 0.5 THEN
            montant_op := 10000 + floor(random() * 20000)::NUMERIC;
            solde_actuel := solde_actuel - montant_op;
            
            INSERT INTO operation_caisse (
                caisse_id, collecteur_id, type_operation, montant, libelle,
                solde_avant, solde_apres, date_operation, reference, created_at, updated_at
            )
            VALUES (
                caisse_rec.id,
                caisse_rec.collecteur_id,
                'sortie',
                montant_op,
                'Remise en banque',
                solde_actuel + montant_op,
                solde_actuel,
                today - INTERVAL '30 minutes',
                'SORT-' || caisse_rec.code || '-' || EXTRACT(EPOCH FROM NOW())::INTEGER,
                NOW(),
                NOW()
            )
            ON CONFLICT (reference) DO NOTHING;
        END IF;
    END LOOP;
    
    RAISE NOTICE '✅ Opérations de caisse créées';
END $$;

-- ==================== JOURNAL TRAVAUX ====================
DO $$
DECLARE
    jour DATE;
    nb_collectes INTEGER;
    montant_collectes NUMERIC;
    nb_operations INTEGER;
    total_entrees NUMERIC;
    total_sorties NUMERIC;
    relances_envoyees INTEGER;
    impayes_regles INTEGER;
    statut_jour TEXT;
BEGIN
    FOR jour IN 
        SELECT generate_series(
            CURRENT_DATE - INTERVAL '6 days',
            CURRENT_DATE,
            INTERVAL '1 day'
        )::DATE
    LOOP
        -- Vérifier si journal existe déjà
        IF EXISTS (SELECT 1 FROM journal_travaux WHERE date_jour = jour) THEN
            CONTINUE;
        END IF;
        
        -- Compter collectes
        SELECT 
            COUNT(*),
            COALESCE(SUM(montant), 0)
        INTO nb_collectes, montant_collectes
        FROM info_collecte
        WHERE DATE(date_collecte) = jour
          AND statut = 'completed'
          AND annule = false;
        
        -- Compter opérations
        SELECT 
            COUNT(*),
            COALESCE(SUM(CASE WHEN type_operation IN ('entree', 'ouverture') THEN montant ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type_operation IN ('sortie', 'fermeture') THEN montant ELSE 0 END), 0)
        INTO nb_operations, total_entrees, total_sorties
        FROM operation_caisse
        WHERE DATE(date_operation) = jour;
        
        -- Simuler relances et impayés
        relances_envoyees := CASE WHEN jour < CURRENT_DATE THEN floor(random() * 16)::INTEGER ELSE 0 END;
        impayes_regles := CASE WHEN jour < CURRENT_DATE THEN floor(random() * 6)::INTEGER ELSE 0 END;
        
        statut_jour := CASE WHEN jour < CURRENT_DATE - INTERVAL '1 day' THEN 'cloture' ELSE 'en_cours' END;
        
        INSERT INTO journal_travaux (
            date_jour, statut, nb_collectes, montant_collectes,
            nb_operations_caisse, total_entrees_caisse, total_sorties_caisse,
            relances_envoyees, impayes_regles,
            remarque, created_at, updated_at,
            closed_at
        )
        VALUES (
            jour,
            statut_jour,
            nb_collectes,
            montant_collectes,
            nb_operations,
            total_entrees,
            total_sorties,
            relances_envoyees,
            impayes_regles,
            CASE WHEN jour < CURRENT_DATE THEN 'Journal automatique pour ' || jour::TEXT ELSE NULL END,
            NOW(),
            NOW(),
            CASE WHEN statut_jour = 'cloture' THEN NOW() - (CURRENT_DATE - jour) ELSE NULL END
        );
    END LOOP;
    
    RAISE NOTICE '✅ Journaux de travaux créés';
END $$;

-- ==================== COMMISSIONS ====================
DO $$
DECLARE
    jour DATE;
    collecteur_rec RECORD;
    fichier_id INTEGER;
    montant_collecte NUMERIC;
    commission_montant NUMERIC;
    commission_pourcentage NUMERIC := 5.00;
    total_collecteurs INTEGER;
    utilisateur_id INTEGER;
BEGIN
    -- Récupérer un utilisateur pour created_by
    SELECT id INTO utilisateur_id FROM utilisateur LIMIT 1;
    
    -- Créer des fichiers de commissions pour les 3 derniers jours
    FOR jour IN 
        SELECT generate_series(
            CURRENT_DATE - INTERVAL '3 days',
            CURRENT_DATE - INTERVAL '1 day',
            INTERVAL '1 day'
        )::DATE
    LOOP
        -- Vérifier si fichier existe déjà
        IF EXISTS (SELECT 1 FROM commission_fichier WHERE date_jour = jour) THEN
            CONTINUE;
        END IF;
        
        -- Compter les collecteurs actifs
        SELECT COUNT(*) INTO total_collecteurs FROM collecteur WHERE actif = true;
        
        -- Créer le fichier de commission
        INSERT INTO commission_fichier (
            date_jour, chemin, type_fichier, statut,
            created_by, file_metadata, created_at
        )
        VALUES (
            jour,
            'commissions/commission_' || jour::TEXT || '_demo.json',
            'json',
            CASE WHEN jour = CURRENT_DATE - INTERVAL '1 day' THEN 'en_attente' ELSE 'envoyee' END,
            utilisateur_id,
            jsonb_build_object(
                'total_collecteurs', total_collecteurs,
                'format', 'json',
                'montant_total_collecte', 0
            ),
            NOW()
        )
        RETURNING id INTO fichier_id;
        
        -- Créer les commissions journalières pour chaque collecteur
        FOR collecteur_rec IN 
            SELECT id, nom, prenom FROM collecteur WHERE actif = true LIMIT 5
        LOOP
            montant_collecte := 50000 + floor(random() * 450000)::NUMERIC;
            commission_montant := (montant_collecte * commission_pourcentage / 100);
            
            INSERT INTO commission_journaliere (
                date_jour, collecteur_id, montant_collecte,
                commission_montant, commission_pourcentage,
                statut_paiement, fichier_id, created_at
            )
            VALUES (
                jour,
                collecteur_rec.id,
                montant_collecte,
                commission_montant,
                commission_pourcentage,
                CASE WHEN jour = CURRENT_DATE - INTERVAL '1 day' THEN 'en_attente' ELSE 'payee' END,
                fichier_id,
                NOW()
            );
        END LOOP;
    END LOOP;
    
    RAISE NOTICE '✅ Fichiers de commissions créés';
END $$;

COMMIT;

-- Afficher un résumé
SELECT 
    'Caisses' as table_name,
    COUNT(*) as total
FROM caisse
UNION ALL
SELECT 
    'Opérations de caisse',
    COUNT(*)
FROM operation_caisse
UNION ALL
SELECT 
    'Journaux de travaux',
    COUNT(*)
FROM journal_travaux
UNION ALL
SELECT 
    'Fichiers de commissions',
    COUNT(*)
FROM commission_fichier
UNION ALL
SELECT 
    'Commissions journalières',
    COUNT(*)
FROM commission_journaliere;

