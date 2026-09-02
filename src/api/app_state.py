"""
Shared application state and utilities for the API.

Separated from main.py to avoid circular imports between
route modules and the FastAPI app factory.
"""

import json
from pathlib import Path
from typing import Any, cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.models import Match
from src.core.sport_config import SportConfig


class AppState:
    """Shared application state for match data and active WebSocket connections."""

    def __init__(self) -> None:
        self.match_data: Match | None = None
        self.active_connections: list[Any] = []
        self.sport_config: SportConfig | None = None
        self.output_dir = Path("output")
        self.uploads_dir = Path("uploads")
        self.uploaded_videos: dict[str, dict[str, Any]] = {}
        self.jobs: dict[str, dict[str, Any]] = {}


app = FastAPI(
    title="Sports Analysis API",
    description="REST + WebSocket API for sports match analysis, event detection, and highlights.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.store = AppState()


def load_match_timeline(timeline_path: str) -> dict[str, Any]:
    """Load a saved match timeline JSON file."""
    path = Path(timeline_path)
    if not path.exists():
        return {"error": f"Timeline not found: {timeline_path}"}
    with open(path) as f:
        data = json.loads(f.read())
    return cast(dict[str, Any], data)
