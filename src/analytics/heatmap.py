"""
Heatmap Generation

Generates player position heatmaps from tracked 2D coordinates
using numpy histogram binning.
"""

from typing import Any

import numpy as np


class HeatmapGenerator:
    """Generates spatial heatmaps from player tracking data."""

    def __init__(self, pitch_size: tuple[float, float] = (105.0, 68.0), bins: int = 50):
        self.pitch_size = pitch_size
        self.bins = bins

    def generate(self, positions: list[tuple[float, float]]) -> dict[str, Any]:
        """Generate a heatmap from a list of (x, y) positions in meters.

        Returns a dict with grid coordinates, weights, and summary stats.
        """
        if not positions:
            return {"grid": [], "x_edges": [], "y_edges": [], "total_points": 0, "max_density": 0.0}

        xs = [p[0] for p in positions]
        ys = [p[1] for p in positions]

        hist, x_edges, y_edges = np.histogram2d(
            xs, ys, bins=self.bins, range=[[0, self.pitch_size[0]], [0, self.pitch_size[1]]]
        )

        grid: list[list[float]] = hist.T.tolist()

        return {
            "grid": grid,
            "x_edges": x_edges.tolist(),
            "y_edges": y_edges.tolist(),
            "total_points": len(positions),
            "max_density": float(hist.max()),
            "mean_density": float(hist.mean()),
            "hotspot": [
                float(x_edges[np.argmax(hist[:, j])]) if hist[:, j].any() else 0.0
                for j in range(self.bins)
            ],
        }
