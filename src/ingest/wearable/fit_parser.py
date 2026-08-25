"""
Garmin/ANT+ .FIT file parsing using fitdecode.
"""

import fitdecode
import datetime
from typing import List, Dict, Any, Iterator
from pathlib import Path
from src.core.models import SensorReading
from src.core.protocols import DataSource, SourceFrame
from dataclasses import dataclass

@dataclass
class FITFrame(SourceFrame):
    _timestamp: float
    _frame_id: int
    readings: List[SensorReading]
    
    @property
    def timestamp(self) -> float: return self._timestamp
    @property
    def frame_id(self) -> int: return self._frame_id

class FITParser(DataSource):
    """Parses .FIT files (e.g., from Garmin devices) into a stream of SensorReadings."""
    
    def __init__(self, fit_filepath: str):
        self.filepath = Path(fit_filepath)
        self.is_open = False
        self.fit_data: List[SensorReading] = []
        self._load_data()
        
    def _load_data(self) -> None:
        """Load all records from FIT file into memory."""
        if not self.filepath.exists():
            return
            
        self.fit_data = []
        with fitdecode.FitReader(str(self.filepath)) as fit:
            for frame in fit:
                if isinstance(frame, fitdecode.FitDataMessage) and frame.name == "record":
                    timestamp_field = frame.get_field('timestamp')
                    if not timestamp_field or not timestamp_field.value:
                        continue
                        
                    # FIT timestamps are datetime objects
                    dt = timestamp_field.value
                    if isinstance(dt, datetime.datetime):
                        ts = dt.timestamp()
                        
                        data_dict = {}
                        for field in frame.fields:
                            if field.name != 'timestamp' and field.value is not None:
                                data_dict[field.name] = field.value
                        
                        self.fit_data.append(
                            SensorReading(
                                timestamp=ts, 
                                source_type="fit", 
                                data=data_dict
                            )
                        )
                        
        # Sort by timestamp
        self.fit_data.sort(key=lambda x: x.timestamp)

    def open(self) -> bool:
        self.is_open = len(self.fit_data) > 0
        return self.is_open
        
    def close(self) -> None:
        self.is_open = False
        self.fit_data.clear()
        
    def iter_frames(self) -> Iterator[FITFrame]:
        if not self.is_open:
            raise RuntimeError("FITParser is not open/loaded.")
            
        for i, reading in enumerate(self.fit_data):
            # Batch them into "frames" if needed, but here we just yield 1 per "frame"
            yield FITFrame(_timestamp=reading.timestamp, _frame_id=i, readings=[reading])
