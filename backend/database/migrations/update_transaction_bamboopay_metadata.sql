-- Migration pour renommer la colonne metadata en metadata_json
-- (car 'metadata' est réservé dans SQLAlchemy)

-- Vérifier si la colonne metadata existe et la renommer
DO $$ 
BEGIN
    -- Vérifier si la colonne metadata existe
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'transaction_bamboopay' 
        AND column_name = 'metadata'
    ) THEN
        -- Renommer la colonne
        ALTER TABLE transaction_bamboopay RENAME COLUMN metadata TO metadata_json;
        RAISE NOTICE 'Colonne metadata renommée en metadata_json';
    ELSE
        -- Si metadata n'existe pas, vérifier si metadata_json existe
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name = 'transaction_bamboopay' 
            AND column_name = 'metadata_json'
        ) THEN
            -- Ajouter la colonne metadata_json si elle n'existe pas
            ALTER TABLE transaction_bamboopay ADD COLUMN metadata_json JSONB;
            RAISE NOTICE 'Colonne metadata_json ajoutée';
        ELSE
            RAISE NOTICE 'Colonne metadata_json existe déjà';
        END IF;
    END IF;
END $$;

