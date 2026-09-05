-- ============================================================
-- Auth & Payments Migration
-- ============================================================
-- Adds columns for JWT auth, OAuth linking, biometric auth,
-- phone/email verification, and device tracking.
-- ============================================================

-- ── Customers: password, OAuth, biometric, verification ──
ALTER TABLE customers
    ADD COLUMN IF NOT EXISTS password_hash TEXT,
    ADD COLUMN IF NOT EXISTS google_id TEXT UNIQUE,
    ADD COLUMN IF NOT EXISTS full_name TEXT,
    ADD COLUMN IF NOT EXISTS phone_number TEXT,
    ADD COLUMN IF NOT EXISTS phone_hash TEXT UNIQUE,
    ADD COLUMN IF NOT EXISTS biometric_public_key TEXT,
    ADD COLUMN IF NOT EXISTS email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN NOT NULL DEFAULT FALSE;

-- ── Refresh tokens: device tracking ──
ALTER TABLE refresh_tokens
    ADD COLUMN IF NOT EXISTS device_name TEXT,
    ADD COLUMN IF NOT EXISTS token_type TEXT NOT NULL DEFAULT 'refresh';

-- ── Indexes for faster lookups ──
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_hash ON refresh_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_customers_google_id ON customers(google_id);
CREATE INDEX IF NOT EXISTS idx_customers_phone_hash ON customers(phone_hash);
