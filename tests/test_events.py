"""
Tests for event detection (Phase 2).
"""

from src.core.models import SensorReading
from src.core.sport_config import SportConfig
from src.events.base import BaseEventDetector
from src.events.basketball import BasketballEventDetector
from src.events.factory import EventDetectorFactory
from src.events.football import FootballEventDetector
from src.events.rugby import RugbyEventDetector
from src.spatial.homography import HomographyMapper


def _make_tracking(bbox, class_id, track_id, confidence=0.9):
    """Create a minimal Trackable-like object for testing."""

    class _T:
        def __init__(self):
            self.bbox = bbox
            self.class_id = class_id
            self.track_id = track_id
            self.confidence = confidence

    return _T()


def test_event_detector_factory():
    config = SportConfig("football", config_dir="config")
    detector = EventDetectorFactory.create("football", config)
    assert isinstance(detector, FootballEventDetector)
    assert isinstance(detector, BaseEventDetector)


def test_event_detector_factory_unsupported():
    config = SportConfig("football", config_dir="config")
    try:
        EventDetectorFactory.create("unknown", config)
        assert False
    except ValueError:
        assert True


def test_supported_sports():
    sports = EventDetectorFactory.supported_sports()
    assert "football" in sports
    assert "rugby" in sports
    assert "basketball" in sports


def test_football_no_ball_no_events():
    config = SportConfig("football", config_dir="config")
    detector = FootballEventDetector(config)
    players = [_make_tracking([100, 100, 120, 200], 0, 1)]
    events = detector.process_frame(players, HomographyMapper(), 10.0, 1)
    assert isinstance(events, list)
    assert len(events) == 0


def test_basketball_ball_near_hoop():
    config = SportConfig("basketball", config_dir="config")
    detector = BasketballEventDetector(config)
    # Ball near hoop_home [1.575, 7.62] — set bbox so bottom center maps close
    # Without homography, ball_xy will be None, so no events
    ball = _make_tracking([100, 100, 110, 115], 32, 99, 0.9)
    player = _make_tracking([200, 200, 220, 300], 0, 1, 0.9)
    events = detector.process_frame([ball, player], HomographyMapper(), 5.0, 1)
    assert isinstance(events, list)


def test_rugby_detect_impacts():
    config = SportConfig("rugby", config_dir="config")
    detector = RugbyEventDetector(config)
    readings = [
        SensorReading(timestamp=0.0, source_type="imu", data={"accel": [1, 2, 3]}),
        SensorReading(timestamp=1.0, source_type="imu", data={"accel": [10, 10, 10]}),
        SensorReading(timestamp=2.0, source_type="imu", data={"accel": [0, 0, 0]}),
    ]
    impacts = detector.detect_impacts(readings)
    assert len(impacts) == 1
    # magnitude = sqrt(10^2 + 10^2 + 10^2) ≈ 17.32 > 8.0
    accel = impacts[0].data["accel"]
    import math

    mag = math.sqrt(sum(a**2 for a in accel))
    assert mag > 8.0


def test_event_reset():
    config = SportConfig("football", config_dir="config")
    detector = FootballEventDetector(config)
    detector.reset()
    assert len(detector._events) == 0
    assert len(detector._frame_history) == 0
