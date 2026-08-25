"""
LiDAR Data Source using Open3D.
"""

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core.protocols import DataSource, SourceFrame


@dataclass
class LiDARFrame(SourceFrame):
    _timestamp: float
    _frame_id: int
    point_cloud: Any  # open3d.geometry.PointCloud

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def frame_id(self) -> int:
        return self._frame_id


class LiDARSource(DataSource):
    """Streams PointCloud frames from a directory of LiDAR files or a live sensor."""

    def __init__(self, data_path: str, fps: float = 10.0):
        self.data_path = Path(data_path)
        self.fps = fps
        self.files: list[Path] = []

    def open(self) -> bool:
        if self.data_path.is_dir():
            self.files = sorted(
                list(self.data_path.glob("*.pcd")) + list(self.data_path.glob("*.ply"))
            )
            return len(self.files) > 0
        return False

    def close(self) -> None:
        self.files = []

    def iter_frames(self) -> Iterator[LiDARFrame]:
        try:
            import open3d as o3d
        except ImportError:
            print("open3d not installed.")
            return

        interval = 1.0 / self.fps
        current_time = 0.0

        for i, f in enumerate(self.files):
            pcd = o3d.io.read_point_cloud(str(f))
            yield LiDARFrame(_timestamp=current_time, _frame_id=i, point_cloud=pcd)
            current_time += interval
