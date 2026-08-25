"""
Homography (Perspective Transform) Mapper.
Maps 2D pixel coordinates to real-world metric coordinates.
"""

import cv2
import numpy as np


class HomographyMapper:
    """Projects pixel positions to a 2D pitch map."""

    def __init__(self) -> None:
        self.H: np.ndarray | None = None

    def calibrate(
        self, src_pts: list[tuple[float, float]], dst_pts: list[tuple[float, float]]
    ) -> bool:
        """
        Calibrate homography matrix H.
        src_pts: Points in pixel coordinates.
        dst_pts: Corresponding points in meter coordinates.
        """
        if len(src_pts) < 4 or len(dst_pts) < 4:
            return False

        src = np.array(src_pts, dtype=np.float32)
        dst = np.array(dst_pts, dtype=np.float32)

        self.H, _ = cv2.findHomography(src, dst)
        return self.H is not None

    def transform(self, x: float, y: float) -> tuple[float, float]:
        """Transform a single point."""
        if self.H is None:
            return (x, y)  # Fallback to pixel coords

        pt = np.array([[[x, y]]], dtype=np.float32)
        dst_pt = cv2.perspectiveTransform(pt, self.H)
        return (float(dst_pt[0][0][0]), float(dst_pt[0][0][1]))

    def get_bottom_center(self, bbox: list[float]) -> tuple[float, float]:
        """Convert a bounding box [x1, y1, x2, y2] to its bottom center pixel coordinate."""
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2.0, y2)
