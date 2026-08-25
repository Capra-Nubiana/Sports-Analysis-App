"""
OpenCV Video Source
Implements DataSource protocol.
"""

from collections.abc import Iterator
from dataclasses import dataclass

import cv2
import numpy as np

from src.core.protocols import DataSource, SourceFrame


@dataclass
class VideoFrame(SourceFrame):
    _timestamp: float
    _frame_id: int
    image: np.ndarray

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def frame_id(self) -> int:
        return self._frame_id


class VideoSource(DataSource):
    def __init__(self, video_path: str, target_fps: int = 30, skip_frames: int = 1):
        self.video_path = video_path
        self.target_fps = target_fps
        self.skip_frames = max(1, skip_frames)

        self.cap: cv2.VideoCapture | None = None
        self.original_fps = 0.0
        self.total_frames = 0

    def open(self) -> bool:
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            return False

        self.original_fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return True

    def close(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def iter_frames(self) -> Iterator[VideoFrame]:
        if not self.cap or not self.cap.isOpened():
            raise RuntimeError("VideoSource is not open. Call open() first.")

        frame_id = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            if frame_id % self.skip_frames == 0:
                timestamp = frame_id / self.original_fps
                yield VideoFrame(_timestamp=timestamp, _frame_id=frame_id, image=frame)

            frame_id += 1
