-- Migration : ajout des tables journal_travaux et commissions
-- Date : 2025-01-25

BEGIN;

-- ENUM statut_journal_enum
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'statut_journal_enum') THEN
        CREATE TYPE statut_journal_enum AS ENUM ('en_cours', 'cloture');
    END IF;
END $$;

-- ENUM statut_commission_enum (utilisé pour fichiers et paiements)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'statut_commission_enum') THEN
        CREATE TYPE statut_commission_enum AS ENUM ('en_attente', 'envoyee', 'payee');
    END IF;
END $$;

-- Table journal_travaux
CREATE TABLE IF NOT EXISTS public.journal_travaux (
    id SERIAL PRIMARY KEY,
    date_jour DATE NOT NULL UNIQUE,
    statut statut_journal_enum NOT NULL DEFAULT 'en_cours',
    nb_collectes INTEGER DEFAULT 0,
    montant_collectes NUMERIC(12,2) DEFAULT 0,
    nb_operations_caisse INTEGER DEFAULT 0,
    total_entrees_caisse NUMERIC(12,2) DEFAULT 0,
    total_sorties_caisse NUMERIC(12,2) DEFAULT 0,
    relances_envoyees INTEGER DEFAULT 0,
    impayes_regles INTEGER DEFAULT 0,
    remarque TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP WITHOUT TIME ZONE,
    closed_by INTEGER REFERENCES public.utilisateur(id)
);

CREATE INDEX IF NOT EXISTS idx_journal_travaux_date ON public.journal_travaux(date_jour);

-- Table commission_fichier
CREATE TABLE IF NOT EXISTS public.commission_fichier (
    id SERIAL PRIMARY KEY,
    date_jour DATE NOT NULL,
    chemin VARCHAR(255) NOT NULL,
    type_fichier VARCHAR(20) DEFAULT 'csv',
    statut statut_commission_enum NOT NULL DEFAULT 'en_attente',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES public.utilisateur(id),
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_commission_fichier_date ON public.commission_fichier(date_jour);

-- Table commission_journaliere
CREATE TABLE IF NOT EXISTS public.commission_journaliere (
    id SERIAL PRIMARY KEY,
    date_jour DATE NOT NULL,
    collecteur_id INTEGER NOT NULL REFERENCES public.collecteur(id) ON DELETE CASCADE,
    montant_collecte NUMERIC(12,2) DEFAULT 0,
    commission_montant NUMERIC(12,2) DEFAULT 0,
    commission_pourcentage NUMERIC(5,2) DEFAULT 0,
    statut_paiement statut_commission_enum NOT NULL DEFAULT 'en_attente',
    fichier_id INTEGER REFERENCES public.commission_fichier(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_commission_jour_date ON public.commission_journaliere(date_jour);
CREATE INDEX IF NOT EXISTS idx_commission_jour_collecteur ON public.commission_journaliere(collecteur_id);

-- Trigger mise à jour updated_at journal_travaux
CREATE OR REPLACE FUNCTION update_journal_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_journal_travaux_updated ON public.journal_travaux;
CREATE TRIGGER trg_journal_travaux_updated
    BEFORE UPDATE ON public.journal_travaux
    FOR EACH ROW
    EXECUTE FUNCTION update_journal_updated_at();

COMMIT;

