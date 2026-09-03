"""Highlight REST endpoints.

Copyright (c) 2026 Philip Kwimba. All rights reserved.
Licensed under AGPLv3 (see LICENSE).
"""


from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from src.api.app_state import app, load_match_timeline

router = APIRouter(prefix="/highlights", tags=["highlights"])


@router.get("/", response_model=list[dict[str, Any]])
async def list_highlights() -> list[dict[str, Any]]:
    """List all generated highlight clips in the output directory."""
    output_dir = Path("output")
    if not output_dir.exists():
        return []
    clips: list[dict[str, Any]] = [
        {"file": f.name, "path": f"output/{f.name}"}
        for f in sorted(output_dir.glob("highlight_*.mp4"))
    ]
    reel = output_dir / "highlight_reel.mp4"
    if reel.exists():
        clips.append({"file": reel.name, "path": f"output/{reel.name}", "reel": True})
    return clips


@router.get("/reel", response_model=dict[str, Any])
async def get_reel() -> dict[str, Any]:
    """Get or generate the highlight reel path."""
    output_dir = Path("output")
    reel = output_dir / "highlight_reel.mp4"
    if reel.exists():
        return {"path": str(reel), "exists": True}
    # If no reel exists, generate one from the match timeline
    if app.state.store.match_data is None:
        raise HTTPException(status_code=404, detail="No match data available")
    from src.highlights.ffmpeg_extractor import ClipExtractor
    from src.highlights.scorer import HighlightScorer

    scorer = HighlightScorer()
    events = app.state.store.match_data.events
    if not events:
        raise HTTPException(status_code=404, detail="No events to generate highlights from")
    extractor = ClipExtractor("input.mp4")
    reel_path = extractor.create_highlight_reel(events, scorer)
    if reel_path:
        return {"path": str(reel_path), "exists": True}
    raise HTTPException(status_code=500, detail="Failed to generate highlight reel")


@router.get("/timeline/{match_id}", response_model=dict[str, Any])
async def get_highlight_timeline(match_id: str) -> dict[str, Any]:
    """Get the highlight-scored timeline for a match."""
    from src.core.models import Event
    from src.highlights.scorer import HighlightScorer

    timeline = load_match_timeline(f"output/timeline_{match_id}.json")
    if "error" in timeline:
        raise HTTPException(status_code=404, detail=timeline["error"])
    events_data = timeline.get("events", [])
    events = [Event(**e) for e in events_data]
    scorer = HighlightScorer()
    windows = scorer.highlight_windows(events)
    return {"windows": [{"start": s, "end": e, "score": sc} for s, e, sc in windows]}
