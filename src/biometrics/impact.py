"""
Impact and G-Force Analysis via IMU.
"""

from typing import List, Dict
from src.core.models import SensorReading

class ImpactAnalyzer:
    def get_max_impact(self, readings: List[SensorReading]) -> Dict[str, float]:
        import numpy as np
        max_g = 0.0
        for r in readings:
            accel = r.data.get('accel', [0,0,0])
            g = float(np.linalg.norm(accel))
            if g > max_g:
                max_g = g
                
        return {"max_g_force": max_g}
