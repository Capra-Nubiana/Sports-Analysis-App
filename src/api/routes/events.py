"""Event REST endpoints.

Copyright (c) 2026 Philip Kwimba. All rights reserved.
Licensed under AGPLv3 (see LICENSE).
"""


from typing import Any, cast

from fastapi import APIRouter, HTTPException

from src.api.app_state import app
from src.core.models import Event

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=list[dict[str, Any]])
async def list_events() -> list[dict[str, Any]]:
    """Get all events from the current in-memory match."""
    if app.state.store.match_data is None:
        return []
    return [e.model_dump() for e in app.state.store.match_data.events]


@router.get("/{event_id}", response_model=dict[str, Any])
async def get_event(event_id: int) -> dict[str, Any]:
    """Get a specific event by index."""
    if app.state.store.match_data is None:
        raise HTTPException(status_code=404, detail="No match loaded")
    events = app.state.store.match_data.events
    if event_id < 0 or event_id >= len(events):
        raise HTTPException(status_code=404, detail=f"Event not found: {event_id}")
    return cast(dict[str, Any], events[event_id].model_dump())


@router.post("/", response_model=dict[str, str])
async def add_event(event: Event) -> dict[str, str]:
    """Add an event to the current match."""
    if app.state.store.match_data is None:
        raise HTTPException(status_code=400, detail="No match loaded. Create match first.")
    app.state.store.match_data.add_event(event)
    return {"status": "added", "event_type": str(event.event_type)}
