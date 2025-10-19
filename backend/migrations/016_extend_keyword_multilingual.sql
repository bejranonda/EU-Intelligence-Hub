-- Migration: extend keyword suggestions and keywords with multilingual fields

BEGIN;

ALTER TABLE keywords
    ADD COLUMN IF NOT EXISTS keyword_de VARCHAR(255),
    ADD COLUMN IF NOT EXISTS keyword_fr VARCHAR(255),
    ADD COLUMN IF NOT EXISTS keyword_es VARCHAR(255),
    ADD COLUMN IF NOT EXISTS keyword_it VARCHAR(255),
    ADD COLUMN IF NOT EXISTS keyword_pl VARCHAR(255),
    ADD COLUMN IF NOT EXISTS keyword_sv VARCHAR(255),
    ADD COLUMN IF NOT EXISTS keyword_nl VARCHAR(255);

ALTER TABLE keyword_suggestions
    ADD COLUMN IF NOT EXISTS keyword_de VARCHAR(255),
    ADD COLUMN IF NOT EXISTS keyword_fr VARCHAR(255),
    ADD COLUMN IF NOT EXISTS keyword_es VARCHAR(255),
    ADD COLUMN IF NOT EXISTS keyword_it VARCHAR(255),
    ADD COLUMN IF NOT EXISTS keyword_pl VARCHAR(255),
    ADD COLUMN IF NOT EXISTS keyword_sv VARCHAR(255),
    ADD COLUMN IF NOT EXISTS keyword_nl VARCHAR(255);

COMMIT;
