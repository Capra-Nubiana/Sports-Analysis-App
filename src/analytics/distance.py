"""
Distance Analyzer

Computes total distance covered, distance at high speed,
and average speed from tracked player positions.
"""

import numpy as np


class DistanceAnalyzer:
    """Calculates distance and speed metrics from player tracking data."""

    def __init__(self, frame_rate: float = 30.0, high_speed_threshold: float = 3.0):
        self.frame_rate = frame_rate
        self.high_speed_threshold = high_speed_threshold

    def analyze(self, positions: list[tuple[float, float, float]]) -> dict[str, float]:
        """Analyze positions in (x, y, timestamp) format.

        Returns total distance, high-speed distance, and average speed.
        """
        if len(positions) < 2:
            return {
                "total_distance_m": 0.0,
                "high_speed_distance_m": 0.0,
                "average_speed_ms": 0.0,
                "max_speed_ms": 0.0,
            }

        arr = np.array(positions, dtype=float)
        diffs = np.diff(arr, axis=0)
        dt = diffs[:, 2]

        # Avoid division by zero
        dt = np.where(dt > 0, dt, 1.0 / self.frame_rate)

        dist_xy = np.sqrt(diffs[:, 0] ** 2 + diffs[:, 1] ** 2)
        speeds = dist_xy / dt

        high_speed_mask = speeds > self.high_speed_threshold

        return {
            "total_distance_m": float(np.sum(dist_xy)),
            "high_speed_distance_m": float(np.sum(dist_xy[high_speed_mask])),
            "average_speed_ms": float(np.mean(speeds)),
            "max_speed_ms": float(np.max(speeds)),
        }
