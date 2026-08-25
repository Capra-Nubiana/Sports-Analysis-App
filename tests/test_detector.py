"""
Test YOLO detection wrapper logic (stub for CI without weights)
"""

from src.detection.detector import YOLODetector
import numpy as np

def test_detector_initialization():
    # Will gracefully set model to None if ultralytics is missing/weights not found
    d = YOLODetector(model_path="dummy.pt")
    assert d.confidence == 0.3
    
def test_detect_empty():
    d = YOLODetector(model_path="dummy.pt")
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    # If model didn't load (e.g. no ultralytics in CI), should return []
    res = d.detect(image)
    assert isinstance(res, list)
    assert len(res) == 0
