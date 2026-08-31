"""
FastAPI application factory.

Creates and configures the ASGI application with all routes,
CORS middleware, and WebSocket support for real-time tracking.
"""

from fastapi import FastAPI, WebSocket

from src.api.app_state import app
from src.api.routes import events, highlights, matches, players
from src.core.sport_config import SportConfig

app.include_router(matches.router)
app.include_router(events.router)
app.include_router(players.router)
app.include_router(highlights.router)


@app.websocket("/ws/tracking")
async def websocket_tracking(ws: WebSocket) -> None:
    """WebSocket endpoint for real-time tracking data streaming."""
    await ws.accept()
    app.state.store.active_connections.append(ws)
    try:
        while True:
            data = await ws.receive_text()
            if data == "close":
                break
            await ws.send_text(f"echo: {data}")
    except Exception:  # noqa: S110
        pass
    finally:
        app.state.store.active_connections.remove(ws)
        await ws.close()


def create_app(sport_name: str = "football", config_dir: str = "config") -> FastAPI:
    """Application factory that configures sport-specific settings."""
    app.state.store.sport_config = SportConfig(sport_name, config_dir)
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=True)  # noqa: S104
