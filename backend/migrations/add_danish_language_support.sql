-- Migration: Add Danish language support
-- Description: Adds keyword_da column to keywords and keyword_suggestions tables
-- Date: 2024-11-17

-- Add Danish column to keywords table
ALTER TABLE keywords ADD COLUMN IF NOT EXISTS keyword_da VARCHAR(255);

-- Add Danish column to keyword_suggestions table
ALTER TABLE keyword_suggestions ADD COLUMN IF NOT EXISTS keyword_da VARCHAR(255);

-- Add comment to the columns
COMMENT ON COLUMN keywords.keyword_da IS 'Danish translation of the keyword';
COMMENT ON COLUMN keyword_suggestions.keyword_da IS 'Danish translation of the suggested keyword';
