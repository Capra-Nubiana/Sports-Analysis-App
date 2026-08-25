"""
Test synchronization offsets
"""

from src.core.models import SensorReading
from src.ingest.sync import Synchronizer


class DummyVidFrame:
    def __init__(self, ts):
        self.timestamp = ts

    @property
    def frame_id(self):
        return 0


def test_sync_offset():
    s = Synchronizer()
    s.calibrate(video_start_time_utc=100.0, sensor_start_time_utc=102.0)

    assert s.offset == -2.0  # Sensor is 2 seconds ahead of video

    r = SensorReading(timestamp=2.0, source_type="imu", data={"accel": [1, 2, 3]})

    # At video timestamp 0.0, sensor adjusted time is 2.0 - 2.0 = 0.0
    f = DummyVidFrame(0.0)
    matched = s.get_readings_for_frame(f, [r], window_sec=0.1)

    assert len(matched) == 1
    assert matched[0].timestamp == 2.0
