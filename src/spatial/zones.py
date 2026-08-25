"""
Spatial zones and polygon matching based on sport configuration.
"""

from src.core.sport_config import SportConfig


class ZoneManager:
    """Manages sport-specific zones and tests point inclusion."""

    def __init__(self, config: SportConfig):
        self.zones: dict[str, list[tuple[float, float]]] = {}
        # load from config: config.get("spatial.zones", {})
        zones_data = config.get("spatial.zones", {})
        for name, points in zones_data.items():
            self.zones[name] = [tuple(pt) for pt in points]

    def point_in_zone(self, point: tuple[float, float], zone_name: str) -> bool:
        """Test if a physical point is inside a named zone polygon using OpenCV."""
        import cv2
        import numpy as np

        if zone_name not in self.zones:
            return False

        polygon = np.array(self.zones[zone_name], dtype=np.float32)
        pt = (float(point[0]), float(point[1]))

        # Returns +1 if inside, 0 if on contour, -1 if outside
        dist = cv2.pointPolygonTest(polygon, pt, measureDist=False)
        return dist >= 0
