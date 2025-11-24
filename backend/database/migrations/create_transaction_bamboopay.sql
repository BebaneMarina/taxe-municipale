-- Migration pour créer la table transaction_bamboopay
-- Table pour enregistrer les transactions de paiement via BambooPay

-- Créer l'enum pour le statut de transaction
DO $$ BEGIN
    CREATE TYPE statut_transaction_enum AS ENUM ('pending', 'success', 'failed', 'cancelled', 'refunded');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Créer la table transaction_bamboopay
CREATE TABLE IF NOT EXISTS transaction_bamboopay (
    id SERIAL PRIMARY KEY,
    contribuable_id INTEGER REFERENCES contribuable(id) ON DELETE SET NULL,
    affectation_taxe_id INTEGER REFERENCES affectation_taxe(id) ON DELETE SET NULL,
    taxe_id INTEGER REFERENCES taxe(id) ON DELETE SET NULL,
    
    -- Informations du payeur
    payer_name VARCHAR(200) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    matricule VARCHAR(50),
    raison_sociale VARCHAR(200),
    
    -- Informations de transaction
    billing_id VARCHAR(100) UNIQUE NOT NULL,
    transaction_amount NUMERIC(12, 2) NOT NULL,
    reference_bp VARCHAR(100),
    transaction_id VARCHAR(100),
    
    -- Statut
    statut statut_transaction_enum DEFAULT 'pending',
    statut_message TEXT,
    
    -- URLs
    return_url VARCHAR(500),
    callback_url VARCHAR(500),
    
    -- Métadonnées
    operateur VARCHAR(50),
    payment_method VARCHAR(50),
    metadata_json JSONB,
    
    -- Dates
    date_initiation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_paiement TIMESTAMP,
    date_callback TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Créer les index
CREATE INDEX IF NOT EXISTS idx_transaction_billing_id ON transaction_bamboopay(billing_id);
CREATE INDEX IF NOT EXISTS idx_transaction_reference_bp ON transaction_bamboopay(reference_bp);
CREATE INDEX IF NOT EXISTS idx_transaction_transaction_id ON transaction_bamboopay(transaction_id);
CREATE INDEX IF NOT EXISTS idx_transaction_statut ON transaction_bamboopay(statut);
CREATE INDEX IF NOT EXISTS idx_transaction_contribuable ON transaction_bamboopay(contribuable_id);
CREATE INDEX IF NOT EXISTS idx_transaction_taxe ON transaction_bamboopay(taxe_id);

-- Créer un trigger pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_transaction_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_transaction_updated_at ON transaction_bamboopay;
CREATE TRIGGER trigger_update_transaction_updated_at
    BEFORE UPDATE ON transaction_bamboopay
    FOR EACH ROW
    EXECUTE FUNCTION update_transaction_updated_at();

COMMENT ON TABLE transaction_bamboopay IS 'Transactions de paiement via BambooPay';
COMMENT ON COLUMN transaction_bamboopay.billing_id IS 'ID facture côté marchand (unique)';
COMMENT ON COLUMN transaction_bamboopay.reference_bp IS 'Référence retournée par BambooPay';
COMMENT ON COLUMN transaction_bamboopay.transaction_id IS 'ID transaction BambooPay';
COMMENT ON COLUMN transaction_bamboopay.payment_method IS 'web ou mobile_instant';
COMMENT ON COLUMN transaction_bamboopay.operateur IS 'moov_money ou airtel_money pour paiement instantané';

