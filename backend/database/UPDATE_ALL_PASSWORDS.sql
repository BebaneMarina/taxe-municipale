-- =====================================================
-- Requêtes SQL pour mettre à jour tous les mots de passe
-- =====================================================

-- Hash pour "admin123"
UPDATE utilisateur 
SET mot_de_passe_hash = '$2b$12$V/uNhcyQKYI9NREdSPaRJ.t54PgS4uUIvwCEVS0uDXxkj9A7O/u9a'
WHERE email = 'admin@mairie-libreville.ga';

-- Hash pour "password123" (pour les autres utilisateurs)
UPDATE utilisateur 
SET mot_de_passe_hash = '$2b$12$EzmNLFv/pObUcST4WrLDTeff5edcwmbtgc8nzr1fLWJlpzM6nCHum'
WHERE email != 'admin@mairie-libreville.ga'
  AND mot_de_passe_hash IS NOT NULL;

-- Vérifier les mises à jour
SELECT 
    email, 
    role, 
    actif,
    CASE 
        WHEN mot_de_passe_hash IS NOT NULL THEN 'Hash présent'
        ELSE 'Pas de hash'
    END as hash_status
FROM utilisateur
ORDER BY email;

