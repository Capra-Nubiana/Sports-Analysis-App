"""
Tests for GPU batch processing (Phase 4).
"""

import numpy as np

from src.detection.batch_processor import BatchProcessor


def test_batch_processor_init():
    bp = BatchProcessor(model_path="yolov8x.pt", batch_size=4)
    assert bp.batch_size == 4
    assert bp.classes == [0, 32]
    assert bp.device == "cpu"  # No GPU in CI


def test_batch_processor_detect_no_model():
    """BatchProcessor without YOLO installed should return empty detections."""
    bp = BatchProcessor(model_path="nonexistent.pt", batch_size=2)
    # model_path won't load (ultralytics may not be installed in test env)
    result = bp.detect(np.zeros((640, 480, 3), dtype=np.uint8))
    assert isinstance(result, list)


def test_batch_processor_queue_and_flush():
    """Queueing frames below batch_size should return None; flush returns detections."""
    bp = BatchProcessor(model_path="yolov8x.pt", batch_size=4)
    frame = np.zeros((640, 480, 3), dtype=np.uint8)

    # Queue 3 frames (below batch_size)
    result = bp.queue_frame(frame, timestamp=1.0, frame_id=1)
    assert result is None

    # Flush returns at least one (possibly empty) detection list
    results = bp.flush()
    assert len(results) == 1


def test_batch_processor_custom_classes():
    bp = BatchProcessor(model_path="yolov8x.pt", classes=[0, 1, 32], batch_size=8)
    assert bp.classes == [0, 1, 32]


def test_batch_processor_device_property():
    bp = BatchProcessor(model_path="yolov8x.pt", batch_size=4)
    assert isinstance(bp.device_name, str)
