-- European News Intelligence Hub Database Schema
-- Includes pgvector for semantic search and comprehensive sentiment tracking

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS pgvector;

-- Keywords table with semantic search support
CREATE TABLE IF NOT EXISTS keywords (
    id SERIAL PRIMARY KEY,
    name_en VARCHAR(255) UNIQUE NOT NULL,
    name_th VARCHAR(255),
    category VARCHAR(100),
    popularity_score FLOAT DEFAULT 0,
    search_count INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW(),
    embedding vector(384)  -- for semantic search with Sentence Transformers
);

-- Articles table with full sentiment tracking
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT,
    full_text TEXT,
    source_url TEXT UNIQUE NOT NULL,
    source_name VARCHAR(255),
    publish_date TIMESTAMP,
    scraped_date TIMESTAMP DEFAULT NOW(),
    language VARCHAR(10),
    classification VARCHAR(20) CHECK (classification IN ('fact', 'opinion', 'mixed')),
    credibility_score FLOAT DEFAULT 0.5,
    embedding vector(384),

    -- Sentiment fields
    sentiment_overall FLOAT,  -- -1.0 to 1.0
    sentiment_confidence FLOAT,  -- 0.0 to 1.0
    sentiment_subjectivity FLOAT,  -- 0.0 to 1.0
    emotion_positive FLOAT,  -- 0.0 to 1.0
    emotion_negative FLOAT,  -- 0.0 to 1.0
    emotion_neutral FLOAT  -- 0.0 to 1.0
);

-- Junction table for many-to-many relationship between keywords and articles
CREATE TABLE IF NOT EXISTS keyword_articles (
    keyword_id INT REFERENCES keywords(id) ON DELETE CASCADE,
    article_id INT REFERENCES articles(id) ON DELETE CASCADE,
    relevance_score FLOAT,
    PRIMARY KEY (keyword_id, article_id)
);

-- Keyword relationships for mind map visualization
CREATE TABLE IF NOT EXISTS keyword_relations (
    keyword1_id INT REFERENCES keywords(id) ON DELETE CASCADE,
    keyword2_id INT REFERENCES keywords(id) ON DELETE CASCADE,
    relation_type VARCHAR(50),  -- 'related', 'parent', 'child', 'causal'
    strength_score FLOAT,
    evidence_count INT DEFAULT 0,
    PRIMARY KEY (keyword1_id, keyword2_id)
);

-- User-submitted keyword suggestions
CREATE TABLE IF NOT EXISTS keyword_suggestions (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(255) NOT NULL,
    suggested_at TIMESTAMP DEFAULT NOW(),
    suggested_by_ip VARCHAR(45),
    vote_count INT DEFAULT 1,
    status VARCHAR(20) DEFAULT 'pending'  -- 'pending', 'approved', 'rejected'
);

-- Manually uploaded documents
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255),
    upload_date TIMESTAMP DEFAULT NOW(),
    extracted_text TEXT,
    source_type VARCHAR(50),
    metadata JSONB
);

-- Daily sentiment trends aggregation
CREATE TABLE IF NOT EXISTS sentiment_trends (
    id SERIAL PRIMARY KEY,
    keyword_id INT REFERENCES keywords(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    avg_sentiment FLOAT,
    article_count INT,
    positive_count INT,
    negative_count INT,
    neutral_count INT,
    top_sources JSONB,  -- Which sources were most positive/negative
    UNIQUE(keyword_id, date)
);

-- Comparative sentiment analysis (Thailand vs. others)
CREATE TABLE IF NOT EXISTS comparative_sentiment (
    id SERIAL PRIMARY KEY,
    primary_keyword VARCHAR(255),  -- e.g., "Thailand"
    comparison_keyword VARCHAR(255),  -- e.g., "Vietnam"
    date_range_start DATE,
    date_range_end DATE,
    primary_avg_sentiment FLOAT,
    comparison_avg_sentiment FLOAT,
    sentiment_gap FLOAT,  -- difference between the two
    article_count_primary INT,
    article_count_comparison INT
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_articles_publish_date ON articles(publish_date DESC);
CREATE INDEX IF NOT EXISTS idx_keywords_popularity ON keywords(popularity_score DESC);
CREATE INDEX IF NOT EXISTS idx_articles_sentiment ON articles(sentiment_overall);
CREATE INDEX IF NOT EXISTS idx_sentiment_trends_date ON sentiment_trends(date DESC);
CREATE INDEX IF NOT EXISTS idx_sentiment_trends_keyword ON sentiment_trends(keyword_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source_name);
CREATE INDEX IF NOT EXISTS idx_articles_classification ON articles(classification);
CREATE INDEX IF NOT EXISTS idx_keyword_articles_keyword ON keyword_articles(keyword_id);
CREATE INDEX IF NOT EXISTS idx_keyword_articles_article ON keyword_articles(article_id);

-- Vector similarity indexes (IVFFlat for faster similarity search)
-- Note: These will be created after data is inserted
-- CREATE INDEX idx_articles_embedding ON articles USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- CREATE INDEX idx_keywords_embedding ON keywords USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);

-- Insert sample data for Thailand keyword
INSERT INTO keywords (name_en, name_th, category, popularity_score)
VALUES ('Thailand', 'ประเทศไทย', 'Country', 100.0)
ON CONFLICT (name_en) DO NOTHING;

-- Create function to update last_updated timestamp
CREATE OR REPLACE FUNCTION update_last_updated()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update last_updated on keywords
CREATE TRIGGER keywords_update_timestamp
    BEFORE UPDATE ON keywords
    FOR EACH ROW
    EXECUTE FUNCTION update_last_updated();

-- View for sentiment summary by keyword
CREATE OR REPLACE VIEW keyword_sentiment_summary AS
SELECT
    k.id,
    k.name_en,
    k.name_th,
    COUNT(DISTINCT a.id) as article_count,
    AVG(a.sentiment_overall) as avg_sentiment,
    AVG(a.sentiment_confidence) as avg_confidence,
    SUM(CASE WHEN a.sentiment_overall > 0.2 THEN 1 ELSE 0 END) as positive_count,
    SUM(CASE WHEN a.sentiment_overall < -0.2 THEN 1 ELSE 0 END) as negative_count,
    SUM(CASE WHEN a.sentiment_overall BETWEEN -0.2 AND 0.2 THEN 1 ELSE 0 END) as neutral_count
FROM keywords k
LEFT JOIN keyword_articles ka ON k.id = ka.keyword_id
LEFT JOIN articles a ON ka.article_id = a.id
WHERE a.sentiment_overall IS NOT NULL
GROUP BY k.id, k.name_en, k.name_th;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO newsadmin;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO newsadmin;
