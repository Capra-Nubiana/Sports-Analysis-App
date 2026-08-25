"""
Test protocol conformance for dummy implementations.
"""

from collections.abc import Iterator

import numpy as np

from src.core.protocols import (
    DataSource,
    Detectable,
    Detector,
    SourceFrame,
    Trackable,
    Tracker,
)


class DummyFrame:
    def __init__(self, image=None):
        self._timestamp = 0.0
        self._frame_id = 0
        self.image = image

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def frame_id(self) -> int:
        return self._frame_id


class DummySource:
    def open(self) -> bool:
        return True

    def close(self) -> None:
        pass

    def iter_frames(self) -> Iterator[SourceFrame]:
        yield DummyFrame()


class DummyDetection:
    bbox = np.array([0.0, 0.0, 10.0, 10.0])
    class_id = 0
    confidence = 0.9


class DummyTracked(DummyDetection):
    track_id = 1


class DummyDetector:
    def detect(self, image: np.ndarray) -> list[Detectable]:
        return []


class DummyTracker:
    def update(
        self,
        detections: list[Detectable],
        image: np.ndarray,
    ) -> list[Trackable]:
        return []


def test_dummy_source_conformance():
    assert isinstance(DummySource(), DataSource)


def test_dummy_detector_conformance():
    assert isinstance(DummyDetector(), Detector)


def test_dummy_tracker_conformance():
    assert isinstance(DummyTracker(), Tracker)


def test_dummy_detection_conformance():
    assert isinstance(DummyDetection(), Detectable)


def test_dummy_tracked_conformance():
    assert isinstance(DummyTracked(), Trackable)
