-- Migration: Add last_searched column to keywords table
-- Date: 2025-10-16
-- Description: Track when a keyword was last searched for news (for 3-hour cooldown feature)

-- Add last_searched column
ALTER TABLE keywords
ADD COLUMN IF NOT EXISTS last_searched TIMESTAMP;

-- Add comment for documentation
COMMENT ON COLUMN keywords.last_searched IS 'Timestamp of when this keyword was last searched for news articles (used for 3-hour search cooldown)';
