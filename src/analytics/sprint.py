"""
Sprint Detection

Identifies sprint bursts from speed data using rolling windows
and threshold-based detection.
"""

import numpy as np


class SprintDetector:
    """Detects sprint events from tracked position/speed data."""

    def __init__(self, sprint_speed_threshold: float = 5.0, min_duration: float = 1.0):
        self.sprint_speed_threshold = sprint_speed_threshold
        self.min_duration = min_duration

    def detect(self, positions: list[tuple[float, float, float]]) -> list[dict[str, float]]:
        """Detect sprint bursts from positions in (x, y, timestamp) format.

        Returns a list of sprint events with start, end, duration, and distance.
        """
        if len(positions) < 3:
            return []

        arr = np.array(positions, dtype=float)
        diffs = np.diff(arr, axis=0)
        dt = diffs[:, 2]
        dt = np.where(dt > 0, dt, 1.0 / 30.0)
        dist_xy = np.sqrt(diffs[:, 0] ** 2 + diffs[:, 1] ** 2)
        speeds = dist_xy / dt
        timestamps = arr[:-1, 2]

        is_sprinting = speeds > self.sprint_speed_threshold

        sprints: list[dict[str, float]] = []
        in_sprint = False
        start_idx = 0

        for i, sprinting in enumerate(is_sprinting):
            if sprinting and not in_sprint:
                in_sprint = True
                start_idx = i
            elif not sprinting and in_sprint:
                in_sprint = False
                duration = float(timestamps[i - 1] - timestamps[start_idx])
                if duration >= self.min_duration:
                    distance = float(np.sum(dist_xy[start_idx:i]))
                    sprints.append(
                        {
                            "start_time": float(timestamps[start_idx]),
                            "end_time": float(timestamps[i - 1]),
                            "duration_sec": duration,
                            "distance_m": distance,
                            "avg_speed_ms": distance / duration if duration > 0 else 0.0,
                        }
                    )

        # Handle sprint that extends to end of data
        if in_sprint:
            duration = float(timestamps[-1] - timestamps[start_idx])
            if duration >= self.min_duration:
                distance = float(np.sum(dist_xy[start_idx:]))
                sprints.append(
                    {
                        "start_time": float(timestamps[start_idx]),
                        "end_time": float(timestamps[-1]),
                        "duration_sec": duration,
                        "distance_m": distance,
                        "avg_speed_ms": distance / duration if duration > 0 else 0.0,
                    }
                )

        return sprints
