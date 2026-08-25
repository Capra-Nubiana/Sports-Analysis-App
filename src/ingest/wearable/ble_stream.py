"""
Live BLE Streaming using Bleak.
For real-time HR and wearable metrics.
"""

import asyncio
from typing import Callable, Iterator, Any, Optional
# import bleak  # Disabling import at top level to allow sync pipeline run without BLE hardware
from src.core.models import SensorReading

class BLEStreamer:
    """Async BLE streamer for live data."""
    
    def __init__(self, device_address: str, characteristics: list[str]):
        self.device_address = device_address
        self.characteristics = characteristics
        self.client: Optional[Any] = None
        self.is_streaming = False
        
    async def connect(self) -> bool:
        import bleak
        self.client = bleak.BleakClient(self.device_address)
        try:
            await self.client.connect()
            return self.client.is_connected
        except Exception as e:
            print(f"BLE Connect failed: {e}")
            return False
            
    async def disconnect(self) -> None:
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            
    async def start_stream(self, callback: Callable[[SensorReading], None]) -> None:
        if not self.client or not self.client.is_connected:
            return
            
        self.is_streaming = True
        
        def notification_handler(sender: int, data: bytearray) -> None:
            # Decode standard HR (0x2A37) as an example
            import time
            hr_value = int(data[1]) if len(data) > 1 else 0
            
            reading = SensorReading(
                timestamp=time.time(),
                source_type="ble",
                data={"heart_rate": hr_value}
            )
            callback(reading)

        for char_uuid in self.characteristics:
            await self.client.start_notify(char_uuid, notification_handler)
            
        while self.is_streaming and self.client.is_connected:
            await asyncio.sleep(1.0)
            
    def stop_stream(self) -> None:
        self.is_streaming = False
