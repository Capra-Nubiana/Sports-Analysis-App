# 🏟️ Sports Analysis & Highlight Generation App

A multi-sport video analysis platform that ingests full match footage alongside wearable sensor data and laser/LiDAR measurements, detects key events, and automatically generates highlight reels.

### Key Features
- **Real-time object detection** — YOLOv8 ONNX model for rugby (ball, player, referee)
- **Subscription-based access** — Tiered rate limiting (FREE/BASIC/PRO) with Stripe & M-Pesa integration
- **Live dashboard** — WebSocket-powered React frontend with player tracking and heatmaps

## Supported Sports
- ⚽ Football (Soccer)
- 🏉 Rugby Union
- 🏀 Basketball
- 🔌 Extensible to any sport via config

## Architecture

Built on **SOLID principles** with Protocol-based abstractions enabling:
- Swappable detection backends (YOLO, custom models)
- Pluggable data sources (video, BLE wearables, ANT+ sensors, LiDAR)
- Sport-specific configuration without code changes
- Dependency injection via factory pattern

### Data Sources
| Source | Tools | Data |
|:---|:---|:---|
| Video | OpenCV, YOLO, ByteTrack | Player/ball detection, tracking |
| Wearables | fitdecode, Bleak, openant, SKDH | GPS, IMU, HR, HRV |
| LiDAR | Open3D, LasPy, PDAL | 3D point clouds, distance |
| Audio | Librosa | Crowd noise spikes |

## Quick Start

```bash
# Clone and setup
cd "Sports Analysis App"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Download YOLO weights
python scripts/download_models.py

# Analyze a match
python -m src.core.pipeline --video match.mp4 --sport football

# Run tests
pytest tests/ -v
```

## Project Structure

```
src/
├── core/          # SOLID abstractions, pipeline, models, factory
├── ingest/        # Video, wearable, and laser data ingestion
├── detection/     # YOLO detection (ONNX Runtime), ByteTrack tracking, team classification
├── spatial/       # Pitch/court homography, zones
├── biometrics/    # HR, metabolic power, impact analysis
├── events/        # Sport-specific event detection (scrums, tackles, tries)
├── highlights/    # Clip extraction & highlight assembly
├── analytics/     # Post-match statistics & reports (heatmaps, distance, sprint)
├── payments/      # Subscription tiers, payment gateways (Stripe, M-Pesa)
└── api/           # FastAPI REST + WebSocket backend
dashboard/
├── src/           # React + TypeScript dashboard
├── train_sports_model.ipynb  # Colab notebook for model training
└── train_sports_model.py     # CLI helper for training
```

## Setup

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

### Database (Supabase)

The project uses Supabase PostgreSQL. Two connection methods:

| Method | Host | Port | IP Allowlist |
|--------|------|------|-------------|
| Direct | `db.<ref>.supabase.co` | 5432 | Required |
| Pooler | `aws-1-<region>.pooler.supabase.com` | 5432 | None |

Set `DATABASE_URL` in `.env`:

```bash
DATABASE_URL=postgresql+asyncpg://postgres.<ref>:<password>@aws-1-<region>.pooler.supabase.com:5432/postgres
```

Apply the schema (first time only):

```bash
supabase link --project-ref <your-ref>
supabase db push
```

### Authentication

JWT-based auth following kioskpay-backend patterns:

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/auth/register` | POST | Public | Email + password signup |
| `/api/v1/auth/login` | POST | Public | Email + password login |
| `/api/v1/auth/google` | POST | Public | Google OAuth sign-in/up |
| `/api/v1/auth/refresh` | POST | Public | Refresh access token |
| `/api/v1/auth/logout` | POST | JWT | Revoke refresh token |
| `/api/v1/auth/forgot-password` | POST | Public | Send reset OTP |
| `/api/v1/auth/reset-password` | POST | Public | Reset with OTP |
| `/api/v1/auth/profile` | GET/PUT | JWT | Get/update profile |
| `/api/v1/auth/password` | PUT | JWT | Change password |
| `/api/v1/auth/account` | DELETE | JWT | Delete account |
| `/api/v1/auth/biometric/*` | GET/POST | JWT | Challenge, register, login |

**Token pairs:** Access (15 min) + Refresh (7 days). Refresh tokens are SHA-256 hashed before storage. Admins auto-promoted from `ADMIN_EMAILS` on every token issuance.

### Payments (Stripe + M-Pesa)

| Provider | Required Env Vars | Notes |
|----------|-------------------|-------|
| **Stripe** | `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | [Stripe Dashboard](https://dashboard.stripe.com/apikeys) |
| **M-Pesa** | `MPESA_CONSUMER_KEY`, `MPESA_CONSUMER_SECRET`, `MPESA_SHORTCODE`, `MPESA_PASSKEY` | [Safaricom Daraja API](https://developer.safaricom.co.ke) |

**Status:** Real implementations using `stripe` and `requests` SDKs.

**Webhook endpoints:**
- Stripe: `POST /api/v1/payments/stripe/webhook`
- M-Pesa: `POST /api/v1/payments/mpesa/callback`

## Development Phases

1. **Phase 1** — Core pipeline + wearable/laser ingestion
2. **Phase 2** — Event detection rules + highlight generation
3. **Phase 3** — FastAPI backend + React dashboard
4. **Phase 4** — GPU optimization + C++ inference engine
5. **Phase 5** — Monetization + subscription-based access ✅

## Development Workflow

- **Branch strategy:** Always create a `feature/*` branch off `develop`
- **Pre-commit hooks:** gitleaks (secret scan), pytest, mypy, ruff
- **Lint/type checks:** `mypy src/` and `ruff check src/ tests/`
- **Run API:** `.venv/bin/python -m src.api.main`
- **Train model:** Use `dashboard/train_sports_model.ipynb` in Colab

## License

AGPLv3 — see [LICENSE](LICENSE) file. Note: YOLOv8 is AGPL-3.0 licensed by Ultralytics; obtain a commercial license for commercial deployments.
