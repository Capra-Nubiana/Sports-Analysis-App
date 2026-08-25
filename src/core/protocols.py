"""
SOLID Core Abstractions — Protocol Definitions
Defines abstract interfaces for data sources, detectors, trackers, and biometrics.
"""

from typing import Protocol, List, Any, Optional, Dict, Iterator
from abc import abstractmethod
import numpy as np

class SourceFrame(Protocol):
    """Protocol for a synchronized frame of data from a source (video, LiDAR, wearable)."""
    @property
    def timestamp(self) -> float: ...
    @property
    def frame_id(self) -> int: ...
    
class DataSource(Protocol):
    """
    Interface Segregation: Streamable data source.
    Can be a video file, RTMP stream, BLE heart rate monitor, or LiDAR point cloud.
    """
    @abstractmethod
    def open(self) -> bool:
        """Initialize the data source."""
        ...
        
    @abstractmethod
    def close(self) -> None:
        """Release resources."""
        ...
        
    @abstractmethod
    def iter_frames(self) -> Iterator[SourceFrame]:
        """Yield frames/readings sequentially."""
        ...

class Detectable(Protocol):
    """Protocol for detection representation."""
    @property
    def bbox(self) -> np.ndarray: ... # [x1, y1, x2, y2]
    @property
    def class_id(self) -> int: ...
    @property
    def confidence(self) -> float: ...

class Trackable(Detectable, Protocol):
    """Protocol for a detection that has been assigned a tracking ID."""
    @property
    def track_id(self) -> int: ...

class Detector(Protocol):
    """
    Liskov Substitution: Swappable detection backend (YOLO, custom, etc.)
    """
    @abstractmethod
    def detect(self, image: np.ndarray) -> List[Detectable]:
        """Perform object detection on an image frame."""
        ...

class Tracker(Protocol):
    """
    Liskov Substitution: Swappable tracking backend (ByteTrack, BoT-SORT)
    """
    @abstractmethod
    def update(self, detections: List[Detectable], image: np.ndarray) -> List[Trackable]:
        """Update tracks given new detections."""
        ...

class EventDetector(Protocol):
    """
    Open/Closed: Abstract event detector. New sports add new detectors without modifying core.
    """
    @abstractmethod
    def process_frame(self, trackables: List[Trackable], spatial_map: Any) -> Optional[Any]:
        """Process current state and optionally return a detected event."""
        ...

class Measurable(Protocol):
    """
    Interface Segregation: Biometric/Wearable measurement metric.
    """
    @property
    def metric_name(self) -> str: ...
    @property
    def value(self) -> float: ...
    @property
    def unit(self) -> str: ...
