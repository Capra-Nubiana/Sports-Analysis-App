"""
Event Detector Factory

Creates sport-specific event detectors based on configuration.
"""

from src.core.sport_config import SportConfig
from src.events.base import BaseEventDetector
from src.events.basketball import BasketballEventDetector
from src.events.football import FootballEventDetector
from src.events.rugby import RugbyEventDetector


class EventDetectorFactory:
    """Factory that creates the correct EventDetector for a given sport."""

    _REGISTRY: dict[str, type[BaseEventDetector]] = {
        "football": FootballEventDetector,
        "rugby": RugbyEventDetector,
        "basketball": BasketballEventDetector,
    }

    @classmethod
    def supported_sports(cls) -> list[str]:
        return list(cls._REGISTRY.keys())

    @classmethod
    def create(cls, sport_name: str, config: SportConfig) -> BaseEventDetector:
        """Instantiate the appropriate event detector for the sport.

        Raises:
            ValueError: if the sport is not registered.
        """
        detector_cls = cls._REGISTRY.get(sport_name)
        if detector_cls is None:
            raise ValueError(
                f"No event detector registered for sport '{sport_name}'. "
                f"Supported: {cls.supported_sports()}"
            )
        return detector_cls(config)
