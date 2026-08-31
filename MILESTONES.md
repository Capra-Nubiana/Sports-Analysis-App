# Project Milestones & Architecture Reference

A comprehensive reference for the Sports Analysis App — its architecture, completed milestones, and roadmap.

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture Principles](#2-architecture-principles)
3. [Phase 1 — Core Pipeline + Wearables + Laser (Complete)](#3-phase-1--core-pipeline--wearables--laser-complete)
4. [Phase 2 — Event Detection & Highlights (Complete)](#4-phase-2--event-detection--highlights-complete)
5. [Phase 3 — API & Analytics (Complete)](#5-phase-3--api--analytics-complete)
6. [Phase 4 — Optimization (Complete)](#6-phase-4--optimization-complete)
7. [Phase 5 — Dashboard (Complete)](#5-phase-5--dashboard-complete)
8. [Setup & Verification](#7-setup--verification)

---

## 1. Project Overview

A multi-sport video analysis platform that ingests full match footage alongside
wearable sensor data and LiDAR measurements, detects key events, and
generates highlight reels.

**Supported Sports:** Football (soccer), Rugby Union, Basketball. Extensible
to any sport via YAML configuration without code changes.

**Key Integrations:**

| Layer | Libraries | Purpose |
|-------|-----------|---------|
| Detection | Ultralytics YOLO, Supervision | Player/ball/referee detection |
| Tracking | ByteTrack (via supervision) | Multi-object persistent tracking |
| Wearables | fitdecode, Bleak, openant, SKDH | GPS, IMU, HR, HRV, ANT+ data |
| LiDAR | Open3D, LasPy, PDAL | 3D point cloud ingestion and processing |
| Biometrics | PhysioDSP, Floodlight | HRV, metabolic power, impact analysis |
| Config | PyYAML, Pydantic | YAML loading + typed models |

---

## 2. Architecture Principles

The codebase follows SOLID principles with Protocol-based abstractions:

| Principle | Application |
|-----------|-------------|
| **S** — Single Responsibility | Detector detects, Tracker tracks, TeamClassifier classifies — no god classes |
| **O** — Open/Closed | ABCs/Protocols (DataSource, Detector, Tracker) allow new sensors/sports without modifying existing code |
| **L** — Liskov Substitution | VideoSource, FITParser, LiDARSource are interchangeable through DataSource protocol |
| **I** — Interface Segregation | Separate protocols: Detectable, Trackable, Measurable, Streamable |
| **D** — Dependency Inversion | Pipeline depends on abstractions, not concrete implementations; injected via factory |

**Additional Patterns:**
- **Strategy** — Swappable detection/tracking backends (YOLO, ByteTrack, BoT-SORT)
- **Observer** — Progress callbacks during pipeline iteration
- **Factory** — Sport-specific component creation via `ComponentFactory`
- **Repository** — Data access abstraction through DataSource protocol

---

## 2.1 Tech Stack

### Language & Runtime
- **Python 3.10+** (developed and tested on 3.12)
- Package management: `pip` with `pyproject.toml` (PEP 621) + `requirements.txt` mirror

### Detection & Tracking
| Tool | Version | Purpose | License |
|------|---------|---------|---------|
| Ultralytics YOLO | >=8.2 | Player/ball/referee detection | AGPL-3.0 |
| Supervision | >=0.21 | ByteTrack tracking, annotations, zones | MIT |
| OpenCV | >=4.9 (opencv-python-headless) | Frame I/O, homography, contour/zone testing | Apache-2.0 |
| scikit-learn | >=1.3 | K-Means jersey color clustering | BSD-3 |
| MediaPipe/MMPose | (future) | Pose estimation | Apache-2.0 |

### Wearable Data Ingestion
| Tool | Version | Purpose | License |
|------|---------|---------|---------|
| fitdecode | >=0.10 | Parse Garmin/ANT+ `.FIT` files | MIT |
| Bleak | >=0.21 | BLE device communication (live streaming) | MIT |
| openant | >=1.3 | ANT+ protocol (HR straps, speed sensors) | MIT |
| SKDH | >=0.14 | IMU pipeline processing, gait/activity metrics | MIT |
| PhysioDSP | | ECG/HRV biometric signal processing | MIT |
| Floodlight | >=0.4 | Sports tracking, metabolic power, kinematics | MIT |

### Laser / LiDAR
| Tool | Version | Purpose | License |
|------|---------|---------|---------|
| Open3D | >=0.18 | 3D point cloud processing, visualization, segmentation | MIT |
| LasPy | >=2.5 | Read/write LAS/LAZ LiDAR files | BSD-2 |
| PDAL | (conda) | Point cloud pipeline processing (ground filtering) | BSD |

### Video & Audio Processing
| Tool | Version | Purpose | License |
|------|---------|---------|---------|
| MoviePy | >=1.0 | Clip extraction, highlight assembly | MIT/LGPL |
| FFmpeg | (system) | Video encoding/transcoding | LGPL |
| LibROSA | >=0.10 | Crowd noise spike detection | ISC |
| PyTorch | >=2.0 | Custom model training (Phase 4) | BSD |

### Data Models & Config
| Tool | Version | Purpose |
|------|---------|---------|
| Pydantic | >=2.0 | Data validation, models with JSON serialization |
| PyYAML | >=6.0 | YAML config loading with deep-merge |
| NumPy | >=1.24 | Numerical arrays, point cloud math |
| SciPy | >=1.11 | Signal processing primitives |

### API & Dashboard (Phase 3)
| Tool | Version | Purpose |
|------|---------|---------|
| FastAPI | >=0.100 | REST API backend |
| Uvicorn | >=0.23 | ASGI server |
| WebSockets | >=11.0 | Real-time streaming |
| React + Vite | (separate Node project) | Frontend dashboard |

### Dev Tools & CI/CD
| Tool | Version | Purpose |
|------|---------|---------|
| pytest | >=7.0 | Testing framework |
| pytest-asyncio | >=0.21 | Async test support |
| pytest-cov | >=4.0 | Coverage reporting |
| Ruff | >=0.1 | Linting + formatting |
| Black | >=23.0 | Code formatting |
| Mypy | >=1.5 | Static type checking |
| Gitleaks | | Secret scanning (pre-commit + CI) |
| GitHub Actions | | CI pipelines (ci.yml, deploy.yml) |

---

## 3. Phase 1 — Core Pipeline + Wearables + Laser (Complete)

Status: **Complete** ✓

### 3.1 SOLID Core Abstractions (`src/core/`)

| File | Description | Status |
|------|-------------|--------|
| `protocols.py` | Protocol/ABC definitions: DataSource, SourceFrame, Detectable, Trackable, Detector, Tracker, EventDetector, Measurable. All decorated with `@runtime_checkable` for `isinstance()` checks. | Complete |
| `factory.py` | Dependency Injection container. `ComponentFactory` creates sport-specific components (VideoSource, YOLODetector, ByteTrackerWrapper, KMeansTeamClassifier) from config. | Complete |
| `models.py` | Pydantic models: Detection, TrackedDetection, SensorReading, Player, Event, Match with full JSON serialization. | Complete |
| `sport_config.py` | YAML loader with deep-merge of `base.yaml` + sport-specific config (football, rugby, basketball). Dot-notation `get()` access. | Complete |
| `pipeline.py` | Orchestrator consuming only abstract interfaces. DI via factory, type-narrowed frame access via `cast()`. | Complete |

### 3.2 Data Ingestion (`src/ingest/`)

| File | Description | Status |
|------|-------------|--------|
| `video_source.py` | OpenCV `VideoCapture` wrapper implementing DataSource. Yields `VideoFrame` with image + timestamp. | Complete |
| `sync.py` | Time synchronization engine. UTC-based timestamp alignment between video and sensor readings with temporal windowing. | Complete |
| `wearable/fit_parser.py` | Garmin/ANT+ `.FIT` file parsing via `fitdecode`. Yields `FITFrame` with `SensorReading` objects. | Complete |
| `wearable/ble_stream.py` | Live BLE streaming via `Bleak`. Async `BLEStreamer` with notification callbacks for HR data. | Complete |
| `wearable/ant_stream.py` | ANT+ device streaming via `openant`. Supports HR strap devices. | Complete |
| `wearable/polar_stream.py` | Polar BLE device stub with ECG streaming capability. | Complete |
| `wearable/imu_processor.py` | IMU signal processing via SKDH. Gait metrics and high-G impact detection. | Complete |
| `laser/lidar_source.py` | LiDAR point cloud ingestion via Open3D. Streams `.pcd`/`.ply` files as `LiDARFrame` objects. | Complete |
| `laser/point_cloud.py` | Point cloud processing via PDAL (SMRF ground filtering) and LasPy (LAS/LAZ reading). | Complete |
| `laser/laser_tracker.py` | DBSCAN clustering and object tracking from 3D point cloud data. | Complete |

### 3.3 Detection Layer (`src/detection/`)

| File | Description | Status |
|------|-------------|--------|
| `detector.py` | YOLO wrapper implementing Detector protocol. Graceful fallback when ultralytics/torch unavailable. Device auto-selection (CUDA → CPU). | Complete |
| `tracker.py` | ByteTrack wrapper via Supervision implementing Tracker protocol. Converts between abstract Detection and sv.Detections. | Complete |
| `team_classifier.py` | K-Means jersey color clustering. Green masking to exclude pitch/court. Dynamic fitting after 50 player crops. | Complete |

### 3.4 Spatial Mapping (`src/spatial/`)

| File | Description | Status |
|------|-------------|--------|
| `homography.py` | Perspective transform mapper (pixel → metric coordinates). Calibrate via src/dst point pairs. | Complete |
| `keypoint_detector.py` | Pitch/court keypoint stub for automated homography calibration. | Complete |
| `zones.py` | Sport-specific zone management with polygon point-inclusion testing via OpenCV. | Complete |

### 3.5 Biometrics (`src/biometrics/`)

| File | Description | Status |
|------|-------------|--------|
| `heart_rate.py` | HR/HRV analysis via PhysioDSP. Fallback stats (avg/max HR) when only BPM data available. | Complete |
| `metabolic.py` | Metabolic power via Floodlight XY tracking data. Velocity/acceleration computation stub. | Complete |
| `impact.py` | G-force/impact detection from IMU accelerometer magnitude. | Complete |
| `fatigue.py` | Fatigue index (0–1) from HR ratio + motion intensity. Rolling fatigue over time windows. | Complete |

### 3.6 Configuration (`config/`)

| File | Description |
|------|-------------|
| `base.yaml` | Shared defaults: video settings, detection thresholds, tracking params, wearable config, output format |
| `football.yaml` | Football-specific: pitch dimensions (105×68m), zones (goal/penalty areas), event rules (goal, pass) |
| `rugby.yaml` | Rugby-specific: pitch (100×70m), try zones, tackle/scrum detection rules, higher G-force threshold |
| `basketball.yaml` | Basketball-specific: court dimensions (28.65×15.24m), hoop positions, 3-point line, LiDAR config |

### 3.7 Scripts (`scripts/`)

| File | Description |
|------|-------------|
| `download_models.py` | Downloads YOLO weights (yolov8x.pt, yolo11x.pt) with progress reporting and skip-if-exists |
| `benchmark.py` | Inference and pipeline throughput benchmarking |

### 3.8 Tests (`tests/`) — 16 tests, all passing

| File | Tests | Coverage |
|------|-------|----------|
| `test_protocols.py` | 5 | Protocol conformance (DataSource, Detector, Tracker, Detectable, Trackable) via `isinstance()` |
| `test_models.py` | 2 | Pydantic model creation, serialization, Match JSON export |
| `test_config.py` | 2 | SportConfig loading, deep-merge, dot-notation defaults |
| `test_detector.py` | 2 | YOLODetector init + empty detection graceful fallback |
| `test_tracker.py` | 2 | ByteTrackerWrapper init + empty update graceful fallback |
| `test_ingest.py` | 2 | FITParser invalid file handling, iter_frames RuntimeError |
| `test_sync.py` | 1 | Synchronizer offset calibration and temporal windowing |

### 3.9 CI/CD (`.github/workflows/`)

| File | Triggers | Behavior |
|------|----------|----------|
| `ci.yml` | PR to develop/main, push to feature/* and develop | Runs gitleaks secret scan (direct `gitleaks detect` command to handle force-push), black format check, pytest. Enforces linear merge: feature/* → develop, develop → main only |
| `deploy.yml` | Push to main, manual dispatch | Production deployment stub with branch verification |

---

## 4. Phase 2 — Event Detection & Highlights (Complete)

Status: **Complete** ✓

### 4.1 Event Detection (`src/events/`)

| File | Description |
|------|-------------|
| `base.py` | `BaseEventDetector` abstract class: shared state tracking, ball/player filtering, spatial lookups, cooldown management |
| `football.py` | `FootballEventDetector` — detects goals (ball in goal zone), passes (ball-to-player distance tracking) |
| `rugby.py` | `RugbyEventDetector` — detects tries (ball in try zone), tackles (velocity drop + proximity), scrums (player clustering), IMU impact flagging |
| `basketball.py` | `BasketballEventDetector` — detects scored baskets (ball near hoop center), three-pointers (shot distance + trajectory) |
| `factory.py` | `EventDetectorFactory` — sport-specific detector creation via registry dict |

**Sport event rule configs** (in `config/*.yaml`):
- Football: goal zones, pass distance thresholds (1.5m)
- Rugby: try zones, tackle overlap (1.0m) + velocity drop (70%), scrum density (8 players, 3.5m radius, 3s stationary), tackle G-force (8.0 G)
- Basketball: hoop positions (points), basket radius (0.5m), three-point distance (6.75m)

### 4.2 Highlight Generation (`src/highlights/`)

| File | Description |
|------|-------------|
| `scorer.py` | `HighlightScorer` — event importance weights, time-window clipping (2s pre + 3s post), overlap deduplication |
| `ffmpeg_extractor.py` | `ClipExtractor` — FFmpeg (primary) + MoviePy (fallback) clip extraction, concatenation into highlight reel |
| `audio_analyzer.py` | `AudioAnalyzer` — LibROSA RMS energy spike detection for crowd noise analysis |

**Default highlight weights:** goal=10, try=10, scored_basket=8, tackle=6, three_pointer=7, pass=2, scrum=3

### 4.3 Pipeline Integration

- `ComponentFactory.create_event_detector()` — instantiates sport-specific detector
- `Pipeline.__init__` — optional `generate_highlights` flag; auto-loads homography from config keypoints
- `Pipeline.run()` — detects events per frame, adds to `Match.events`
- `Pipeline.main()` — `--highlights` CLI flag for highlight reel generation
- `ZoneManager` — extended to handle both polygon zones and point zones (basketball hoops)

### 4.4 Tests — 13 new tests (29 total, all passing)

| File | Tests | Coverage |
|------|-------|----------|
| `test_events.py` | 7 | Factory registry, sport selection, football no-op, basketball ball detection, rugby IMU impacts, reset |
| `test_highlights.py` | 6 | Goal scoring, sorted events, window overlap filtering, max clips limit, clip extraction fallback, custom weights |

### 4.5 New Dependencies
- `librosa>=0.10` — audio spike detection (already in requirements.txt)
- `moviepy>=1.0` — clip extraction fallback (already in requirements.txt)

---

## 5. Phase 3 — API & Analytics (Complete)

Status: **Complete** ✓

### 5.1 REST API (`src/api/`)

| File | Description |
|------|-------------|
| `main.py` | FastAPI app factory, WebSocket `/ws/tracking` endpoint, CORS middleware |
| `app_state.py` | Shared `AppState` container (match data, WebSocket connections, sport config) |
| `routes/matches.py` | List/create/get matches, get match events |
| `routes/events.py` | List/get/add events |
| `routes/players.py` | List/get players, player heatmap data |
| `routes/highlights.py` | List highlight clips, generate reel, get highlight-scored timeline |
| `routes/websocket.py` | WebSocket route re-export |

**API Endpoints:**
- `GET /api/v1/matches/` — List saved timelines
- `POST /api/v1/matches/` — Register a Match object
- `GET /api/v1/matches/{id}` — Get match timeline JSON
- `GET /api/v1/matches/{id}/events` — Get match events
- `GET /api/v1/events/` — Get in-memory events
- `GET /api/v1/events/{id}` — Get specific event
- `POST /api/v1/events/` — Add event to current match
- `GET /api/v1/players/` — List tracked players
- `GET /api/v1/players/{id}` — Get player details
- `GET /api/v1/players/{id}/heatmap` — Player position heatmap
- `GET /api/v1/highlights/` — List highlight clips
- `GET /api/v1/highlights/reel` — Generate/retrieve highlight reel
- `GET /api/v1/highlights/timeline/{id}` — Get scored highlight windows
- `WS /ws/tracking` — Real-time tracking data stream

### 5.2 Analytics (`src/analytics/`)

| File | Description |
|------|-------------|
| `heatmap.py` | `HeatmapGenerator` — 2D position density heatmaps via numpy histogram2d |
| `distance.py` | `DistanceAnalyzer` — total distance, high-speed distance, avg/max speed |
| `sprint.py` | `SprintDetector` — sprint burst detection (speed threshold + min duration) |
| `report.py` | `AnalyticsReport` — aggregates all analytics into per-player reports |

### 5.3 CLI Usage

```bash
# Start API server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Or via project script
python -m src.api.main
```

### 5.4 New Dependencies
- `fastapi>=0.110` — web framework
- `uvicorn>=0.29` — ASGI server
- `websockets>=12.0` — WebSocket support

---

## 6. Phase 4 — Optimization (Complete)

Status: **Complete** ✓

### 6.1 GPU Batch Processing (`src/detection/batch_processor.py`)

| Component | Description |
|-----------|-------------|
| `BatchProcessor` | Accumulates frames into batches and runs YOLO inference in a single forward pass for GPU throughput optimization |

**Features:**
- Lazy model loading with CUDA/MPS/CPU detection
- `queue_frame()` — accumulates frames, returns detections when batch is full
- `flush()` — process all queued frames
- `detect_batch()` — run inference on multiple images simultaneously
- Batch size configurable (default: 8)

### 6.2 PyTorch Training Pipeline (`scripts/train_model.py`)

| Component | Description |
|-----------|-------------|
| `TrainingPipeline` | Fine-tunes YOLOv8/v11 on sport-specific datasets via Ultralytics API |

**Features:**
- `build_train_config()` — generates YAML training config from SportConfig
- `save_train_config()` — saves config to disk
- `train()` — full fine-tuning with configurable epochs, batch size, learning rate, patience
- `validate()` — post-training validation with mAP50, mAP, precision, recall metrics
- CLI interface with `--sport`, `--dataset`, `--model`, `--epochs`, `--batch-size`, `--img-size`, `--lr`

### 6.3 C++ Inference Engine (`cpp_inference/`)

| File | Description |
|------|-------------|
| `include/cpp_inference/detector.hpp` | C++ Detector class with ONNX Runtime/TensorRT stub |
| `src/detector.cpp` | Implementation skeleton (preprocess, inference, post-process with NMS) |
| `CMakeLists.txt` | CMake build configuration with OpenCV linking and Release optimizations |

### 6.4 Pre-existing Script Fixes

- `scripts/benchmark.py` — fixed `frame.image` access by casting to `VideoFrame` (resolves mypy attr-defined error)
- `scripts/download_models.py` — fixed `download_ultralytics_model` return type to `Path | None`, added exception handling

### 6.5 Tests — 9 new tests (53 total, all passing)

| File | Tests | Coverage |
|------|-------|----------|
| `test_batch_processor.py` | 5 | Init, no-model fallback, queue/flush, custom classes, device property |
| `test_training.py` | 4 | Pipeline init, config building, config saving, sport-specific configs |

---

## 5. Phase 5 — Dashboard (Complete)

Status: **Complete** ✓

### 5.1 Frontend (`dashboard/`)

| File | Description |
|------|-------------|
| `src/App.tsx` | Main router with 4 pages: Tracking, Events, Analytics, Highlights |
| `src/main.tsx` | React entry point with StrictMode |
| `src/index.css` | Tailwind CSS imports |
| `src/hooks/useWebSocket.ts` | WebSocket hook for real-time tracking data |
| `src/types/index.ts` | TypeScript type definitions |

**Pages:**
- `TrackingDashboard` — Live canvas-based field tracking with WebSocket
- `EventsPage` — Event timeline chart + data table
- `AnalyticsPage` — Player heatmaps, distance bar charts, sprint stats
- `HighlightsPage` — Highlight clip listing with reel support

**Components:**
- `TrackingCanvas` — HTML5 canvas field visualization with player positions
- `DistanceBarChart` — Chart.js bar chart for distance/speed metrics
- `EventTimeline` — Chart.js line chart for event confidence over time
- `PlayerHeatmap` — Grid-based position density visualization

**Tech Stack:**
- React 18 + TypeScript + Vite
- Tailwind CSS for styling
- Chart.js (via react-chartjs-2) for data visualization
- Native WebSocket API for real-time tracking

### 5.2 Integration

- Vite proxy configured for `/api` → `http://localhost:8000/api/v1/`
- WebSocket proxy for `/ws` → FastAPI WebSocket endpoint
- CI: Added `frontend-check` job (TypeScript type check + oxlint)
- `package.json` scripts: `dev`, `build`, `lint`, `preview`, `start`

### 5.3 CLI Usage

```bash
# Start API backend
uvicorn src.api.main:app --reload

# Start dashboard (dev)
cd dashboard && npm run dev

# Build dashboard (production)
cd dashboard && npm run build
```

### 5.4 Verification

| Check | Result |
|-------|--------|
| TypeScript tsc --noEmit | ✓ 0 errors |
| pytest (53 tests) | ✓ All passing |
| ruff check | ✓ Clean |
| black --check | ✓ Clean |
| mypy | ✓ 0 errors (63 files) |

---

## 7. Setup & Verification

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install dev tools (for linting/typechecking)
pip install ruff black mypy pytest pytest-asyncio

# Run tests
pytest tests/ -v

# Lint
ruff check src/ tests/ scripts/
ruff format --check src/ tests/ scripts/

# Type check
mypy src/ scripts/

# Format check
black --check src/ tests/ scripts/

# Smoke tests
python -c "from src.core.sport_config import SportConfig; print(SportConfig('football'))"
python -c "from src.core.factory import ComponentFactory; f = ComponentFactory('football'); print(f.create_detector())"
python -c "from src.events.factory import EventDetectorFactory; print(EventDetectorFactory.create('football', SportConfig('football')))"
python -c "from src.highlights.scorer import HighlightScorer; print(HighlightScorer())"
python -c "from src.highlights.ffmpeg_extractor import ClipExtractor; print(ClipExtractor('test.mp4'))"
python -c "from src.highlights.audio_analyzer import AudioAnalyzer; print(AudioAnalyzer())"
python -c "from src.api.main import app; print(app.title)"
python -c "from src.analytics.heatmap import HeatmapGenerator; print(HeatmapGenerator())"
python -c "from src.analytics.distance import DistanceAnalyzer; print(DistanceAnalyzer())"
python -c "from src.detection.batch_processor import BatchProcessor; print(BatchProcessor())"
```

**Verification status (Phase 1):**

| Check | Result |
|-------|--------|
| pytest (16 tests) | ✓ All passing |
| ruff check | ✓ Clean |
| ruff format --check | ✓ Clean |
| black --check | ✓ Clean |
| mypy src/ | ✓ 0 errors (37 files) |
| smoke: SportConfig | ✓ Config loads + merges |
| smoke: ComponentFactory | ✓ Creates detector with config |
| smoke: FatigueAnalyzer | ✓ Imports correctly |
| smoke: scripts package | ✓ Imports correctly |

**Verification status (Phase 2):**

| Check | Result |
|-------|--------|
| pytest (29 tests) | ✓ All passing |
| ruff check | ✓ Clean (57 files) |
| ruff format --check | ✓ Clean |
| black --check | ✓ Clean |
| mypy src/ scripts/ | ✓ 0 errors (45 files) |
| CI: gitleaks | ✓ Clean (direct gitleaks detect) |
| CI: pytest (GitHub Actions) | ✓ All passing |
| CI: branch routing | ✓ Pass (feature/* → develop only) |

**Verification status (Phase 3):**

| Check | Result |
|-------|--------|
| pytest (44 tests) | ✓ All passing |
| ruff check | ✓ Clean (72 files) |
| black --check | ✓ Clean |
| mypy src/ scripts/ | ✓ 0 errors (63 files) |

**Verification status (Phase 4):**

| Check | Result |
|-------|--------|
| pytest (53 tests) | ✓ All passing |
| ruff check | ✓ Clean (76 files) |
| black --check | ✓ Clean |
| mypy src/ scripts/ | ✓ 0 errors (63 files) |

### CLI Usage

```bash
# Basic analysis (tracking + event detection)
python -m src.core.pipeline --sport football --video input/match.mp4

# Analysis + highlight reel generation
python -m src.core.pipeline --sport football --video input/match.mp4 --highlights

# Download pre-trained YOLO weights
python scripts/download_models.py

# Benchmark inference throughput
python scripts/benchmark.py --model yolov8x.pt --video input/match.mp4 --frames 300

# Train a custom YOLO model (Phase 4)
python scripts/train_model.py --sport football --dataset /path/to/dataset --epochs 50

# Validate a trained model
python scripts/train_model.py --sport football --dataset /path/to/dataset --validate runs/train/best.pt

# Start REST API server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Appendix A — Colab Model Training Plan

A precise, step-by-step plan for acquiring data, training models in
Google Colab, and integrating results back into the Sports Analysis App.

### A.1. Prerequisites

- Google account with Colab Pro (recommended for GPU T4/V100 access)
- Kaggle API token (`kaggle.json`) — downloaded from
  `https://www.kaggle.com/my-account` → "Create New API Token"
- Google Drive quota (≥25 GB free for dataset + model checkpoints)
- Local development branch: `feature/phase4-models`

### A.2. Data Sources

| Dataset | Source | Size | Format | License | Colab Mount |
|---------|--------|------|--------|---------|-------------|
| **Football** | Kaggle: SoccerNet | ~12 GB | MP4 video, JSON annotations | MIT | `/content/drive/MyDrive/datasets/football/` |
| | Kaggle: Football Match Videos | ~5 GB | MP4, 720p | Custom | same |
| | Open Images V7 (soccer subset) | ~3 GB | JPEG, CSV | CC-BY 4.0 | same |
| **Rugby** | Kaggle: Rugby League Videos | ~2 GB | MP4 | Custom | `/content/drive/MyDrive/datasets/rugby/` |
| | Kaggle: Rugby Vision Dataset | ~500 MB | JPG, TXT (YOLO) | MIT | same |
| **Basketball** | Kaggle: NBA Player Tracking | ~3 GB | MP4, CSV (bbox/track) | Custom | `/content/drive/MyDrive/datasets/basketball/` |
| | OpenABI Basketball Dataset | ~800 MB | MP4, JSON | Apache-2.0 | same |
| **Generic Player Dataset** | Kaggle: Soccer Player Detection | ~500 MB | JPG, XML (VOC) | MIT | shared |

### A.3. Colab Notebook Workflow

#### Step 1 — Environment Setup (Cell 1)
```python
# Install dependencies
!pip install -q torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
!pip install -q ultralytics opencv-python-headless albumentations
!pip install -q kaggle pyyaml gdown

# Authenticate Kaggle
from pathlib import Path
import json

Path("/root/.kaggle").mkdir(exist_ok=True)
# Upload kaggle.json via file upload in Colab UI
# Then:
!cp /content/kaggle.json /root/.kaggle/kaggle.json
!chmod 600 /root/.kaggle/kaggle.json

# Mount Drive for checkpoints
from google.colab import drive
drive.mount("/content/drive")
```

#### Step 2 — Dataset Download (Cell 2)
```bash
# Download SoccerNet (football events)
!kaggle datasets download -d clementine3625/soccer-tracklab \
  -p /content/drive/MyDrive/datasets/football/ --unzip

# Download NBA tracking data (basketball)
!kaggle datasets download -d nba123/nba-player-tracking \
  -p /content/drive/MyDrive/datasets/basketball/ --unzip

# Download generic player detection (for transfer learning base)
!kaggle datasets download -d alessigottlieb/soccer-count-the-15637 \
  -p /content/datasets/player_detection/ --unzip
```

#### Step 3 — Data Preprocessing (Cells 3–5)
```python
# Convert annotations to YOLO format (VOC XML → YOLO TXT)
import xml.etree.ElementTree as ET
import os

SPORT_LABELS = {"person": 0, "ball": 32, "referee": 1, "goalkeeper": 2}
# Map sport-specific labels to YOLO class IDs (matching pyproject.toml "classes")
# football: 0=person, 32=ball, 1=referee, 2=goalkeeper
# rugby: 0=person, 32=ball, 1=referee
# basketball: 0=person, 32=ball

def voc_to_yolo(xml_path, output_dir):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    size = root.find("size")
    w, h = int(size.find("width").text), int(size.find("height").text)
    lines = []
    for obj in root.findall("object"):
        name = obj.find("name").text
        class_id = SPORT_LABELS.get(name, -1)
        if class_id == -1:
            continue
        bndbox = obj.find("bndbox")
        x1 = int(bndbox.find("xmin").text) / w
        y1 = int(bndbox.find("ymin").text) / h
        x2 = int(bndbox.find("xmax").text) / w
        y2 = int(bndbox.find("ymax").text) / h
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        bw = x2 - x1
        bh = y2 - y1
        lines.append(f"{class_id} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")
    # Write YOLO file
    ...

# Extract keyframes from videos at 2fps for training frames
!python -c "
import cv2, os
vid_dir = '/content/drive/MyDrive/datasets/football/videos'
out_dir = '/content/drive/MyDrive/datasets/football/frames'
os.makedirs(out_dir, exist_ok=True)
for i, f in enumerate(sorted(os.listdir(vid_dir))):
    cap = cv2.VideoCapture(os.path.join(vid_dir, f))
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret: break
        if frame_count % 50 == 0:  # ~2fps at 25fps source
            cv2.imwrite(f'{out_dir}/{f}_{frame_count}.jpg', frame)
        frame_count += 1
    cap.release()
"
```

#### Step 4 — Train YOLO Model (Cells 6–8)
```yaml
# /content/datasets/football/data.yaml
path: /content/drive/MyDrive/datasets/football
train: frames/train
val: frames/val
names:
  0: person
  1: referee
  2: goalkeeper
  32: ball
```

```python
from ultralytics import YOLO

# Start from yolov8x.pt pre-trained on COCO
model = YOLO("yolov8x.pt")

# Transfer learning: train on sport-specific data
results = model.train(
    data="/content/datasets/football/data.yaml",
    epochs=100,
    batch=16,
    imgsz=1280,
    patience=20,
    augment=True,
    mosaic=1.0,
    degrees=10.0,
    translate=0.1,
    scale=0.5,
    fliplr=0.5,
    project="/content/drive/MyDrive/models/football",
    name="yolov8x-football-v1",
    device="cuda",
    amp=True
)
```

#### Step 5 — Validate & Export (Cells 9–10)
```python
# Validate on held-out test set
metrics = model.val(data="/content/datasets/football/data.yaml")
print(metrics.box.map)  # mAP50-95

# Export to ONNX for cross-platform deployment
model.export(format="onnx", opset=12)
```

#### Step 6 — Upload Back to Project (Cell 11)
```python
# Upload to GCS bucket (for model serving)
!pip install -q google-cloud-storage
from google.cloud import storage

client = storage.Client.create_anonymous_client()
bucket = client.bucket("sports-analysis-models")
blob = bucket.blob("football/yolov8x-football-v1.onnx")
blob.upload_from_filename("/content/drive/MyDrive/models/football/yolov8x-football-v1.onnx")

# Or: copy from Drive to local repo (manual download via Colab UI)
# Download via: files.download from colab or gs:// path
```

### A.4. Integration Steps

1. **Pull models into project:**
   ```bash
   python scripts/download_models.py
   # Downloads yolov8x.pt from Ultralytics + custom models from GCS bucket
   ```

2. **Config wiring** (`config/football.yaml`):
   ```yaml
   detection:
     model_path: "models/yolov8x-football-v1.onnx"
     confidence_threshold: 0.35  # tuned from Colab validation
   ```

3. **Factory update** (`src/core/factory.py`):
   ```python
   def create_detector(self) -> Detector:
       from src.detection.detector import YOLODetector
       return YOLODetector(
           model_path=self.config.get("detection.model_path", "models/yolov8x.pt"),
           confidence=self.config.get("detection.confidence_threshold", 0.3),
           classes=self.config.get("detection.classes", [0, 32]),
       )
   ```

4. **Verify on sample video:**
   ```python
   python -m src.core.pipeline --sport football --video data/sample_match.mp4
   ```

### A.5. Schedule

| Week | Task |
|------|------|
| Week 1 | Colab env setup, Kaggle auth, dataset downloads |
| Week 2 | Data preprocessing (VOC→YOLO, keyframe extraction, train/val split) |
| Week 3 | Baseline training (100 epochs, hyperparameter sweep) |
| Week 4 | Validation, mAP evaluation, ONNX export, upload to GCS |
| Week 5 | Integration into project, config updates, end-to-end test |

### A.6. Expected Model Performance Targets

| Sport | Target mAP@0.5:0.95 | Target FPS (RTX 3060) | Notes |
|-------|---------------------|----------------------|-------|
| Football | ≥0.75 | ≥25 | Person, ball, referee, goalkeeper |
| Rugby | ≥0.72 | ≥25 | Person, ball, referee |
| Basketball | ≥0.78 | ≥30 | Person, ball (3D LiDAR fusion in Phase 4) |
