BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'type_coupure_enum') THEN
        CREATE TYPE type_coupure_enum AS ENUM ('billet', 'piece');
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS public.coupure_caisse (
    id SERIAL PRIMARY KEY,
    valeur NUMERIC(12,2) NOT NULL,
    devise VARCHAR(3) NOT NULL DEFAULT 'XAF',
    type_coupure type_coupure_enum NOT NULL DEFAULT 'billet',
    description VARCHAR(255),
    ordre_affichage INTEGER NOT NULL DEFAULT 0,
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_coupure_valeur_devise_type
    ON public.coupure_caisse (valeur, devise, type_coupure);

CREATE INDEX IF NOT EXISTS idx_coupure_caisse_actif ON public.coupure_caisse (actif);
CREATE INDEX IF NOT EXISTS idx_coupure_caisse_ordre ON public.coupure_caisse (ordre_affichage);

COMMIT;

