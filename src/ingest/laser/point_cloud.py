"""
Point Cloud Processing using PDAL and LasPy
"""

from pathlib import Path


class PointCloudProcessor:
    """Processes LAS/LAZ files to extract terrain vs objects."""

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)

    def filter_ground(self) -> None:
        """Use PDAL to run a Simple Morphological Filter (SMRF) to remove ground points."""
        try:
            import pdal
        except ImportError:
            print("PDAL not installed. Install via conda: conda install -c conda-forge python-pdal")
            return

        json_pipeline = f"""
        [
            "{str(self.filepath)}",
            {{
                "type":"filters.smrf"
            }},
            {{
                "type":"filters.range",
                "limits":"Classification![2:2]"
            }},
            "output_no_ground.las"
        ]
        """
        pipeline = pdal.Pipeline(json_pipeline)
        pipeline.execute()

    def read_laspy(self) -> None:
        try:
            import laspy

            las = laspy.read(self.filepath)
            print(f"Loaded {len(las.points)} points from {self.filepath.name}")
            # Do object clustering here
        except ImportError:
            print("LasPy not installed.")
