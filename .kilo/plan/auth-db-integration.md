# Auth & DB Integration Plan

## Reference: kioskpay-backend patterns
- **Database:** Supabase PostgreSQL with pgcrypto + uuid-ossp extensions
- **Connection:** HikariCP pool (Python equivalent: SQLAlchemy async engine)
- **Migrations:** Flyway → Alembic (Python equivalent)
- **Auth:** JWT access/refresh tokens, rate-limited endpoints
- **Admin:** `ADMIN_EMAILS` env var for admin auto-promotion
- **Infra:** Terraform for Supabase resources

## Implementation Plan

### Phase 1: Database Layer
- [ ] `src/core/database/` — SQLAlchemy models, session, alembic migrations
- [ ] Schema: customers, refresh_tokens, matches, events, transactions
- [ ] Supabase extensions: pgcrypto, uuid-ossp
- [ ] `docker-compose.yml` for local PostgreSQL

### Phase 2: Authentication Routes
- [ ] `src/api/routes/auth.py` — /register, /login, /refresh, /logout
- [ ] JWT access tokens (15 min), refresh tokens (7 days)
- [ ] Password hashing: bcrypt
- [ ] Admin auto-promotion via ADMIN_EMAILS env var
- [ ] Rate limiting on auth-sensitive endpoints

### Phase 3: Integrate with Existing Subscription Logic
- [ ] Replace in-memory `app.state.store.customers` with database-backed Customer model
- [ ] Persist matches_processed in DB
- [ ] Transaction records for payment history

### Phase 4: Infrastructure (Render + Doppler + Supabase)
- [ ] `render.yaml` — Render config (free tier, staging + production services)
- [ ] `docker-compose.yml` — local PostgreSQL + API for development
- [ ] `.doppler.toml` — Doppler config for secrets rotation
- [ ] `infrastructure/` — Terraform for Supabase resources (mirrors kioskpay pattern)
- [ ] Local HDD storage: `/mnt/data/videos` for media, `/mnt/data/processed` for outputs
  - GDPR: encrypt at rest, retention period 90 days, user deletion triggers cleanup
- [ ] `privacy-policy.md` — GDPR compliance (data categories, retention, user rights)

### Environment Variables
- `DATABASE_URL` — Supabase PostgreSQL connection string
- `JWT_SECRET` — 32+ char secret for token signing (Doppler-managed)
- `ADMIN_EMAILS` — comma-separated admin emails for auto-promotion
- `STORAGE_PATH` — local HDD path for media files (default: `/mnt/data/videos`)
- `RETENTION_DAYS` — auto-delete processed data after N days (GDPR default: 90)

## Verification
- All 58 existing tests must continue passing
- New auth tests: signup, login, token refresh, rate limiting
- mypy + ruff clean
- GDPR check: data deletion endpoint works
