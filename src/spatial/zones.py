"""
Spatial zones and polygon matching based on sport configuration.
"""

from src.core.sport_config import SportConfig


class ZoneManager:
    """Manages sport-specific zones and tests point inclusion.

    Supports both polygon zones (list of [x, y] vertex pairs) and
    point zones (a single [x, y] coordinate).
    """

    def __init__(self, config: SportConfig):
        self.zones: dict[str, list[tuple[float, float]]] = {}
        self.point_zones: dict[str, tuple[float, float]] = {}
        zones_data = config.get("spatial.zones", {})
        for name, points in zones_data.items():
            if self._is_point_zone(points):
                self.point_zones[name] = (float(points[0]), float(points[1]))
            else:
                self.zones[name] = [tuple(pt) for pt in points]

    @staticmethod
    def _is_point_zone(points: list) -> bool:
        """Return True if the zone is a single [x, y] point, not a polygon."""
        return len(points) == 2 and all(isinstance(v, (int, float)) for v in points)

    def point_in_zone(self, point: tuple[float, float], zone_name: str) -> bool:
        """Test if a physical point is inside a named zone (polygon or point)."""
        if zone_name in self.point_zones:
            px, py = self.point_zones[zone_name]
            return (float(point[0]), float(point[1])) == (px, py)

        if zone_name not in self.zones:
            return False

        import cv2
        import numpy as np

        polygon = np.array(self.zones[zone_name], dtype=np.float32)
        pt = (float(point[0]), float(point[1]))

        # Returns +1 if inside, 0 if on contour, -1 if outside
        dist = cv2.pointPolygonTest(polygon, pt, measureDist=False)
        return dist >= 0
