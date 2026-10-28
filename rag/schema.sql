CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    book TEXT NOT NULL,
    layer TEXT NOT NULL,
    pian TEXT NOT NULL DEFAULT '',
    zhang TEXT NOT NULL DEFAULT '',
    anchor TEXT NOT NULL DEFAULT '',
    part INTEGER NOT NULL DEFAULT 0,
    source TEXT NOT NULL DEFAULT '',
    body TEXT NOT NULL DEFAULT '',
    embedding vector(1024),
    fts tsvector GENERATED ALWAYS AS (to_tsvector('simple', coalesce(body, ''))) STORED
);

CREATE INDEX IF NOT EXISTS documents_fts ON documents USING GIN (fts);
CREATE INDEX IF NOT EXISTS documents_embedding
    ON documents USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS documents_zhang ON documents (zhang);
CREATE INDEX IF NOT EXISTS documents_layer ON documents (layer);
