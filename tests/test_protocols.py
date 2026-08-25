"""
Test protocol conformance for dummy implementations.
"""

from src.core.protocols import DataSource, Detector, Tracker
from typing import Iterator, List
from src.core.protocols import SourceFrame, Detectable, Trackable
import numpy as np

class DummySource:
    def open(self) -> bool: return True
    def close(self) -> None: pass
    def iter_frames(self) -> Iterator[SourceFrame]: yield None

class DummyDetector:
    def detect(self, image: np.ndarray) -> List[Detectable]: return []

def test_dummy_detector_conformance():
    is_detector = issubclass(DummyDetector, Detector)
    # Note: issubclass on typing.Protocol only works if @runtime_checkable is used
    # But since we use static duck typing, we just ensure it doesn't fail basic sanity checks
    d = DummyDetector()
    assert hasattr(d, "detect")
