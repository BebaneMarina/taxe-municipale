-- Migration : ajout de la colonne file_metadata sur commission_fichier
-- Objectif : aligner le schéma avec SQLAlchemy (file_metadata remplace metadata)

BEGIN;

-- Ajouter la colonne si elle n'existe pas encore
ALTER TABLE public.commission_fichier
    ADD COLUMN IF NOT EXISTS file_metadata JSONB;

-- Migrer les anciennes données depuis metadata si elle existe
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'commission_fichier'
          AND column_name = 'metadata'
    ) THEN
        UPDATE public.commission_fichier
        SET file_metadata = COALESCE(file_metadata, metadata)
        WHERE metadata IS NOT NULL;
    END IF;
END $$;

-- Supprimer l'ancienne colonne metadata si elle est encore présente
ALTER TABLE public.commission_fichier
    DROP COLUMN IF EXISTS metadata;

COMMIT;

