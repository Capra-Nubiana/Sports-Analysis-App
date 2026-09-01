"""
YOLO Object Detection Wrapper
Implements Detector protocol.
Supports both PyTorch (.pt) and ONNX (.onnx) backends.
"""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

import numpy as np

from src.core.models import Detection
from src.core.protocols import Detectable, Detector

if TYPE_CHECKING:
    import onnxruntime as ort


class YOLODetector(Detector):
    def __init__(
        self,
        model_path: str = "yolov8x.pt",
        confidence: float = 0.3,
        classes: list[int] | None = None,
        imgsz: int = 1280,
    ):
        self.confidence = confidence
        self.classes = classes or [0, 32]  # Default: Person, Sports ball
        self.model: Any = None
        self.device = "cpu"
        self.imgsz = imgsz
        self.is_onnx = False
        self.session: ort.InferenceSession | None = None
        self.input_name: str | None = None
        self.output_names: list[str] | None = None

        model_lower = model_path.lower()
        if model_lower.endswith(".onnx"):
            self._init_onnx(model_path)
        else:
            self._init_torch(model_path)

    def _init_onnx(self, model_path: str) -> None:
        """Initialize ONNX Runtime backend."""
        try:
            import onnxruntime as ort

            session = ort.InferenceSession(model_path)
            self.session = session
            if self.session is not None:
                self.input_name = session.get_inputs()[0].name
                self.output_names = [o.name for o in session.get_outputs()]
            self.is_onnx = True
        except ImportError:
            print("onnxruntime not installed.")
            self.session = None
        except Exception as e:
            print(f"ONNX model not loaded: {e}")
            self.session = None

    def _init_torch(self, model_path: str) -> None:
        """Initialize PyTorch/Ultralytics backend."""
        try:
            import torch
            from ultralytics import YOLO

            self.model = YOLO(model_path)
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            if self.model is not None:
                self.model.to(self.device)
        except ImportError:
            print("ultralytics YOLO not installed. Trying ONNX fallback...")
            if model_path.lower().endswith(".onnx"):
                self._init_onnx(model_path)
            else:
                self.model = None
        except Exception as e:
            print(f"YOLO model not loaded: {e}")
            self.model = None

    def _preprocess(self, image: np.ndarray) -> tuple[np.ndarray, float]:
        """Resize and normalize image for ONNX inference."""
        import cv2

        h, w = image.shape[:2]
        scale = self.imgsz / max(h, w)

        img_resized = cv2.resize(image, (self.imgsz, self.imgsz))
        img_rgb = img_resized.astype(np.float32) / 255.0
        img_chw = np.transpose(img_rgb, (2, 0, 1))
        img_batched = np.expand_dims(img_chw, axis=0)
        return img_batched, scale

    def _postprocess(
        self, output: np.ndarray, scale: float, original_shape: tuple
    ) -> list[Detection]:
        """Parse YOLOv8 ONNX output into Detection objects.

        YOLOv8 ONNX export (end2end=False, nms=False) outputs:
        [batch, 4+nc, num_anchors] where 4=bbox(cx,cy,w,h), nc=class logits
        (objectness is folded into class scores, no separate obj channel)

        Bbox values are in the model's input image coordinate space.
        Class scores are raw logits needing sigmoid.
        """
        import numpy as np

        pred = output[0]  # [7, 33600]
        pred = np.transpose(pred)  # [33600, 7]
        bboxes = pred[:, :4]  # [N, 4] cx, cy, w, h
        class_logits = pred[:, 4:]  # [N, nc]

        class_scores = 1.0 / (1.0 + np.exp(-class_logits))  # sigmoid
        confs = np.max(class_scores, axis=1)  # [N]
        class_ids = np.argmax(class_scores, axis=1)  # [N]

        mask = confs > self.confidence
        if self.classes:
            class_mask = np.isin(class_ids, self.classes)
            mask = mask & class_mask

        bboxes = bboxes[mask]
        confs = confs[mask]
        class_ids = class_ids[mask]

        if len(bboxes) == 0:
            return []

        # Convert cx,cy,w,h → x1,y1,x2,y2
        cx = bboxes[:, 0]
        cy = bboxes[:, 1]
        w = bboxes[:, 2]
        h = bboxes[:, 3]
        x1 = cx - w / 2
        y1 = cy - h / 2
        x2 = cx + w / 2
        y2 = cy + h / 2

        # Scale from model input space to original image
        x1 = x1 / scale
        y1 = y1 / scale
        x2 = x2 / scale
        y2 = y2 / scale

        # Apply NMS
        boxes_for_nms = np.stack([x1, y1, x2, y2], axis=1)
        keep_indices = self._nms(boxes_for_nms, confs)
        keep_indices = keep_indices[:100]

        detections: list[Detection] = []
        for idx in keep_indices:
            detections.append(
                Detection(
                    bbox=[float(x1[idx]), float(y1[idx]), float(x2[idx]), float(y2[idx])],
                    class_id=int(class_ids[idx]),
                    confidence=float(confs[idx]),
                )
            )

        return detections

    def _nms(self, boxes: np.ndarray, scores: np.ndarray, iou_thresh: float = 0.5) -> np.ndarray:
        """Standard NMS implementation returning indices of kept boxes."""
        if len(boxes) == 0:
            return np.array([], dtype=int)

        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = np.argsort(scores)[::-1]

        keep = []
        while len(order) > 0:
            i = order[0]
            keep.append(i)

            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0.0, xx2 - xx1 + 1)
            h = np.maximum(0.0, yy2 - yy1 + 1)
            inter = w * h
            iou = inter / (areas[i] + areas[order[1:]] - inter)

            order = order[1:][iou <= iou_thresh]

        return np.array(keep, dtype=int)

    def detect(self, image: np.ndarray) -> Sequence[Detectable]:
        if self.is_onnx:
            return self._detect_onnx(image)
        return self._detect_torch(image)

    def _detect_onnx(self, image: np.ndarray) -> list[Detection]:
        if self.session is None:
            return []

        original_shape = image.shape
        input_tensor, scale = self._preprocess(image)

        outputs = self.session.run(self.output_names, {self.input_name: input_tensor})
        output = outputs[0]

        return self._postprocess(output, scale, original_shape)

    def _detect_torch(self, image: np.ndarray) -> list[Detection]:
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
