"""
Polar BLE streaming.
"""

from src.core.models import SensorReading
from typing import Callable

class PolarStreamer:
    """Stub for Polar SDK integration (polar-python)."""
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        
    async def start_ecg_stream(self, callback: Callable[[SensorReading], None]) -> None:
        pass # Implementation requires polar-python SDK which is wrapper around native Android/iOS mostly
