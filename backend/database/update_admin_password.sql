-- =====================================================
-- Requête SQL pour mettre à jour le mot de passe admin
-- =====================================================

-- Mettre à jour le hash de mot de passe pour l'utilisateur admin
-- Mot de passe: admin123
UPDATE utilisateur 
SET mot_de_passe_hash = '$2b$12$V/uNhcyQKYI9NREdSPaRJ.t54PgS4uUIvwCEVS0uDXxkj9A7O/u9a'
WHERE email = 'admin@mairie-libreville.ga';

-- Vérifier la mise à jour
SELECT email, role, actif, 
       CASE 
           WHEN mot_de_passe_hash IS NOT NULL THEN 'Hash présent'
           ELSE 'Pas de hash'
       END as hash_status
FROM utilisateur 
WHERE email = 'admin@mairie-libreville.ga';

