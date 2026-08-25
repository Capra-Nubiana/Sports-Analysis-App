"""
Time synchronization engine.
Aligns video frames with wearable/LiDAR timestamps.
"""

from src.core.models import SensorReading
from src.core.protocols import SourceFrame


class Synchronizer:
    def __init__(self, method: str = "timestamp"):
        self.method = method
        self.offset = 0.0  # Time offset to apply to sensor readings to match video

    def calibrate(self, video_start_time_utc: float, sensor_start_time_utc: float) -> None:
        """Simple UTC timestamp alignment."""
        self.offset = video_start_time_utc - sensor_start_time_utc

    def get_readings_for_frame(
        self, frame: SourceFrame, all_readings: list[SensorReading], window_sec: float = 0.05
    ) -> list[SensorReading]:
        """Get sensor readings that occurred within a temporal window around the video frame."""
        # This assumes frame.timestamp is relative to video start (0.0)
        # and sensor readings have been adjusted by offset so they are also relative to 0.0

        frame_time = frame.timestamp
        matched = []
        for r in all_readings:
            adjusted_time = r.timestamp + self.offset
            if abs(adjusted_time - frame_time) <= window_sec:
                matched.append(r)

        return matched
