"""
Fatigue Analysis — calculates player fatigue index from
biometric and motion data.
"""

import numpy as np

from src.core.models import Player, SensorReading


class FatigueAnalyzer:
    """Estimates player fatigue based on heart rate, metabolic
    power, and motion intensity trends."""

    def __init__(self, window_sec: float = 60.0):
        self.window_sec = window_sec

    def calculate_fatigue_index(
        self,
        player: Player,
        hr_data: list[SensorReading],
        positions: dict[float, tuple[float, float]],
    ) -> float:
        """Compute a 0–1 fatigue index from HR and speed history."""
        if not hr_data or not positions:
            return 0.0

        avg_hr = float(np.mean([r.data.get("heart_rate", 0) for r in hr_data]))
        max_hr = float(np.max([r.data.get("heart_rate", 0) for r in hr_data]))

        if max_hr == 0:
            return 0.0

        hr_ratio = avg_hr / max_hr

        speeds = list(positions.values())
        if len(speeds) < 2:
            speed_variance = 0.0
        else:
            pts = np.array(speeds, dtype=float)
            diffs = np.diff(pts, axis=0)
            distances = np.linalg.norm(diffs, axis=1)
            speed_variance = float(np.var(distances)) if len(distances) > 0 else 0.0

        speed_component = min(speed_variance / 10.0, 1.0)
        fatigue = 0.6 * hr_ratio + 0.4 * speed_component
        return float(np.clip(fatigue, 0.0, 1.0))

    def rolling_fatigue(
        self,
        readings: list[SensorReading],
    ) -> list[tuple[float, float]]:
        """Return (timestamp, fatigue_index) over rolling windows."""
        if len(readings) < 2:
            return []

        result: list[tuple[float, float]] = []
        for i in range(1, len(readings)):
            window = readings[max(0, i - int(self.window_sec)) : i + 1]
            times = [r.timestamp for r in window]
            hrs = [r.data.get("heart_rate", 0) for r in window]
            if not hrs or max(hrs) == 0:
                continue
            normalized = float(np.mean(hrs)) / float(max(hrs))
            result.append((times[-1], round(normalized, 4)))

        return result
