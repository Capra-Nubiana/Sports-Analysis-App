"""
Event Detection Base Classes

Sport-specific event detectors that analyze tracked objects frame-by-frame
and emit Event objects when match events are detected (goals, tackles,
touches, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any

from src.core.models import Event
from src.core.protocols import Trackable
from src.core.sport_config import SportConfig
from src.spatial.zones import ZoneManager


class BaseEventDetector(ABC):
    """Abstract base for sport-specific event detectors.

    Implements the EventDetector protocol and provides shared spatial
    lookup and state-tracking infrastructure.
    """

    def __init__(self, config: SportConfig):
        self.config = config
        self.zone_manager = ZoneManager(config)
        self._frame_history: list[dict[str, Any]] = []
        self._events: list[Event] = []
        self._event_cooldown: dict[str, float] = {}

    @property
    def sport_name(self) -> str:
        return self.config.sport_name

    def reset(self) -> None:
        """Clear all accumulated state. Call at match start."""
        self._frame_history.clear()
        self._events.clear()
        self._event_cooldown.clear()

    def _get_ball(self, trackables: list[Trackable]) -> Trackable | None:
        """Return the ball Trackable if present (class_id 32)."""
        for t in trackables:
            if t.class_id == 32:
                return t
        return None

    def _get_players(self, trackables: list[Trackable]) -> list[Trackable]:
        """Return all player Trackables (class_id 0 = person)."""
        return [t for t in trackables if t.class_id == 0]

    def _bottom_center(self, t: Trackable) -> tuple[float, float]:
        """Return bottom-center pixel coordinate of a Trackable's bbox."""
        bbox = list(t.bbox)
        x1, _y1, x2, y2 = bbox
        return ((x1 + x2) / 2.0, y2)

    def _is_on_cooldown(self, event_type: str, timestamp: float, cooldown_sec: float = 3.0) -> bool:
        last = self._event_cooldown.get(event_type)
        if last is not None and (timestamp - last) < cooldown_sec:
            return True
        self._event_cooldown[event_type] = timestamp
        return False

    def process_frame(
        self, trackables: list[Trackable], spatial_map: Any, timestamp: float, frame_id: int
    ) -> list[Event]:
        """Process one frame and return any detected events.

        Delegates to ``_detect`` which subclasses implement.
        """
        record: dict[str, Any] = {
            "timestamp": timestamp,
            "frame_id": frame_id,
            "trackables": trackables,
        }
        self._frame_history.append(record)
        # Keep only last 10 frames for velocity/state calculations
        if len(self._frame_history) > 10:
            self._frame_history.pop(0)

        events = self._detect(trackables, spatial_map, timestamp, frame_id)
        self._events.extend(events)
        return events

    @abstractmethod
    def _detect(
        self, trackables: list[Trackable], spatial_map: Any, timestamp: float, frame_id: int
    ) -> list[Event]:
        """Subclasses implement sport-specific detection logic."""
        ...
