-- Run in a PostgreSQL database with pgvector installed; adjust privileges per environment.
CREATE SCHEMA IF NOT EXISTS rag;
CREATE TABLE IF NOT EXISTS rag.source_documents (
 source_type text NOT NULL, source_id text NOT NULL, version bigint NOT NULL,
 status text NOT NULL CHECK (status IN ('draft','approved','test_only','archived')),
 content jsonb NOT NULL, content_hash text NOT NULL,
 valid_from timestamptz, valid_to timestamptz,
 updated_at timestamptz NOT NULL, indexed_at timestamptz,
 sync_status text NOT NULL DEFAULT 'pending',
 PRIMARY KEY (source_type,source_id)
);
CREATE TABLE IF NOT EXISTS rag.sync_events (
 event_id uuid PRIMARY KEY, source_type text NOT NULL, source_id text NOT NULL,
 source_version bigint NOT NULL, received_at timestamptz NOT NULL DEFAULT now(),
 processed_at timestamptz, error text
);
-- Vector dimension must match BGE-M3 dense output; set index strategy after benchmarks.
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS rag.document_chunks (
 chunk_id text PRIMARY KEY, source_type text NOT NULL, source_id text NOT NULL,
 source_version bigint NOT NULL, section_id text NOT NULL, content text NOT NULL,
 metadata jsonb NOT NULL, dense_embedding vector(1024),
 is_active boolean NOT NULL DEFAULT false,
 FOREIGN KEY (source_type,source_id) REFERENCES rag.source_documents(source_type,source_id)
);
CREATE INDEX IF NOT EXISTS idx_rag_active_chunks ON rag.document_chunks(source_type,source_id) WHERE is_active;
-- BGE-M3 sparsevec mapping/index to be added after validating token IDs and dimensions.
