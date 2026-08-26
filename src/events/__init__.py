"""
Event detection package.

Sport-specific event detectors implementing the EventDetector protocol.
"""

from src.events.base import BaseEventDetector
from src.events.factory import EventDetectorFactory

__all__ = ["BaseEventDetector", "EventDetectorFactory"]
