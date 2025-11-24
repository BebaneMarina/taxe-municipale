-- Migration pour créer les tables de relances et impayés

-- ==================== ENUMS ====================
CREATE TYPE type_relance_enum AS ENUM ('sms', 'email', 'appel', 'courrier', 'visite');
CREATE TYPE statut_relance_enum AS ENUM ('en_attente', 'envoyee', 'echec', 'annulee');

-- ==================== TABLE RELANCE ====================
CREATE TABLE relance (
    id SERIAL PRIMARY KEY,
    contribuable_id INTEGER NOT NULL REFERENCES contribuable(id) ON DELETE CASCADE,
    affectation_taxe_id INTEGER REFERENCES affectation_taxe(id) ON DELETE SET NULL,
    type_relance type_relance_enum NOT NULL,
    statut statut_relance_enum NOT NULL DEFAULT 'en_attente',
    message TEXT,
    montant_due NUMERIC(12, 2) NOT NULL,
    date_echeance TIMESTAMP,
    date_envoi TIMESTAMP,
    date_planifiee TIMESTAMP NOT NULL,
    canal_envoi VARCHAR(100),
    reponse_recue BOOLEAN DEFAULT FALSE,
    date_reponse TIMESTAMP,
    notes TEXT,
    utilisateur_id INTEGER REFERENCES utilisateur(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_relance_contribuable ON relance(contribuable_id);
CREATE INDEX idx_relance_affectation_taxe ON relance(affectation_taxe_id);
CREATE INDEX idx_relance_date_planifiee ON relance(date_planifiee);
CREATE INDEX idx_relance_statut ON relance(statut);

-- ==================== TABLE DOSSIER_IMPAYE ====================
CREATE TABLE dossier_impaye (
    id SERIAL PRIMARY KEY,
    contribuable_id INTEGER NOT NULL REFERENCES contribuable(id) ON DELETE CASCADE,
    affectation_taxe_id INTEGER NOT NULL REFERENCES affectation_taxe(id) ON DELETE CASCADE,
    montant_initial NUMERIC(12, 2) NOT NULL,
    montant_paye NUMERIC(12, 2) DEFAULT 0.00,
    montant_restant NUMERIC(12, 2) NOT NULL,
    penalites NUMERIC(12, 2) DEFAULT 0.00,
    date_echeance TIMESTAMP NOT NULL,
    jours_retard INTEGER DEFAULT 0,
    statut VARCHAR(50) DEFAULT 'en_cours',
    priorite VARCHAR(20) DEFAULT 'normale',
    dernier_contact TIMESTAMP,
    nombre_relances INTEGER DEFAULT 0,
    notes TEXT,
    assigne_a INTEGER REFERENCES collecteur(id) ON DELETE SET NULL,
    date_assignation TIMESTAMP,
    date_cloture TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dossier_impaye_contribuable ON dossier_impaye(contribuable_id);
CREATE INDEX idx_dossier_impaye_affectation_taxe ON dossier_impaye(affectation_taxe_id);
CREATE INDEX idx_dossier_impaye_statut ON dossier_impaye(statut);
CREATE INDEX idx_dossier_impaye_priorite ON dossier_impaye(priorite);
CREATE INDEX idx_dossier_impaye_collecteur ON dossier_impaye(assigne_a);

-- Trigger pour mettre à jour updated_at
CREATE TRIGGER update_relance_updated_at
    BEFORE UPDATE ON relance
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dossier_impaye_updated_at
    BEFORE UPDATE ON dossier_impaye
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Commentaires
COMMENT ON TABLE relance IS 'Historique des relances envoyées aux contribuables';
COMMENT ON TABLE dossier_impaye IS 'Dossiers d''impayés pour suivi et recouvrement';

