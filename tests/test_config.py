"""
Test robust YAML configuration loading.
"""

from src.core.sport_config import SportConfig


def test_load_football_config():
    config = SportConfig("football", config_dir="config")

    # Base attributes
    assert config.get("video.target_fps") == 30
    assert config.get("detection.classes") == [0, 32]

    # Overridden attributes
    assert config.get("spatial.pitch_dimensions.length") == 105.0


def test_missing_config_returns_default():
    config = SportConfig("football", config_dir="config")
    assert config.get("non_existent.key", default="fallback") == "fallback"
