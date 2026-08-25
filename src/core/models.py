"""
Core Data Models (Pydantic validation for robust data handling)
"""

from typing import Any

from pydantic import BaseModel, ConfigDict


class Detection(BaseModel):
    """A raw bounding box detection."""

    bbox: list[float]  # [x1, y1, x2, y2]
    class_id: int
    confidence: float


class TrackedDetection(Detection):
    """A detection with a persistent tracking ID across frames."""

    track_id: int


class SensorReading(BaseModel):
    """A single reading from a wearable or laser sensor."""

    timestamp: float
    source_type: str  # "imu", "hr", "lidar", "gps"
    data: dict[str, Any]


class Player(BaseModel):
    """Represents a tracked player on the field."""

    track_id: int
    team_id: int | None = None
    jersey_number: str | None = None
    positions_2d: dict[float, tuple[float, float]] = {}  # timestamp -> (x,y)
    heart_rate: dict[float, int] = {}
    speed: dict[float, float] = {}


class Event(BaseModel):
    """A significant match event."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    event_type: str
    timestamp: float
    frame_id: int
    confidence: float
    players_involved: list[int] = []  # track_ids
    metadata: dict[str, Any] = {}


class Match(BaseModel):
    """Main data container for a full match analysis."""

    sport_type: str
    start_time: str
    teams: dict[int, str] = {0: "Team A", 1: "Team B", 2: "Referee"}
    players: dict[int, Player] = {}
    sensor_streams: dict[str, list[SensorReading]] = {}
    events: list[Event] = []

    def add_event(self, event: Event) -> None:
        self.events.append(event)
        # Notify observers in the future for real-time WebSocket dashboard
