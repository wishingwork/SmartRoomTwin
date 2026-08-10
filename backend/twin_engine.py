from database import SessionLocal
from db_models import SensorRecord
import asyncio

from websocket_manager import manager


class TwinEngine:

    def __init__(self):

        self.rooms = {}
        self.event_loop = None

    def set_event_loop(self, loop):

        self.event_loop = loop        

    def update_sensor(self, sensor):

        room = sensor["room"]

        # -------------------------
        # 1. Update digital state
        # -------------------------
        self.rooms[room] = sensor

        # -------------------------
        # 2. Save telemetry
        # -------------------------
        self.save_history(sensor)

        # -------------------------
        # 3. Notify clients
        # -------------------------
        if self.event_loop:
            asyncio.run_coroutine_threadsafe(
                manager.broadcast(sensor),
                self.event_loop
            )

    def save_history(self, sensor):

        db = SessionLocal()

        record = SensorRecord(
            room=sensor["room"],
            sensor_id=sensor["sensor_id"],
            timestamp=sensor["timestamp"],
            temperature=sensor["temperature"],
            humidity=sensor["humidity"],
            light=sensor["light"]
        )

        db.add(record)
        db.commit()
        db.close()

    def get_room(self, room):

        return self.rooms.get(room)    
        
twin_engine = TwinEngine()