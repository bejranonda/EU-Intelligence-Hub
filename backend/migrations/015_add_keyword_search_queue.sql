-- Migration: add keyword search queue

BEGIN;

-- Add scheduling metadata to keywords table
ALTER TABLE keywords
    ADD COLUMN IF NOT EXISTS next_search_after TIMESTAMP,
    ADD COLUMN IF NOT EXISTS search_priority INTEGER DEFAULT 0;

-- Create keyword search queue table
CREATE TABLE IF NOT EXISTS keyword_search_queue (
    id SERIAL PRIMARY KEY,
    keyword_id INTEGER NOT NULL REFERENCES keywords(id) ON DELETE CASCADE,
    scheduled_at TIMESTAMP NOT NULL,
    priority INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    status VARCHAR(20) DEFAULT 'pending',
    last_attempt_at TIMESTAMP,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_keyword_search_queue_status_scheduled
    ON keyword_search_queue (status, scheduled_at);

CREATE INDEX IF NOT EXISTS idx_keyword_search_queue_priority
    ON keyword_search_queue (priority DESC, scheduled_at);

CREATE INDEX IF NOT EXISTS idx_keyword_search_queue_keyword
    ON keyword_search_queue (keyword_id);

COMMIT;
