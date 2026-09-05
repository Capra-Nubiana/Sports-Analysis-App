-- ============================================================
-- Auth Migration Fix — Timezone-aware timestamps
-- ============================================================
-- The expires_at column on refresh_tokens was TIMESTAMP WITHOUT
-- TIME ZONE, but AuthService issues timezone-aware datetimes.
-- PostgreSQL silently truncates the timezone, causing
-- "can't subtract offset-naive and offset-aware datetimes" errors.
-- ============================================================

ALTER TABLE refresh_tokens
    ALTER COLUMN expires_at TYPE TIMESTAMPTZ USING expires_at AT TIME ZONE 'UTC';
