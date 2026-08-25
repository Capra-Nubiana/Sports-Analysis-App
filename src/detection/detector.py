"""
YOLO Object Detection Wrapper
Implements Detector protocol.
"""

from collections.abc import Sequence

import numpy as np

from src.core.models import Detection
from src.core.protocols import Detectable, Detector


class YOLODetector(Detector):
    def __init__(
        self,
        model_path: str = "yolov8x.pt",
        confidence: float = 0.3,
        classes: list[int] | None = None,
    ):
        self.confidence = confidence
        self.classes = classes or [0, 32]  # Default: Person, Sports ball
        self.model = None
        self.device = "cpu"

        try:
            import torch
            from ultralytics import YOLO

            self.model = YOLO(model_path)
            # Force auto-cast to best device (CUDA -> MPS -> CPU)
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
        except ImportError:
            print("ultralytics YOLO not installed.")
            self.model = None
        except Exception as e:
            print(f"YOLO model not loaded: {e}")
            self.model = None

    def detect(self, image: np.ndarray) -> Sequence[Detectable]:
        if self.model is None:
            return []

        results = self.model(
            image,
            conf=self.confidence,
            classes=self.classes,
            verbose=False,
            device=self.device,
        )[0]

        detections: list[Detection] = []
        if len(results.boxes) == 0:
            return detections

        boxes = results.boxes.xyxy.cpu().numpy()
        confidences = results.boxes.conf.cpu().numpy()
        class_ids = results.boxes.cls.cpu().numpy().astype(int)

        for bbox, conf, cls_id in zip(boxes, confidences, class_ids, strict=False):
            detections.append(
                Detection(
                    bbox=bbox.tolist(),
                    class_id=cls_id,
                    confidence=float(conf),
                )
            )

        return detections
