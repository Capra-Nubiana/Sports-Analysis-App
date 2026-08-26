"""
API package for the Sports Analysis App.

FastAPI REST + WebSocket backend serving match data, events,
player tracking, and highlights.
"""

from src.api.app_state import AppState, app, load_match_timeline
from src.api.main import create_app

__all__ = ["app", "AppState", "load_match_timeline", "create_app"]
