# Supabase Database Setup

## Project Details
- **URL:** `https://wkwgxhdtexjpqleuzyem.supabase.co`
- **Project Ref:** `wkwgxhdtexjpqleuzyem`
- **Region:** EU West (Frankfurt)

## Connection

### Option A: Transaction Pooler (recommended — no IP allowlist)
No Supabase IP allowlist required. Works from any network.

```
postgresql+asyncpg://postgres.wkwgxhdtexjpqleuzyem:<password>@aws-1-eu-west-1.pooler.supabase.com:5432/postgres
```

Get password: Supabase Dashboard → Project Settings → Database → Connection password.

### Option B: Direct Connection (requires IP allowlist)
Add your IP to: Database → Connection params → Network restrictions.

```
postgresql+asyncpg://postgres:<password>@db.wkwgxhdtexjpqleuzyem.supabase.co:5432/postgres
```

## Apply Schema

### CLI (preferred)
```bash
supabase link --project-ref wkwgxhdtexjpqleuzyem
supabase db push
```

### SQL Editor (alternative)
1. Open SQL Editor in Supabase Dashboard.
2. Paste `infrastructure/supabase/schema.sql`.
3. Run query.

## Tables (6)
| Table | Purpose |
|-------|---------|
| `customers` | Users/auth, subscription tiers |
| `refresh_tokens` | JWT refresh token tracking |
| `matches` | Match metadata (sport, teams, status) |
| `events` | Detected events (scrums, tackles, tries) |
| `transactions` | Payment history (Stripe, M-Pesa) |
| `match_tracks` | Player/ball tracking data per frame |

All tables have RLS enabled with policies restricting access to the customer's own data.

## Verify
```bash
# Test async connection
python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
e = create_async_engine('postgresql+asyncpg://postgres.wkwgxhdtexjpqleuzyem:<password>@aws-1-eu-west-1.pooler.supabase.com:5432/postgres')
async with e.connect() as c:
    print('Connected OK')
"
```
