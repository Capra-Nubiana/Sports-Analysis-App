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

### Payments (Stripe + M-Pesa)

| Provider | Required Env Vars | Notes |
|----------|-------------------|-------|
| **Stripe** | `STRIPE_SECRET_KEY` | Live/secret key from [Stripe Dashboard](https://dashboard.stripe.com/apikeys) |
| **M-Pesa** | `MPESA_CONSUMER_KEY`, `MPESA_CONSUMER_SECRET`, `MPESA_SHORTCODE`, `MPESA_PASSKEY` | Safaricom [Daraja API](https://developer.safaricom.co.ke) credentials |

**Status:** Mock implementations in Phase 5 (in progress). Payment routes not yet wired into the FastAPI backend. Set env vars in `.env` or Render dashboard (sync: false in `render.yaml`) for when routes are implemented.

**Future webhook endpoints** (to be created in Phase 5):
- Stripe: `https://<app>.onrender.com/api/payments/stripe/webhook`
- M-Pesa: `https://<app>.onrender.com/api/payments/mpesa/callback`

## Development Phases

1. **Phase 1** — Core pipeline + wearable/laser ingestion
2. **Phase 2** — Event detection rules + highlight generation
3. **Phase 3** — FastAPI backend + React dashboard
4. **Phase 4** — GPU optimization + C++ inference engine
5. **Phase 5** — Monetization + subscription-based access ✅

## Development Workflow

- **Branch strategy:** Always create a `feature/*` branch off `develop`
- **Pre-commit hooks:** gitleaks (secret scan), pytest (58 tests), mypy, ruff
- **Lint/type checks:** `mypy src/` and `ruff check src/ tests/`
- **Run API:** `.venv/bin/python -m src.api.main`
- **Train model:** Use `dashboard/train_sports_model.ipynb` in Colab

## License

AGPLv3 — see [LICENSE](LICENSE) file. Note: YOLOv8 is AGPL-3.0 licensed by Ultralytics; obtain a commercial license for commercial deployments.
