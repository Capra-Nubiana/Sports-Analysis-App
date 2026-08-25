"""
ANT+ streaming using openant.
"""

from collections.abc import Callable
from typing import Any

from src.core.models import SensorReading


class ANTStreamer:
    """Streams data from ANT+ devices (e.g. Heart Rate Monitors)."""

    def __init__(self, device_type: str = "hrm"):
        self.device_type = device_type
        self.node: Any | None = None
        self.is_streaming = False

    def start_stream(self, callback: Callable[[SensorReading], None]) -> None:
        try:
            from openant.devices import ANTPLUS_NETWORK_KEY
            from openant.devices.heart_rate import HeartRate
            from openant.easy.node import Node
        except ImportError:
            print("openant not installed. Cannot start ANT+ stream.")
            return

        self.node = Node()
        self.node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)

        device = HeartRate(self.node)
        self.is_streaming = True

        def on_device_data(page: int, page_name: str, data: Any) -> None:
            import time

            if page_name == "main":
                reading = SensorReading(
                    timestamp=time.time(),
                    source_type="ant",
                    data={"heart_rate": data.get("heart_rate", 0)},
                )
                callback(reading)

        device.on_device_data = on_device_data

        try:
            self.node.start()
        except KeyboardInterrupt:
            self.stop_stream()

    def stop_stream(self) -> None:
        self.is_streaming = False
        if self.node:
            self.node.stop()
