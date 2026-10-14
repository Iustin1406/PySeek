CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS code_units (
    id SERIAL PRIMARY KEY,
    repository_path TEXT NOT NULL,
    name TEXT NOT NULL,
    filepath TEXT NOT NULL,
    start_line INTEGER,
    end_line INTEGER,
    scope_path TEXT[],
    source_code TEXT,
    embedding VECTOR(384)
);

CREATE INDEX IF NOT EXISTS idx_code_units_repository_path
ON code_units(repository_path);