from dataclasses import dataclass
from typing import Optional
from typing import Any

@dataclass
class RoomState:
    room: str
    sensor_id: str
    timestamp: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    light: Optional[str] = None


@dataclass
class TwinEvent:
    event_type: str
    room: str
    timestamp: str
    data: dict[str, Any]