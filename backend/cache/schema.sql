-- Legal Cache Database Schema
-- Stores cached laws and articles from e-TAR

CREATE TABLE IF NOT EXISTS law_cache (
    law_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    full_text TEXT NOT NULL,
    version TEXT NOT NULL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    metadata TEXT  -- JSON string
);

CREATE TABLE IF NOT EXISTS article_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    law_id TEXT NOT NULL,
    article_number TEXT NOT NULL,
    article_title TEXT,
    content TEXT NOT NULL,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(law_id, article_number),
    FOREIGN KEY (law_id) REFERENCES law_cache(law_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_law_id ON article_cache(law_id);
CREATE INDEX IF NOT EXISTS idx_article_number ON article_cache(article_number);
CREATE INDEX IF NOT EXISTS idx_expires_at ON law_cache(expires_at);
