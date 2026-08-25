"""
Configuration Loader
Loads base.yaml + sport.yaml and provides typed access.
"""

from pathlib import Path
from typing import Any

import yaml


class SportConfig:
    def __init__(self, sport_name: str, config_dir: str = "config"):
        self.sport_name = sport_name
        self.config_dir = Path(config_dir)
        self.data: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        """Merge base.yaml and {sport}.yaml."""
        base_path = self.config_dir / "base.yaml"
        sport_path = self.config_dir / f"{self.sport_name}.yaml"

        if not base_path.exists():
            raise FileNotFoundError(f"Base config not found at {base_path}")

        with open(base_path) as f:
            config: dict[str, Any] = yaml.safe_load(f) or {}

        if sport_path.exists():
            with open(sport_path) as f:
                sport_config = yaml.safe_load(f) or {}
                config = self._deep_merge(config, sport_config)

        return config

    def _deep_merge(self, base_dict: dict, override_dict: dict) -> dict:
        """Deep merge dictionaries."""
        merged = base_dict.copy()
        for key, value in override_dict.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    def get(self, key_path: str, default: Any = None) -> Any:
        """Fetch config using dot notation (e.g. 'detection.confidence_threshold')."""
        keys = key_path.split(".")
        value = self.data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
