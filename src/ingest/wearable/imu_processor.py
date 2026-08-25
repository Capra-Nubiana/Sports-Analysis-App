"""
IMU Processing using SKDH (Scikit Digital Health)
"""

from typing import Any

import numpy as np

from src.core.models import SensorReading


class IMUProcessor:
    """Processes raw IMU data (Accel/Gyro) into digital endpoints (steps, impact, gait)."""

    def __init__(self, sampling_rate: float = 100.0):
        self.sampling_rate = sampling_rate

    def process_gait(self, readings: list[SensorReading]) -> dict[str, Any]:
        """Calculates gait metrics using SKDH."""
        try:
            from skdh.gait import Gait
        except ImportError:
            print("SKDH not installed.")
            return {}

        times = np.array([r.timestamp for r in readings])
        # Assuming r.data['accel'] is a list [x,y,z]
        accel = np.array([r.data.get("accel", [0, 0, 0]) for r in readings])

        gait = Gait()
        res = gait.predict(time=times, accel=accel, fs=self.sampling_rate)
        return dict(res) if isinstance(res, dict) else {}

    def detect_impacts(
        self, readings: list[SensorReading], threshold_g: float = 4.0
    ) -> list[SensorReading]:
        """Detects high-G impacts (e.g. rugby tackles)."""
        impacts = []
        for r in readings:
            acc = r.data.get("accel", [0, 0, 0])
            magnitude = np.linalg.norm(acc)
            if magnitude > threshold_g:
                impacts.append(r)
        return impacts
