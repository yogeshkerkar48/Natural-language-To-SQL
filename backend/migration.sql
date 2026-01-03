-- Migration script to add schema_hash column to query_history table
-- Run this on your PostgreSQL server

ALTER TABLE query_history ADD COLUMN IF NOT EXISTS schema_hash VARCHAR(64);
CREATE INDEX IF NOT EXISTS ix_query_history_schema_hash ON query_history (schema_hash);
