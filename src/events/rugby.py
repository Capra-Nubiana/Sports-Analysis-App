"""
Rugby Event Detector

Detects: tries, tackles, and scrums from tracked player/ball data
and IMU impact readings.
"""

import numpy as np

from src.core.models import Event, SensorReading
from src.core.protocols import Trackable
from src.core.sport_config import SportConfig
from src.events.base import BaseEventDetector
from src.spatial.homography import HomographyMapper


class RugbyEventDetector(BaseEventDetector):
    """Detects rugby-specific events from tracked video frames and IMU data."""

    def __init__(self, config: SportConfig):
        super().__init__(config)
        self._player_velocities: dict[int, tuple[float, float, float]] = {}
        self._tackle_cooldown: dict[int, float] = {}
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
        player_xy: dict[int, tuple[float, float]] = {}

        if ball is not None and spatial_map is not None and spatial_map.H is not None:
            px, py = self._bottom_center(ball)
            ball_xy = spatial_map.transform(px, py)

        for p in players:
            if spatial_map is not None and spatial_map.H is not None:
                px, py = self._bottom_center(p)
                player_xy[p.track_id] = spatial_map.transform(px, py)
            else:
                player_xy[p.track_id] = self._bottom_center(p)

        # --- Try detection ---
        try_events = self._detect_try(ball, ball_xy, players, timestamp, frame_id)
        events.extend(try_events)

        # --- Tackle detection ---
        tackle_event = self._detect_tackle(players, player_xy, timestamp, frame_id)
        if tackle_event is not None:
            events.append(tackle_event)

        # --- Scrum detection (player clustering) ---
        scrum_event = self._detect_scrum(players, player_xy, timestamp, frame_id)
        if scrum_event is not None:
            events.append(scrum_event)

        return events

    def _detect_try(
        self,
        ball: Trackable | None,
        ball_xy: tuple[float, float] | None,
        players: list[Trackable],
        timestamp: float,
        frame_id: int,
    ) -> list[Event]:
        """Detect a try: ball grounded in the try zone."""
        if ball_xy is None:
            return []

        try_zones = [k for k in self.config.get("spatial.zones", {}) if "try_zone" in k]

        events: list[Event] = []
        for zone_name in try_zones:
            if self.zone_manager.point_in_zone(ball_xy, zone_name):
                if zone_name not in self._is_on_cooldown_check(timestamp):
                    scoring_team = 0 if "home" in zone_name.lower() else 1
                    events.append(
                        Event(
                            event_type="try_scored",
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
            if timestamp - self._goal_cooldown[zone_name] >= 5.0:
                active.append(zone_name)
        return active

    def _detect_tackle(
        self,
        players: list[Trackable],
        player_xy: dict[int, tuple[float, float]],
        timestamp: float,
        frame_id: int,
    ) -> Event | None:
        """Detect a tackle: sudden velocity drop (overlap) between players."""
        velocity_drop = self.config.get("events.tackle.velocity_drop", 0.7)
        overlap_dist = self.config.get("events.tackle.overlap_distance_threshold", 1.0)

        for i, p1 in enumerate(players):
            for p2 in players[i + 1 :]:
                pos1 = player_xy.get(p1.track_id)
                pos2 = player_xy.get(p2.track_id)
                if pos1 is None or pos2 is None:
                    continue

                dist = float(np.linalg.norm(np.array(pos1) - np.array(pos2)))
                if dist > overlap_dist:
                    continue

                # Check velocity drop
                v1 = self._player_velocity(p1.track_id, pos1, timestamp)
                if v1 > 0 and v1 * (1 - velocity_drop) <= 0:
                    if (
                        self._tackle_cooldown.get(p1.track_id, 0)
                        and timestamp - self._tackle_cooldown[p1.track_id] < 3.0
                    ):
                        continue
                    self._tackle_cooldown[p1.track_id] = timestamp
                    return Event(
                        event_type="tackle",
                        timestamp=timestamp,
                        frame_id=frame_id,
                        confidence=0.85,
                        players_involved=[p1.track_id, p2.track_id],
                        metadata={"distance_m": dist, "velocity_before": v1},
                    )

        return None

    def _detect_scrum(
        self,
        players: list[Trackable],
        player_xy: dict[int, tuple[float, float]],
        timestamp: float,
        frame_id: int,
    ) -> Event | None:
        """Detect a scrum: cluster of 8+ players remaining stationary."""
        density_threshold = self.config.get("events.scrum.player_density_threshold", 8)
        cluster_radius = self.config.get("events.scrum.cluster_radius", 3.5)
        stationary_duration = self.config.get("events.scrum.stationary_duration", 3.0)

        if len(players) < density_threshold:
            return None

        positions = np.array(list(player_xy.values()), dtype=float)
        # Simple center-of-mass clustering
        centroid = positions.mean(axis=0)
        distances = np.linalg.norm(positions - centroid, axis=1)
        clustered = int(np.sum(distances < cluster_radius))

        if clustered >= density_threshold:
            if not hasattr(self, "_scrum_start"):
                self._scrum_start = timestamp
                return None
            duration = timestamp - self._scrum_start
            if duration >= stationary_duration:
                del self._scrum_start
                self._scrum_start = timestamp
                return Event(
                    event_type="scrum",
                    timestamp=timestamp,
                    frame_id=frame_id,
                    confidence=0.7,
                    players_involved=[p.track_id for p in players[:clustered]],
                    metadata={"player_count": clustered, "duration_sec": duration},
                )
        else:
            if hasattr(self, "_scrum_start"):
                del self._scrum_start

        return None

    def _player_velocity(self, track_id: int, pos: tuple[float, float], timestamp: float) -> float:
        """Estimate player speed in m/s based on last known position."""
        prev = self._player_velocities.get(track_id)
        self._player_velocities[track_id] = (pos[0], pos[1], timestamp)
        if prev is None:
            return 0.0
        dt = timestamp - prev[2]
        if dt <= 0:
            return 0.0
        dist = float(np.linalg.norm(np.array(pos) - np.array([prev[0], prev[1]])))
        return dist / dt

    def detect_impacts(self, readings: list[SensorReading]) -> list[SensorReading]:
        """Flag IMU readings exceeding the rugby tackle G-force threshold."""
        threshold = self.config.get("wearables.imu.g_force_threshold_tackle", 8.0)
        impacts: list[SensorReading] = []
        for r in readings:
            accel = r.data.get("accel", [0, 0, 0])
            g = float(np.linalg.norm(accel))
            if g > threshold:
                impacts.append(r)
        return impacts
