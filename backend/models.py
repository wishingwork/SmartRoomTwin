from pydantic import BaseModel

class SensorData(BaseModel):
    room: str
    sensor_id: str
    timestamp: str
    temperature: float
    humidity: int
    light: str