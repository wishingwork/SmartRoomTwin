from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, Float, String

class Base(DeclarativeBase):
    pass


class SensorRecord(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True)

    room = Column(String)
    sensor_id = Column(String)
    timestamp = Column(String)

    temperature = Column(Float)
    humidity = Column(Integer)

    light = Column(String)