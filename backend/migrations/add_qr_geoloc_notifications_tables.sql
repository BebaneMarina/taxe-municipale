-- Migration: Ajout des tables pour QR Code, Géolocalisation et Notifications
-- Date: 2024-01-15

-- 1. Ajouter la colonne qr_code à la table contribuable
ALTER TABLE contribuable 
ADD COLUMN IF NOT EXISTS qr_code VARCHAR(100) UNIQUE;

CREATE INDEX IF NOT EXISTS idx_contribuable_qr_code ON contribuable(qr_code);

-- 2. Créer la table collecte_location
CREATE TABLE IF NOT EXISTS collecte_location (
    id SERIAL PRIMARY KEY,
    collecte_id INTEGER NOT NULL UNIQUE REFERENCES info_collecte(id) ON DELETE CASCADE,
    latitude NUMERIC(10, 8) NOT NULL,
    longitude NUMERIC(11, 8) NOT NULL,
    accuracy NUMERIC(10, 2),
    altitude NUMERIC(10, 2),
    heading NUMERIC(5, 2),
    speed NUMERIC(10, 2),
    timestamp TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_collecte_location_collecte_id ON collecte_location(collecte_id);

-- 3. Créer la table collecteur_zone
CREATE TABLE IF NOT EXISTS collecteur_zone (
    id SERIAL PRIMARY KEY,
    collecteur_id INTEGER NOT NULL REFERENCES collecteur(id) ON DELETE CASCADE,
    nom VARCHAR(255) NOT NULL,
    latitude NUMERIC(10, 8) NOT NULL,
    longitude NUMERIC(11, 8) NOT NULL,
    radius NUMERIC(10, 2) NOT NULL DEFAULT 1000.0,
    description TEXT,
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_collecteur_zone_collecteur_id ON collecteur_zone(collecteur_id);

-- 4. Créer la table notification_token
CREATE TABLE IF NOT EXISTS notification_token (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES utilisateur(id) ON DELETE CASCADE,
    token VARCHAR(500) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, token)
);

CREATE INDEX IF NOT EXISTS idx_notification_token_user_id ON notification_token(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_token_token ON notification_token(token);

-- 5. Créer la table notification
CREATE TABLE IF NOT EXISTS notification (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES utilisateur(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    read BOOLEAN DEFAULT FALSE,
    data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_notification_user_id ON notification(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_read ON notification(user_id, read);
CREATE INDEX IF NOT EXISTS idx_notification_created_at ON notification(created_at DESC);

-- 6. Créer un trigger pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Appliquer le trigger aux nouvelles tables
DROP TRIGGER IF EXISTS update_collecte_location_updated_at ON collecte_location;
CREATE TRIGGER update_collecte_location_updated_at
    BEFORE UPDATE ON collecte_location
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_collecteur_zone_updated_at ON collecteur_zone;
CREATE TRIGGER update_collecteur_zone_updated_at
    BEFORE UPDATE ON collecteur_zone
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_notification_token_updated_at ON notification_token;
CREATE TRIGGER update_notification_token_updated_at
    BEFORE UPDATE ON notification_token
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_notification_updated_at ON notification;
CREATE TRIGGER update_notification_updated_at
    BEFORE UPDATE ON notification
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

