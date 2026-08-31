from dataclasses import dataclass
from typing import Any

@dataclass
class DeviceCommand:
    room: str
    device: str
    action: str
    reason: str
    source: str