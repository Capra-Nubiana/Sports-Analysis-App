"""
Core Data Models (Pydantic validation for robust data handling)
"""

from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Optional, Tuple, Any

class Detection(BaseModel):
    """A raw bounding box detection."""
    bbox: List[float] # [x1, y1, x2, y2]
    class_id: int
    confidence: float
    
class TrackedDetection(Detection):
    """A detection with a persistent tracking ID across frames."""
    track_id: int

class SensorReading(BaseModel):
    """A single reading from a wearable or laser sensor."""
    timestamp: float
    source_type: str  # "imu", "hr", "lidar", "gps"
    data: Dict[str, Any]

class Player(BaseModel):
    """Represents a tracked player on the field."""
    track_id: int
    team_id: Optional[int] = None
    jersey_number: Optional[str] = None
    positions_2d: Dict[float, Tuple[float, float]] = {} # timestamp -> (x,y)
    heart_rate: Dict[float, int] = {}
    speed: Dict[float, float] = {}

class Event(BaseModel):
    """A significant match event."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    event_type: str
    timestamp: float
    frame_id: int
    confidence: float
    players_involved: List[int] = [] # track_ids
    metadata: Dict[str, Any] = {}

class Match(BaseModel):
    """Main data container for a full match analysis."""
    sport_type: str
    start_time: str
    teams: Dict[int, str] = {0: "Team A", 1: "Team B", 2: "Referee"}
    players: Dict[int, Player] = {}
    sensor_streams: Dict[str, List[SensorReading]] = {}
    events: List[Event] = []
    
    def add_event(self, event: Event) -> None:
        self.events.append(event)
        # Notify observers in the future for real-time WebSocket dashboard
