-- =====================================================
-- Script de création de la base de données PostgreSQL
-- Application de Collecte de Taxe Municipale
-- Mairie de Libreville - Gabon
-- =====================================================

-- Créer la base de données (à exécuter en tant que superutilisateur)
-- CREATE DATABASE taxe_municipale;
-- \c taxe_municipale;

-- Extension pour les UUIDs (optionnel)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==================== TABLE SERVICE ====================
CREATE TABLE IF NOT EXISTS service (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    code VARCHAR(20) UNIQUE NOT NULL,
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== TABLE TYPE_TAXE ====================
CREATE TABLE IF NOT EXISTS type_taxe (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== TABLE ZONE ====================
CREATE TABLE IF NOT EXISTS zone (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== TABLE QUARTIER ====================
CREATE TABLE IF NOT EXISTS quartier (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    zone_id INTEGER NOT NULL REFERENCES zone(id) ON DELETE RESTRICT,
    description TEXT,
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== TABLE TYPE_CONTRIBUABLE ====================
CREATE TABLE IF NOT EXISTS type_contribuable (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50) NOT NULL UNIQUE,
    code VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== TABLE COLLECTEUR ====================
CREATE TYPE statut_collecteur_enum AS ENUM ('active', 'desactive');
CREATE TYPE etat_collecteur_enum AS ENUM ('connecte', 'deconnecte');

CREATE TABLE IF NOT EXISTS collecteur (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telephone VARCHAR(20) UNIQUE NOT NULL,
    matricule VARCHAR(50) UNIQUE NOT NULL,
    statut statut_collecteur_enum DEFAULT 'active',
    etat etat_collecteur_enum DEFAULT 'deconnecte',
    zone_id INTEGER REFERENCES zone(id) ON DELETE SET NULL,
    date_derniere_connexion TIMESTAMP,
    date_derniere_deconnexion TIMESTAMP,
    heure_cloture VARCHAR(5), -- Format HH:MM
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== TABLE CONTRIBUABLE ====================
CREATE TABLE IF NOT EXISTS contribuable (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    telephone VARCHAR(20) UNIQUE NOT NULL,
    type_contribuable_id INTEGER NOT NULL REFERENCES type_contribuable(id) ON DELETE RESTRICT,
    quartier_id INTEGER NOT NULL REFERENCES quartier(id) ON DELETE RESTRICT,
    collecteur_id INTEGER NOT NULL REFERENCES collecteur(id) ON DELETE RESTRICT,
    adresse TEXT,
    latitude NUMERIC(10, 8),
    longitude NUMERIC(11, 8),
    numero_identification VARCHAR(50) UNIQUE,
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== TABLE TAXE ====================
CREATE TYPE periodicite_enum AS ENUM ('journaliere', 'hebdomadaire', 'mensuelle', 'trimestrielle');

CREATE TABLE IF NOT EXISTS taxe (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    montant NUMERIC(12, 2) NOT NULL,
    montant_variable BOOLEAN DEFAULT FALSE,
    periodicite periodicite_enum NOT NULL,
    type_taxe_id INTEGER NOT NULL REFERENCES type_taxe(id) ON DELETE RESTRICT,
    service_id INTEGER NOT NULL REFERENCES service(id) ON DELETE RESTRICT,
    commission_pourcentage NUMERIC(5, 2) DEFAULT 0.00,
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== TABLE AFFECTATION_TAXE ====================
CREATE TABLE IF NOT EXISTS affectation_taxe (
    id SERIAL PRIMARY KEY,
    contribuable_id INTEGER NOT NULL REFERENCES contribuable(id) ON DELETE CASCADE,
    taxe_id INTEGER NOT NULL REFERENCES taxe(id) ON DELETE CASCADE,
    date_debut TIMESTAMP NOT NULL,
    date_fin TIMESTAMP,
    montant_custom NUMERIC(12, 2),
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(contribuable_id, taxe_id, date_debut)
);

-- ==================== TABLE INFO_COLLECTE ====================
CREATE TYPE type_paiement_enum AS ENUM ('especes', 'mobile_money', 'carte');
CREATE TYPE statut_collecte_enum AS ENUM ('pending', 'completed', 'failed', 'cancelled');

CREATE TABLE IF NOT EXISTS info_collecte (
    id SERIAL PRIMARY KEY,
    contribuable_id INTEGER NOT NULL REFERENCES contribuable(id) ON DELETE RESTRICT,
    taxe_id INTEGER NOT NULL REFERENCES taxe(id) ON DELETE RESTRICT,
    collecteur_id INTEGER NOT NULL REFERENCES collecteur(id) ON DELETE RESTRICT,
    montant NUMERIC(12, 2) NOT NULL,
    commission NUMERIC(12, 2) DEFAULT 0.00,
    type_paiement type_paiement_enum NOT NULL,
    statut statut_collecte_enum DEFAULT 'pending',
    reference VARCHAR(50) UNIQUE NOT NULL,
    billetage TEXT, -- JSON string
    date_collecte TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_cloture TIMESTAMP,
    sms_envoye BOOLEAN DEFAULT FALSE,
    ticket_imprime BOOLEAN DEFAULT FALSE,
    annule BOOLEAN DEFAULT FALSE,
    raison_annulation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== TABLE UTILISATEUR (pour l'authentification) ====================
CREATE TYPE role_enum AS ENUM ('admin', 'agent_back_office', 'agent_front_office', 'controleur_interne', 'collecteur');

CREATE TABLE IF NOT EXISTS utilisateur (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telephone VARCHAR(20) UNIQUE,
    mot_de_passe_hash VARCHAR(255) NOT NULL,
    role role_enum NOT NULL DEFAULT 'agent_back_office',
    actif BOOLEAN DEFAULT TRUE,
    derniere_connexion TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== INDEXES ====================
CREATE INDEX IF NOT EXISTS idx_contribuable_collecteur ON contribuable(collecteur_id);
CREATE INDEX IF NOT EXISTS idx_contribuable_quartier ON contribuable(quartier_id);
CREATE INDEX IF NOT EXISTS idx_contribuable_type ON contribuable(type_contribuable_id);
CREATE INDEX IF NOT EXISTS idx_contribuable_telephone ON contribuable(telephone);
CREATE INDEX IF NOT EXISTS idx_contribuable_numero_id ON contribuable(numero_identification);

CREATE INDEX IF NOT EXISTS idx_collecteur_zone ON collecteur(zone_id);
CREATE INDEX IF NOT EXISTS idx_collecteur_matricule ON collecteur(matricule);
CREATE INDEX IF NOT EXISTS idx_collecteur_email ON collecteur(email);
CREATE INDEX IF NOT EXISTS idx_collecteur_statut ON collecteur(statut);
CREATE INDEX IF NOT EXISTS idx_collecteur_etat ON collecteur(etat);

CREATE INDEX IF NOT EXISTS idx_taxe_type ON taxe(type_taxe_id);
CREATE INDEX IF NOT EXISTS idx_taxe_service ON taxe(service_id);
CREATE INDEX IF NOT EXISTS idx_taxe_code ON taxe(code);

CREATE INDEX IF NOT EXISTS idx_collecte_contribuable ON info_collecte(contribuable_id);
CREATE INDEX IF NOT EXISTS idx_collecte_taxe ON info_collecte(taxe_id);
CREATE INDEX IF NOT EXISTS idx_collecte_collecteur ON info_collecte(collecteur_id);
CREATE INDEX IF NOT EXISTS idx_collecte_date ON info_collecte(date_collecte);
CREATE INDEX IF NOT EXISTS idx_collecte_reference ON info_collecte(reference);
CREATE INDEX IF NOT EXISTS idx_collecte_statut ON info_collecte(statut);

CREATE INDEX IF NOT EXISTS idx_affectation_contribuable ON affectation_taxe(contribuable_id);
CREATE INDEX IF NOT EXISTS idx_affectation_taxe ON affectation_taxe(taxe_id);

CREATE INDEX IF NOT EXISTS idx_utilisateur_email ON utilisateur(email);
CREATE INDEX IF NOT EXISTS idx_utilisateur_role ON utilisateur(role);

-- ==================== TRIGGERS POUR updated_at ====================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_service_updated_at BEFORE UPDATE ON service
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_type_taxe_updated_at BEFORE UPDATE ON type_taxe
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_zone_updated_at BEFORE UPDATE ON zone
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_quartier_updated_at BEFORE UPDATE ON quartier
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_type_contribuable_updated_at BEFORE UPDATE ON type_contribuable
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_collecteur_updated_at BEFORE UPDATE ON collecteur
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contribuable_updated_at BEFORE UPDATE ON contribuable
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_taxe_updated_at BEFORE UPDATE ON taxe
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_affectation_taxe_updated_at BEFORE UPDATE ON affectation_taxe
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_info_collecte_updated_at BEFORE UPDATE ON info_collecte
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_utilisateur_updated_at BEFORE UPDATE ON utilisateur
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==================== COMMENTAIRES ====================
COMMENT ON TABLE service IS 'Services de la mairie';
COMMENT ON TABLE type_taxe IS 'Types de taxes municipales';
COMMENT ON TABLE zone IS 'Zones géographiques de Libreville';
COMMENT ON TABLE quartier IS 'Quartiers de Libreville';
COMMENT ON TABLE type_contribuable IS 'Types de contribuables';
COMMENT ON TABLE collecteur IS 'Collecteurs de taxes';
COMMENT ON TABLE contribuable IS 'Contribuables (clients)';
COMMENT ON TABLE taxe IS 'Taxes municipales';
COMMENT ON TABLE affectation_taxe IS 'Affectation d''une taxe à un contribuable';
COMMENT ON TABLE info_collecte IS 'Informations sur les collectes effectuées';
COMMENT ON TABLE utilisateur IS 'Utilisateurs du système (authentification)';

