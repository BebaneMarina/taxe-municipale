-- Migration: Création des tables pour la gestion des caisses des collecteurs
-- Date: 2025-01-25

BEGIN;

-- Créer les types ENUM si ils n'existent pas
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'type_caisse_enum') THEN
        CREATE TYPE type_caisse_enum AS ENUM ('physique', 'en_ligne');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'etat_caisse_enum') THEN
        CREATE TYPE etat_caisse_enum AS ENUM ('ouverte', 'fermee', 'suspendue', 'cloturee');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'type_operation_caisse_enum') THEN
        CREATE TYPE type_operation_caisse_enum AS ENUM ('ouverture', 'fermeture', 'entree', 'sortie', 'ajustement', 'cloture');
    END IF;
END $$;

-- Table CAISSE
CREATE TABLE IF NOT EXISTS public.caisse (
    id SERIAL PRIMARY KEY,
    collecteur_id INTEGER NOT NULL REFERENCES public.collecteur(id) ON DELETE CASCADE,
    type_caisse type_caisse_enum NOT NULL,
    etat etat_caisse_enum NOT NULL DEFAULT 'fermee',
    code VARCHAR(50) UNIQUE NOT NULL,
    nom VARCHAR(100),
    solde_initial NUMERIC(12, 2) DEFAULT 0.00,
    solde_actuel NUMERIC(12, 2) DEFAULT 0.00,
    date_ouverture TIMESTAMP WITHOUT TIME ZONE,
    date_fermeture TIMESTAMP WITHOUT TIME ZONE,
    date_cloture TIMESTAMP WITHOUT TIME ZONE,
    montant_cloture NUMERIC(12, 2),
    notes TEXT,
    actif BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index pour la table CAISSE
CREATE INDEX IF NOT EXISTS idx_caisse_collecteur_id ON public.caisse(collecteur_id);
CREATE INDEX IF NOT EXISTS idx_caisse_code ON public.caisse(code);
CREATE INDEX IF NOT EXISTS idx_caisse_etat ON public.caisse(etat);
CREATE INDEX IF NOT EXISTS idx_caisse_type ON public.caisse(type_caisse);

-- Si la table operation_caisse existe déjà, ajouter les colonnes manquantes AVANT de créer les index
DO $$ 
BEGIN
    -- Ajouter caisse_id si elle n'existe pas (nullable d'abord, on la rendra NOT NULL après migration des données)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema = 'public' AND table_name = 'operation_caisse' AND column_name = 'caisse_id') THEN
        ALTER TABLE public.operation_caisse ADD COLUMN caisse_id INTEGER;
    END IF;
    
    -- Ajouter solde_avant si elle n'existe pas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema = 'public' AND table_name = 'operation_caisse' AND column_name = 'solde_avant') THEN
        ALTER TABLE public.operation_caisse ADD COLUMN solde_avant NUMERIC(12, 2);
    END IF;
    
    -- Ajouter solde_apres si elle n'existe pas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_schema = 'public' AND table_name = 'operation_caisse' AND column_name = 'solde_apres') THEN
        ALTER TABLE public.operation_caisse ADD COLUMN solde_apres NUMERIC(12, 2);
    END IF;
END $$;

-- Table OPERATION_CAISSE (créer seulement si elle n'existe pas)
CREATE TABLE IF NOT EXISTS public.operation_caisse (
    id SERIAL PRIMARY KEY,
    caisse_id INTEGER REFERENCES public.caisse(id) ON DELETE CASCADE,
    collecteur_id INTEGER NOT NULL REFERENCES public.collecteur(id) ON DELETE CASCADE,
    type_operation type_operation_caisse_enum NOT NULL,
    montant NUMERIC(12, 2) NOT NULL,
    libelle VARCHAR(200) NOT NULL,
    collecte_id INTEGER REFERENCES public.info_collecte(id) ON DELETE SET NULL,
    reference VARCHAR(50) UNIQUE,
    solde_avant NUMERIC(12, 2),
    solde_apres NUMERIC(12, 2),
    notes TEXT,
    date_operation TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Ajouter la contrainte FK pour caisse_id si elle n'existe pas déjà
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_operation_caisse_caisse'
    ) THEN
        ALTER TABLE public.operation_caisse 
        ADD CONSTRAINT fk_operation_caisse_caisse 
        FOREIGN KEY (caisse_id) REFERENCES public.caisse(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Index pour la table OPERATION_CAISSE
CREATE INDEX IF NOT EXISTS idx_operation_caisse_caisse_id ON public.operation_caisse(caisse_id) WHERE caisse_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_operation_caisse_collecteur_id ON public.operation_caisse(collecteur_id);
CREATE INDEX IF NOT EXISTS idx_operation_caisse_date ON public.operation_caisse(date_operation);
CREATE INDEX IF NOT EXISTS idx_operation_caisse_type ON public.operation_caisse(type_operation);
CREATE INDEX IF NOT EXISTS idx_operation_caisse_reference ON public.operation_caisse(reference) WHERE reference IS NOT NULL;

-- Mettre à jour le type_operation enum si nécessaire
DO $$
BEGIN
    -- Vérifier si les nouvelles valeurs existent dans l'enum
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_schema = 'public' AND table_name = 'operation_caisse' AND column_name = 'type_operation') THEN
        BEGIN
            -- PostgreSQL ne supporte pas ADD VALUE IF NOT EXISTS, donc on utilise une exception
            ALTER TYPE type_operation_caisse_enum ADD VALUE 'ouverture';
        EXCEPTION WHEN duplicate_object THEN
            NULL;
        END;
        
        BEGIN
            ALTER TYPE type_operation_caisse_enum ADD VALUE 'fermeture';
        EXCEPTION WHEN duplicate_object THEN
            NULL;
        END;
        
        BEGIN
            ALTER TYPE type_operation_caisse_enum ADD VALUE 'cloture';
        EXCEPTION WHEN duplicate_object THEN
            NULL;
        END;
    END IF;
END $$;

-- Fonction pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_caisse_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour updated_at sur CAISSE
DROP TRIGGER IF EXISTS trigger_update_caisse_updated_at ON public.caisse;
CREATE TRIGGER trigger_update_caisse_updated_at
    BEFORE UPDATE ON public.caisse
    FOR EACH ROW
    EXECUTE FUNCTION update_caisse_updated_at();

-- Trigger pour updated_at sur OPERATION_CAISSE
DROP TRIGGER IF EXISTS trigger_update_operation_caisse_updated_at ON public.operation_caisse;
CREATE TRIGGER trigger_update_operation_caisse_updated_at
    BEFORE UPDATE ON public.operation_caisse
    FOR EACH ROW
    EXECUTE FUNCTION update_caisse_updated_at();

-- Commentaires sur les tables
COMMENT ON TABLE public.caisse IS 'Référentiel des caisses des collecteurs (physique et en ligne)';
COMMENT ON TABLE public.operation_caisse IS 'Opérations de caisse (ouverture, fermeture, entrées, sorties, ajustements, clôture)';

COMMENT ON COLUMN public.caisse.type_caisse IS 'Type de caisse: physique (espèces) ou en_ligne (mobile money, carte)';
COMMENT ON COLUMN public.caisse.etat IS 'État de la caisse: ouverte, fermee, suspendue, cloturee';
COMMENT ON COLUMN public.caisse.solde_actuel IS 'Solde actuel calculé automatiquement à partir des opérations';

COMMIT;

