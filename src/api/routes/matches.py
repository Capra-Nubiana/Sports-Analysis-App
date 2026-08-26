"""Match-level REST endpoints."""

import json
from pathlib import Path
from typing import Any, cast

from fastapi import APIRouter, HTTPException

from src.api.app_state import app
from src.core.models import Match

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("/", response_model=list[dict[str, Any]])
async def list_matches() -> list[dict[str, Any]]:
    """List all saved match timelines in the output directory."""
    output_dir = Path("output")
    if not output_dir.exists():
        return []
    matches: list[dict[str, Any]] = []
    for f in sorted(output_dir.glob("timeline_*.json")):
        matches.append({"file": f.name, "path": str(f)})
    return matches


@router.get("/{match_id}", response_model=dict[str, Any])
async def get_match(match_id: str) -> dict[str, Any]:
    """Get a specific match timeline by ID (filename stem)."""
    output_dir = Path("output")
    path = output_dir / f"timeline_{match_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Match not found: {match_id}")

    with open(path) as f:
        data = json.loads(f.read())
    return cast(dict[str, Any], data)


@router.post("/", response_model=dict[str, str])
async def create_match(match: Match) -> dict[str, str]:
    """Create/register a match object."""
    app.state.store.match_data = match
    return {"status": "created", "sport_type": str(match.sport_type)}


@router.get("/{match_id}/events", response_model=list[dict[str, Any]])
async def get_match_events(match_id: str) -> list[dict[str, Any]]:
    """Get all events for a match."""
    output_dir = Path("output")
    path = output_dir / f"timeline_{match_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Match not found: {match_id}")

    with open(path) as f:
        data = json.loads(f.read())
    return cast(list[dict[str, Any]], data.get("events", []))
