"""
GPU Batch Inference Processor

Optimized batch inference for YOLO detection using GPU acceleration.
Processes multiple frames in a single batch for higher throughput.
"""

from collections.abc import Sequence
from typing import Any

import numpy as np

from src.core.models import Detection
from src.core.protocols import Detectable


class BatchProcessor:
    """Batch GPU processor for YOLO inference.

    Accumulates frames into batches and runs inference in a single
    forward pass for improved throughput on CUDA-capable devices.
    """

    def __init__(
        self,
        model_path: str = "yolov8x.pt",
        confidence: float = 0.3,
        classes: list[int] | None = None,
        batch_size: int = 8,
    ):
        self.model_path = model_path
        self.confidence = confidence
        self.classes = classes or [0, 32]
        self.batch_size = batch_size
        self.model: Any = None
        self.device = "cpu"
        self._frame_buffer: list[np.ndarray] = []
        self._timestamp_buffer: list[float] = []
        self._frame_id_buffer: list[int] = []

    def _init_model(self) -> Any | None:
        """Lazy-load the YOLO model with GPU detection."""
        if self.model is not None:
            return self.model

        try:
            import torch
            from ultralytics import YOLO

            self.model = YOLO(self.model_path)
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            return self.model
        except ImportError:
            print("ultralytics not installed; batch processing unavailable.")
            return None
        except Exception as e:
            print(f"YOLO model not loaded: {e}")
            return None

    def detect(self, image: np.ndarray) -> Sequence[Detectable]:
        """Detect objects in a single frame using batch processing."""
        detections = self.detect_batch([image])
        return detections[0] if detections else []

    def detect_batch(self, images: Sequence[np.ndarray]) -> list[list[Detection]]:
        """Run batch inference on multiple frames simultaneously.

        Returns a list of detection lists, one per input image.
        """
        model = self._init_model()
        if model is None:
            return [[] for _ in images]

        results = model(
            list(images),
            conf=self.confidence,
            classes=self.classes,
            verbose=False,
            device=self.device,
            batch=self.batch_size,
        )

        all_detections: list[list[Detection]] = []
        for result in results:
            detections: list[Detection] = []
            if len(result.boxes) == 0:
                all_detections.append(detections)
                continue

            boxes = result.boxes.xyxy.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy().astype(int)

            for bbox, conf, cls_id in zip(boxes, confidences, class_ids, strict=False):
                detections.append(
                    Detection(
                        bbox=bbox.tolist(),
                        class_id=int(cls_id),
                        confidence=float(conf),
                    )
                )
            all_detections.append(detections)

        return all_detections

    def queue_frame(
        self, image: np.ndarray, timestamp: float, frame_id: int
    ) -> list[list[Detection]] | None:
        """Queue a frame for batch processing.

        Returns detections for all buffered frames when the batch is full, None otherwise.
        """
        self._frame_buffer.append(image)
        self._timestamp_buffer.append(timestamp)
        self._frame_id_buffer.append(frame_id)

        if len(self._frame_buffer) >= self.batch_size:
            return self._flush()

        return None

        return None

    def flush(self) -> list[list[Detection]]:
        """Process all queued frames and return their detections."""
        return self._flush()

    def _flush(self) -> list[list[Detection]]:
        """Internal: process buffered frames."""
        if not self._frame_buffer:
            return []

        results = self.detect_batch(self._frame_buffer)
        self._frame_buffer.clear()
        self._timestamp_buffer.clear()
        self._frame_id_buffer.clear()
        return results

    @property
    def device_name(self) -> str:
        return self.device
