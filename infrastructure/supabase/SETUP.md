# Supabase Database Setup Guide

## 1. Get Your Project Details
- Log into [supabase.com](https://supabase.com/dashboard)
- Open project: `wkwgxhdtexjpqleuzyem`
- Dashboard → Project Settings → Database

## 2. Two Connection Options

### Option A: Direct Connection (port 5432)
- Requires IP allowlisting
- Go to: DATABASE → Connection params → Add networking (0.0.0.0/0)
- Connection string format:
  `postgresql+asyncpg://postgres:<password>@db.wkwgxhdtexjpqleuzyem.supabase.co:5432/postgres`

### Option B: Transaction Pooler (port 6543)
- No IP allowlist required
- Go to: DATABASE → Connection pooler → Copy URI
- Connection string format:
  `postgresql+asyncpg://postgres.wkwgxhdtexjpqleuzyem:<password>@aws-1-eu-west-3.pooler.supabase.co:6543/postgres`

## 3. Apply Schema
- Go to: SQL Editor → New query
- Paste contents of `infrastructure/supabase/schema.sql`
- Run the query

## 4. Verify
```bash
# Check .env is set up
cat .env | grep DATABASE_URL

# Test connection
python -c "
import os; os.environ['DATABASE_URL']='postgresql+asyncpg://...'
from src.core.database.database import get_session
# Should not error
"
```
