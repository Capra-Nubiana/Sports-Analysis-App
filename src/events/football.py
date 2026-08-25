"""
Football (Soccer) Event Detector

Detects: goals, passes, and touches using tracked player/ball data
and real-world spatial mapping.
"""

import numpy as np

from src.core.models import Event
from src.core.protocols import Trackable
from src.core.sport_config import SportConfig
from src.events.base import BaseEventDetector
from src.spatial.homography import HomographyMapper


class FootballEventDetector(BaseEventDetector):
    """Detects football-specific events from tracked video frames."""

    def __init__(self, config: SportConfig):
        super().__init__(config)
        self._pass_in_progress = False
        self._last_ball_pos: tuple[float, float] | None = None
        self._last_ball_frame: int = -1
        self._goal_cooldown: dict[str, float] = {}

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

        # --- Goal detection ---
        goal_events = self._detect_goal(ball, ball_xy, players, timestamp, frame_id)
        events.extend(goal_events)

        # --- Pass detection ---
        pass_event = self._detect_pass(ball, ball_xy, players, timestamp, frame_id)
        if pass_event is not None:
            events.append(pass_event)

        # Update state
        if ball_xy is not None:
            self._last_ball_pos = ball_xy
            self._last_ball_frame = frame_id

        return events

    def _detect_goal(
        self,
        ball: Trackable | None,
        ball_xy: tuple[float, float] | None,
        players: list[Trackable],
        timestamp: float,
        frame_id: int,
    ) -> list[Event]:
        """Detect if the ball entered a goal zone."""
        if ball_xy is None:
            return []

        goal_zones = self.config.get("spatial.zones", {})
        goal_zone_names = [k for k in goal_zones if "goal_area" in k]

        events: list[Event] = []
        for zone_name in goal_zone_names:
            if self.zone_manager.point_in_zone(ball_xy, zone_name):
                if zone_name not in self._is_on_cooldown_check(timestamp):
                    scoring_team = 0 if "home" in zone_name.lower() else 1
                    events.append(
                        Event(
                            event_type="goal",
                            timestamp=timestamp,
                            frame_id=frame_id,
                            confidence=ball.confidence if ball else 0.5,
                            players_involved=[p.track_id for p in players],
                            metadata={"zone": zone_name, "scoring_team": scoring_team},
                        )
                    )
                    self._goal_cooldown[zone_name] = timestamp
        return events

    def _is_on_cooldown_check(self, timestamp: float) -> list[str]:
        """Return zones NOT on cooldown. Updates cooldowns in place."""
        active: list[str] = []
        for zone_name in list(self._goal_cooldown.keys()):
            if timestamp - self._goal_cooldown[zone_name] >= 3.0:
                active.append(zone_name)
        return active

    def _detect_pass(
        self,
        ball: Trackable | None,
        ball_xy: tuple[float, float] | None,
        players: list[Trackable],
        timestamp: float,
        frame_id: int,
    ) -> Event | None:
        """Detect a pass: ball moves from one player to another."""
        if ball_xy is None or len(players) < 2:
            return None

        max_dist = self.config.get("events.pass.max_distance_to_nearest_player_start", 1.5)

        nearest_player = min(
            players,
            key=lambda p: self._player_distance_to_ball(p, ball_xy),
        )

        dist = self._player_distance_to_ball(nearest_player, ball_xy)

        if dist <= max_dist and not self._pass_in_progress:
            self._pass_in_progress = True
            return Event(
                event_type="pass",
                timestamp=timestamp,
                frame_id=frame_id,
                confidence=0.8,
                players_involved=[nearest_player.track_id],
                metadata={"distance": dist},
            )

        if dist > max_dist and self._pass_in_progress:
            self._pass_in_progress = False

        return None

    def _player_distance_to_ball(self, player: Trackable, ball_xy: tuple[float, float]) -> float:
        """2D distance from player's bottom-center to ball position in meters."""
        return float(np.linalg.norm(np.array(ball_xy) - np.array(self._bottom_center(player))))
