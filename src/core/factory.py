"""
Dependency Injection Container / Factory
Creates concrete implementations for protocols based on config.
"""

import importlib
from typing import Any

from src.core.protocols import DataSource, Detector, Tracker
from src.core.sport_config import SportConfig


class ComponentFactory:
    """Dependency Injection Container."""

    def __init__(self, sport_name: str, config_dir: str = "config"):
        self.config = SportConfig(sport_name, config_dir)
        self._registry: dict[str, Any] = {}

    def _instantiate(self, class_path: str, **kwargs: Any) -> Any:
        module_path, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        return cls(**kwargs)

    def create_video_source(self, video_path: str) -> DataSource:
        """Create OpenCV Video Source."""
        # Hardcoded for Phase 1, can be dynamic later
        from src.ingest.video_source import VideoSource

        return VideoSource(
            video_path=video_path,
            target_fps=self.config.get("video.target_fps", 30),
            skip_frames=self.config.get("video.skip_frames", 1),
        )

    def create_detector(self) -> Detector:
        """Create YOLO Detector."""
        from src.detection.detector import YOLODetector

        return YOLODetector(
            model_path=self.config.get("detection.model_path", "models/yolov8x.pt"),
            confidence=self.config.get("detection.confidence_threshold", 0.3),
            classes=self.config.get("detection.classes", [0, 32]),
        )

    def create_tracker(self) -> Tracker:
        """Create ByteTrack Tracker."""
        from src.detection.tracker import ByteTrackerWrapper

        return ByteTrackerWrapper(
            track_thresh=self.config.get("tracking.track_thresh", 0.25),
            track_buffer=self.config.get("tracking.track_buffer", 30),
            match_thresh=self.config.get("tracking.match_thresh", 0.8),
            frame_rate=self.config.get("tracking.frame_rate", 30),
        )

    def create_team_classifier(self) -> Any:
        """Create Team Classifier."""
        from src.detection.team_classifier import KMeansTeamClassifier

        return KMeansTeamClassifier(
            num_teams=self.config.get("team_classification.num_clusters", 3),
        )
