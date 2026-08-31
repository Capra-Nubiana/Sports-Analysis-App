# Sports Analysis Dashboard

React + TypeScript + Vite dashboard for the Sports Analysis App.

## Prerequisites

- Node.js 20+
- Python backend running on `http://localhost:8000`

## Setup

```bash
npm install
npm run dev
```

## Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server (port 5173) |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Run oxlint |

## Features

- **Live Tracking** — WebSocket-powered real-time player tracking on a pitch canvas
- **Events** — Interactive event timeline with confidence visualization
- **Analytics** — Player heatmaps, distance bar charts, sprint detection
- **Highlights** — List generated highlight clips and reels

## API Integration

The dashboard proxies API requests to `http://localhost:8000/api/v1/` via Vite's dev server proxy. WebSocket connections use `/ws/tracking`.
