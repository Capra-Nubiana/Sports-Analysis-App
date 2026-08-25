"""
IMU Processing using SKDH (Scikit Digital Health)
"""

import numpy as np
from typing import List, Dict, Any
from src.core.models import SensorReading

class IMUProcessor:
    """Processes raw IMU data (Accel/Gyro) into digital endpoints (steps, impact, gait)."""
    
    def __init__(self, sampling_rate: float = 100.0):
        self.sampling_rate = sampling_rate
        
    def process_gait(self, readings: List[SensorReading]) -> Dict[str, Any]:
        """Calculates gait metrics using SKDH."""
        try:
            import skdh
            from skdh.gait import Gait
        except ImportError:
            print("SKDH not installed.")
            return {}
            
        times = np.array([r.timestamp for r in readings])
        # Assuming r.data['accel'] is a list [x,y,z]
        accel = np.array([r.data.get('accel', [0,0,0]) for r in readings])
        
        gait = Gait()
        res = gait.predict(time=times, accel=accel, fs=self.sampling_rate)
        return res
        
    def detect_impacts(self, readings: List[SensorReading], threshold_g: float = 4.0) -> List[SensorReading]:
        """Detects high-G impacts (e.g. rugby tackles)."""
        impacts = []
        for r in readings:
            acc = r.data.get('accel', [0,0,0])
            magnitude = np.linalg.norm(acc)
            if magnitude > threshold_g:
                impacts.append(r)
        return impacts
