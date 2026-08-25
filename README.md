# 🏟️ Sports Analysis & Highlight Generation App

A multi-sport video analysis platform that ingests full match footage alongside wearable sensor data and laser/LiDAR measurements, detects key events, and automatically generates highlight reels.

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
├── detection/     # YOLO detection, ByteTrack tracking, team classification
├── spatial/       # Pitch/court homography, zones
├── biometrics/    # HR, metabolic power, impact analysis
├── events/        # Sport-specific event detection (Phase 2)
├── highlights/    # Clip extraction & highlight assembly (Phase 2)
├── analytics/     # Post-match statistics & reports (Phase 3)
└── api/           # FastAPI REST + WebSocket (Phase 3)
```

## Development Phases

1. **Phase 1** — Core pipeline + wearable/laser ingestion ← *Current*
2. **Phase 2** — Event detection rules + highlight generation
3. **Phase 3** — FastAPI backend + React dashboard
4. **Phase 4** — GPU optimization + C++ inference engine

## License

MIT
