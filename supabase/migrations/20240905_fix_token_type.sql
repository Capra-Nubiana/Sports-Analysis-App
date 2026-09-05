-- ============================================================
-- Auth Migration Fix — Add token_type column
-- ============================================================
-- The initial auth migration (20240910) was missing the token_type
-- column on refresh_tokens. This migration adds it with a safe
-- default.
-- ============================================================

ALTER TABLE refresh_tokens
    ADD COLUMN IF NOT EXISTS token_type TEXT NOT NULL DEFAULT 'refresh';
