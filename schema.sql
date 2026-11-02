CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS code_units (
    id SERIAL PRIMARY KEY,

    repository_path TEXT NOT NULL,

    name TEXT NOT NULL,
    filepath TEXT NOT NULL,
    start_line INTEGER,
    end_line INTEGER,

    scope_path TEXT[],
    scope_text TEXT,

    docstring TEXT,
    source_code TEXT,

    lexical_name TEXT,
    lexical_scope TEXT,
    lexical_docstring TEXT,
    lexical_source TEXT,

    embedding VECTOR(384),

    search_vector tsvector GENERATED ALWAYS AS (
        setweight(
            to_tsvector('simple', coalesce(lexical_name, '')),
            'A'
        )
        ||
        setweight(
            to_tsvector('simple', coalesce(lexical_scope, '')),
            'B'
        )
        ||
        setweight(
            to_tsvector('simple', coalesce(lexical_docstring, '')),
            'C'
        )
        ||
        setweight(
            to_tsvector('simple', coalesce(lexical_source, '')),
            'D'
        )
    ) STORED
);

CREATE INDEX IF NOT EXISTS idx_code_units_repository_path
ON code_units(repository_path);

CREATE INDEX IF NOT EXISTS idx_code_units_search_vector
ON code_units
USING GIN(search_vector);