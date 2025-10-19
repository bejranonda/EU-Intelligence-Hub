CREATE TABLE IF NOT EXISTS news_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    base_url VARCHAR(512) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    language VARCHAR(10) DEFAULT 'en',
    country VARCHAR(100),
    priority INTEGER DEFAULT 0,
    parser VARCHAR(100),
    tags TEXT[],
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS source_ingestion_history (
    id SERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES news_sources(id) ON DELETE CASCADE,
    last_run_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    articles_ingested INTEGER DEFAULT 0,
    success BOOLEAN DEFAULT TRUE,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_news_sources_enabled ON news_sources(enabled);
CREATE INDEX IF NOT EXISTS idx_news_sources_priority ON news_sources(priority);
CREATE INDEX IF NOT EXISTS idx_source_ingestion_history_source_id ON source_ingestion_history(source_id);
