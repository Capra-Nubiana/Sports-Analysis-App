"""
Basketball Event Detector

Detects: scored baskets and three-pointers from tracked ball/player data.
"""

import numpy as np

from src.core.models import Event
from src.core.protocols import Trackable
from src.core.sport_config import SportConfig
from src.events.base import BaseEventDetector
from src.spatial.homography import HomographyMapper


class BasketballEventDetector(BaseEventDetector):
    """Detects basketball-specific events from tracked video frames."""

    BALL_CLASS_ID = 32
    PERSON_CLASS_ID = 0

    def __init__(self, config: SportConfig):
        super().__init__(config)
        self._ball_history: list[tuple[float, float, float]] = []
        self._shot_in_progress = False
        self._shot_release_pos: tuple[float, float] | None = None

    def _detect(
        self,
        trackables: list[Trackable],
        spatial_map: HomographyMapper,
        timestamp: float,
        frame_id: int,
    ) -> list[Event]:
        events: list[Event] = []
        ball = self._get_ball(trackables)
        players = self._get_players(trackables)

        ball_xy: tuple[float, float] | None = None
        if ball is not None and spatial_map is not None and spatial_map.H is not None:
            px, py = self._bottom_center(ball)
            ball_xy = spatial_map.transform(px, py)

        # Track ball history for trajectory analysis
        if ball_xy is not None:
            self._ball_history.append((ball_xy[0], ball_xy[1], timestamp))
            if len(self._ball_history) > 15:
                self._ball_history.pop(0)

        # --- Scored basket detection ---
        basket_event = self._detect_scored_basket(ball, ball_xy, timestamp, frame_id)
        if basket_event is not None:
            events.append(basket_event)

        # --- Three-pointer detection ---
        tp_event = self._detect_three_pointer(ball_xy, players, spatial_map, timestamp, frame_id)
        if tp_event is not None:
            events.append(tp_event)

        return events

    def _detect_scored_basket(
        self,
        ball: Trackable | None,
        ball_xy: tuple[float, float] | None,
        timestamp: float,
        frame_id: int,
    ) -> Event | None:
        """Detect a scored basket: ball passes through the hoop plane."""
        if ball_xy is None:
            return None

        hoop_home = self.config.get("spatial.zones.hoop_home")
        hoop_away = self.config.get("spatial.zones.hoop_away")
        radius = self.config.get("events.scored_basket.ball_in_zone_radius", 0.5)

        if hoop_home:
            hx, hy = float(hoop_home[0]), float(hoop_home[1])
            dist = float(np.linalg.norm(np.array(ball_xy) - np.array([hx, hy])))
            if dist <= radius and not self._is_on_cooldown("scored_basket", timestamp, 3.0):
                return Event(
                    event_type="scored_basket",
                    timestamp=timestamp,
                    frame_id=frame_id,
                    confidence=ball.confidence if ball else 0.5,
                    players_involved=[],
                    metadata={"hoop": "home", "distance_m": dist},
                )

        if hoop_away:
            hx, hy = float(hoop_away[0]), float(hoop_away[1])
            dist = float(np.linalg.norm(np.array(ball_xy) - np.array([hx, hy])))
            if dist <= radius and not self._is_on_cooldown("scored_basket", timestamp, 3.0):
                return Event(
                    event_type="scored_basket",
                    timestamp=timestamp,
                    frame_id=frame_id,
                    confidence=ball.confidence if ball else 0.5,
                    players_involved=[],
                    metadata={"hoop": "away", "distance_m": dist},
                )

        return None

    def _detect_three_pointer(
        self,
        ball_xy: tuple[float, float] | None,
        players: list[Trackable],
        spatial_map: HomographyMapper,
        timestamp: float,
        frame_id: int,
    ) -> Event | None:
        """Detect a three-pointer: shot taken from beyond the 3-point line."""
        if ball_xy is None or len(self._ball_history) < 3:
            return None

        min_distance = self.config.get("events.three_pointer.distance_to_hoop_start", 6.75)
        hoop = self.config.get("spatial.zones.hoop_home")
        if hoop is None:
            return None

        hx, hy = float(hoop[0]), float(hoop[1])

        # Check if ball is moving downward toward hoop (trajectory from history)
        hist = self._ball_history
        dz = hist[-1][2] - hist[0][2]
        if dz <= 0.01:
            return None

        # Ball should be above hoop height (z-axis not available in 2D, use y-axis as proxy)
        # The ball should be descending toward the hoop
        ball_height_change = hist[-1][1] - hist[0][1]  # y-axis (vertical in image)
        if ball_height_change < 0:  # Ball moving down in the image (toward hoop)
            dist_to_hoop = float(np.linalg.norm(np.array(ball_xy) - np.array([hx, hy])))
            if dist_to_hoop > min_distance and not self._is_on_cooldown(
                "three_pointer", timestamp, 3.0
            ):
                return Event(
                    event_type="three_pointer",
                    timestamp=timestamp,
                    frame_id=frame_id,
                    confidence=0.75,
                    players_involved=[p.track_id for p in players[:5]],
                    metadata={"distance_to_hoop_m": dist_to_hoop},
                )

        return None
