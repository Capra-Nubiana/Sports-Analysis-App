"""
Test ByteTrack wrapper logic
"""

import numpy as np

from src.detection.tracker import ByteTrackerWrapper


def test_tracker_initialization():
    # Supervision might not be installed in the CI env, so it sets tracker to None
    ByteTrackerWrapper()


def test_tracker_empty():
    t = ByteTrackerWrapper()
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    res = t.update([], image)
    assert isinstance(res, list)
    assert len(res) == 0
