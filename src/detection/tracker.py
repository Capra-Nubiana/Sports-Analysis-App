"""
ByteTrack Integration using supervision.
Implements Tracker protocol.
"""

from collections.abc import Sequence

import numpy as np

from src.core.models import TrackedDetection
from src.core.protocols import Detectable, Trackable, Tracker


class ByteTrackerWrapper(Tracker):
    def __init__(
        self,
        track_thresh: float = 0.25,
        track_buffer: int = 30,
        match_thresh: float = 0.8,
        frame_rate: int = 30,
    ):
        try:
            import supervision as sv

            self.tracker = sv.ByteTrack(
                track_activation_threshold=track_thresh,
                lost_track_buffer=track_buffer,
                minimum_matching_threshold=match_thresh,
                frame_rate=frame_rate,
            )
        except ImportError:
            print("supervision not installed.")
            self.tracker = None

    def update(self, detections: Sequence[Detectable], image: np.ndarray) -> Sequence[Trackable]:
        if self.tracker is None or len(detections) == 0:
            return []

        try:
            import supervision as sv
        except ImportError:
            return []

        # Convert our abstract Detection to supervision Detections format
        bboxes = np.array([d.bbox for d in detections])
        confidences = np.array([d.confidence for d in detections])
        class_ids = np.array([d.class_id for d in detections])

        sv_detections = sv.Detections(
            xyxy=bboxes,
            confidence=confidences,
            class_id=class_ids,
        )

        tracked_sv = self.tracker.update_with_detections(sv_detections)

        tracked_results: list[TrackedDetection] = []
        for i in range(len(tracked_sv)):
            tracked_results.append(
                TrackedDetection(
                    bbox=tracked_sv.xyxy[i].tolist(),
                    class_id=int(tracked_sv.class_id[i]),
                    confidence=float(tracked_sv.confidence[i]),
                    track_id=int(tracked_sv.tracker_id[i]),
                )
            )

        return tracked_results
