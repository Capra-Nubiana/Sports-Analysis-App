"""
YOLO Object Detection Wrapper
Implements Detector protocol.
"""

from typing import List
import numpy as np
import torch
from src.core.protocols import Detector, Detectable
from src.core.models import Detection

class YOLODetector(Detector):
    def __init__(self, model_path: str = "yolov8x.pt", confidence: float = 0.3, classes: List[int] = None):
        self.confidence = confidence
        self.classes = classes or [0, 32] # Default: Person, Sports ball
        
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
            # Force auto-cast to best device (CUDA -> MPS -> CPU)
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
        except ImportError:
            print("ultralytics YOLO not installed.")
            self.model = None

    def detect(self, image: np.ndarray) -> List[Detectable]:
        if self.model is None:
            return []
            
        results = self.model(
            image,
            conf=self.confidence,
            classes=self.classes,
            verbose=False,
            device=self.device
        )[0]
        
        detections = []
        if len(results.boxes) == 0:
            return detections
            
        boxes = results.boxes.xyxy.cpu().numpy()
        confidences = results.boxes.conf.cpu().numpy()
        class_ids = results.boxes.cls.cpu().numpy().astype(int)
        
        for bbox, conf, cls_id in zip(boxes, confidences, class_ids):
            detections.append(Detection(
                bbox=bbox.tolist(),
                class_id=cls_id,
                confidence=float(conf)
            ))
            
        return detections
