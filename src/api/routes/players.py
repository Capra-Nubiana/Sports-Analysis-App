"""Player REST endpoints.

Copyright (c) 2026 Philip Kwimba. All rights reserved.
Licensed under AGPLv3 (see LICENSE).
"""


from typing import Any

from fastapi import APIRouter, HTTPException

from src.api.app_state import app
from src.core.models import Player

router = APIRouter(prefix="/players", tags=["players"])


@router.get("/", response_model=list[dict[str, Any]])
async def list_players() -> list[dict[str, Any]]:
    """Get all tracked players from the current match."""
    if app.state.store.match_data is None:
        return []
    return [
        {**p.model_dump(), "track_id": tid} for tid, p in app.state.store.match_data.players.items()
    ]


@router.get("/{player_id}", response_model=dict[str, Any])
async def get_player(player_id: int) -> dict[str, Any]:
    """Get a specific player by track_id."""
    if app.state.store.match_data is None:
        raise HTTPException(status_code=404, detail="No match loaded")
    if player_id not in app.state.store.match_data.players:
        raise HTTPException(status_code=404, detail=f"Player not found: {player_id}")
    p = app.state.store.match_data.players[player_id]
    return {**p.model_dump(), "track_id": player_id}


@router.get("/{player_id}/heatmap", response_model=dict[str, Any])
async def get_player_heatmap(player_id: int) -> dict[str, Any]:
    """Get heatmap data for a player (positions over time)."""
    if app.state.store.match_data is None:
        raise HTTPException(status_code=404, detail="No match loaded")
    if player_id not in app.state.store.match_data.players:
        raise HTTPException(status_code=404, detail=f"Player not found: {player_id}")
    p = app.state.store.match_data.players[player_id]
    return {
        "track_id": player_id,
        "positions": list(p.positions_2d.items()) if p.positions_2d else [],
    }
