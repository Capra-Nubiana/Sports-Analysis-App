-- ============================================================
-- Sports Analysis App — Supabase Database Schema
-- ============================================================
-- Run this in Supabase SQL Editor (or psql) to set up the schema.
-- Extensions: pgcrypto (for JWT hashing), uuid-ossp (for UUID generation)
-- ============================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- Customers / Auth
-- ============================================================
CREATE TABLE IF NOT EXISTS customers (
    customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    tier TEXT NOT NULL DEFAULT 'free' CHECK (tier IN ('free', 'basic', 'pro')),
    stripe_customer_id TEXT,
    mpesa_phone_number TEXT,
    matches_processed INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- Refresh Tokens
-- ============================================================
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(customer_id) ON DELETE CASCADE,
    token_hash TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    replaced_by UUID REFERENCES refresh_tokens(id)
);

-- ============================================================
-- Matches
-- ============================================================
CREATE TABLE IF NOT EXISTS matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(customer_id),
    sport_type TEXT NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    teams JSONB,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'complete', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- Events (detected during analysis)
-- ============================================================
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID REFERENCES matches(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    timestamp FLOAT NOT NULL,
    frame_id INTEGER,
    confidence FLOAT,
    players_involved UUID[],
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- Transactions (payment history)
-- ============================================================
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(customer_id),
    amount_cents INTEGER NOT NULL,
    currency TEXT NOT NULL DEFAULT 'usd',
    status TEXT NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    provider TEXT NOT NULL CHECK (provider IN ('stripe', 'mpesa')),
    provider_reference TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- Player Tracking Data (stored per match)
-- ============================================================
CREATE TABLE IF NOT EXISTS match_tracks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID REFERENCES matches(id) ON DELETE CASCADE,
    track_id INTEGER NOT NULL,
    frame_number INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    confidence FLOAT NOT NULL,
    x REAL NOT NULL,
    y REAL NOT NULL,
    width REAL NOT NULL,
    height REAL NOT NULL,
    team_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- Indexes for performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_customer ON refresh_tokens(customer_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires ON refresh_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_matches_customer ON matches(customer_id);
CREATE INDEX IF NOT EXISTS idx_matches_created_at ON matches(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_match ON events(match_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_match_tracks_match_frame ON match_tracks(match_id, frame_number);
CREATE INDEX IF NOT EXISTS idx_match_tracks_match_track ON match_tracks(match_id, track_id);

-- ============================================================
-- Row Level Security (RLS) — customer data isolation
-- ============================================================
-- Enable RLS on all customer-data tables
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE match_tracks ENABLE ROW LEVEL SECURITY;
ALTER TABLE refresh_tokens ENABLE ROW LEVEL SECURITY;

-- Allow users to access only their own data
CREATE POLICY "customers access own data" ON customers
    FOR SELECT USING (auth.uid()::text = customer_id::text OR role = 'admin');

CREATE POLICY "matches access own data" ON matches
    FOR ALL USING (customer_id IN (
        SELECT c.customer_id::text FROM customers c
        WHERE c.customer_id::text = auth.uid()::text OR c.role = 'admin'
    ));

CREATE POLICY "events access own matches" ON events
    FOR ALL USING (match_id IN (
        SELECT m.id::text FROM matches m
        JOIN customers c ON m.customer_id::text = c.customer_id::text
        WHERE c.customer_id::text = auth.uid()::text OR c.role = 'admin'
    ));

CREATE POLICY "transactions access own data" ON transactions
    FOR ALL USING (customer_id::text = auth.uid()::text OR customer_id IN (
        SELECT c.customer_id FROM customers c WHERE c.role = 'admin'
    ));
