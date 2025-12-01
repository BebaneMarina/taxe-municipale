-- Migration pour créer la table parametrage_notification
-- Table de paramétrage des notifications du système

-- Créer la table parametrage_notification
CREATE TABLE IF NOT EXISTS parametrage_notification (
    id SERIAL PRIMARY KEY,
    type_notification VARCHAR(100) NOT NULL UNIQUE,
    nom VARCHAR(255) NOT NULL,
    description TEXT,
    actif BOOLEAN DEFAULT TRUE,
    envoyer_email BOOLEAN DEFAULT FALSE,
    envoyer_sms BOOLEAN DEFAULT FALSE,
    envoyer_push BOOLEAN DEFAULT TRUE,
    template_email TEXT,
    template_sms TEXT,
    template_push TEXT,
    roles_cibles TEXT,  -- JSON string des rôles cibles
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Créer les index
CREATE INDEX IF NOT EXISTS idx_parametrage_notification_type ON parametrage_notification(type_notification);
CREATE INDEX IF NOT EXISTS idx_parametrage_notification_actif ON parametrage_notification(actif);

-- Créer le trigger pour mettre à jour updated_at automatiquement
DROP TRIGGER IF EXISTS update_parametrage_notification_updated_at ON parametrage_notification;
CREATE TRIGGER update_parametrage_notification_updated_at
    BEFORE UPDATE ON parametrage_notification
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insérer des paramètres de notification par défaut
INSERT INTO parametrage_notification (type_notification, nom, description, actif, envoyer_email, envoyer_sms, envoyer_push, template_email, template_sms, template_push, roles_cibles)
VALUES
    ('collecte_nouvelle', 'Nouvelle collecte', 'Notification envoyée lorsqu''une nouvelle collecte est effectuée', TRUE, FALSE, FALSE, TRUE, NULL, NULL, 'Nouvelle collecte de {montant} FCFA par {collecteur_nom}', '["admin", "agent_back_office"]'),
    ('collecte_cloturee', 'Collecte clôturée', 'Notification envoyée lorsqu''une collecte est clôturée', TRUE, FALSE, FALSE, TRUE, NULL, NULL, 'Collecte clôturée : {montant_total} FCFA', '["admin", "agent_back_office"]'),
    ('relance_envoyee', 'Relance envoyée', 'Notification envoyée lorsqu''une relance est envoyée à un contribuable', TRUE, FALSE, TRUE, TRUE, NULL, 'Relance envoyée à {contribuable_nom}', 'Relance envoyée à {contribuable_nom}', '["admin", "agent_back_office"]'),
    ('paiement_reçu', 'Paiement reçu', 'Notification envoyée lorsqu''un paiement est reçu', TRUE, TRUE, FALSE, TRUE, 'Paiement de {montant} FCFA reçu de {contribuable_nom}', NULL, 'Paiement de {montant} FCFA reçu', '["admin", "agent_back_office", "agent_front_office"]'),
    ('alerte_impaye', 'Alerte impayé', 'Notification envoyée lorsqu''un impayé est détecté', TRUE, TRUE, TRUE, TRUE, 'Alerte : Impayé détecté pour {contribuable_nom}', 'Alerte impayé : {contribuable_nom}', 'Alerte impayé : {contribuable_nom}', '["admin", "agent_back_office", "controleur_interne"]'),
    ('caisse_ouverte', 'Caisse ouverte', 'Notification envoyée lorsqu''une caisse est ouverte', TRUE, FALSE, FALSE, TRUE, NULL, NULL, 'Caisse {caisse_nom} ouverte', '["admin", "agent_back_office"]'),
    ('caisse_fermee', 'Caisse fermée', 'Notification envoyée lorsqu''une caisse est fermée', TRUE, TRUE, FALSE, TRUE, 'Caisse {caisse_nom} fermée avec un solde de {solde} FCFA', NULL, 'Caisse {caisse_nom} fermée', '["admin", "agent_back_office"]')
ON CONFLICT (type_notification) DO NOTHING;

-- Commentaires sur la table et les colonnes
COMMENT ON TABLE parametrage_notification IS 'Paramètres de configuration des notifications du système';
COMMENT ON COLUMN parametrage_notification.type_notification IS 'Type unique de notification (ex: collecte_nouvelle, relance_envoyee)';
COMMENT ON COLUMN parametrage_notification.nom IS 'Nom descriptif du paramètre de notification';
COMMENT ON COLUMN parametrage_notification.description IS 'Description détaillée du paramètre';
COMMENT ON COLUMN parametrage_notification.actif IS 'Indique si le paramètre est actif';
COMMENT ON COLUMN parametrage_notification.envoyer_email IS 'Indique si les notifications de ce type doivent être envoyées par email';
COMMENT ON COLUMN parametrage_notification.envoyer_sms IS 'Indique si les notifications de ce type doivent être envoyées par SMS';
COMMENT ON COLUMN parametrage_notification.envoyer_push IS 'Indique si les notifications de ce type doivent être envoyées par push notification';
COMMENT ON COLUMN parametrage_notification.template_email IS 'Template pour les emails (peut contenir des variables comme {montant}, {nom}, etc.)';
COMMENT ON COLUMN parametrage_notification.template_sms IS 'Template pour les SMS (peut contenir des variables comme {montant}, {nom}, etc.)';
COMMENT ON COLUMN parametrage_notification.template_push IS 'Template pour les push notifications (peut contenir des variables comme {montant}, {nom}, etc.)';
COMMENT ON COLUMN parametrage_notification.roles_cibles IS 'Liste JSON des rôles cibles pour cette notification (ex: ["admin", "agent_back_office"])';

