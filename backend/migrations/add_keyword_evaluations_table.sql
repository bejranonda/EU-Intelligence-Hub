-- Migration: create keyword_evaluations table
CREATE TABLE IF NOT EXISTS keyword_evaluations (
    id SERIAL PRIMARY KEY,
    suggestion_id INTEGER REFERENCES keyword_suggestions(id) ON DELETE SET NULL,
    keyword_id INTEGER REFERENCES keywords(id) ON DELETE SET NULL,
    keyword_text VARCHAR(255) NOT NULL,
    searchability_score INTEGER,
    significance_score INTEGER,
    specificity VARCHAR(50),
    decision VARCHAR(20),
    reasoning TEXT,
    evaluation_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_keyword_evaluations_suggestion ON keyword_evaluations(suggestion_id);
CREATE INDEX IF NOT EXISTS idx_keyword_evaluations_keyword ON keyword_evaluations(keyword_id);
