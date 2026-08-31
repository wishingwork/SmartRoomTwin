from command_engine import command_engine
from email import message
from dataclasses import asdict
from database import SessionLocal
from db_models import SensorRecord
import asyncio

from websocket_manager import manager
from twin_models import RoomState, TwinEvent
from rule_engine import rule_engine
from ai_agent import ai_agent
from command_models import DeviceCommand
from command_engine import command_engine

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
        old_state = self.rooms.get(room)
        new_state = self.build_new_state(old_state, sensor)
        self.rooms[room] = new_state        

        events = self.detect_events(old_state, new_state)

        # -------------------------
        # 2. Save telemetry
        # -------------------------
        self.save_history(sensor)

        # -------------------------
        # 3. Notify clients
        # -------------------------
        self.broadcast_state(new_state)

        commands = rule_engine.get_commands(
            new_state
        )
        for command_data in commands:
            command = DeviceCommand(
                room=room,
                device=command_data["device"],
                action=command_data["action"],
                reason=command_data["reason"],
                source=command_data["source"]
            )
            command_engine.execute(
                command
            )

        for event in events:
            self.handle_event(event)

        alerts = rule_engine.evaluate(new_state)

        if alerts:
            self.handle_alerts(alerts, new_state)

    def update_device(self, device):

        room = device["room"]
        state = self.rooms.get(room)
        if state is None:
            return

        if (
            device["device"]
            == "air_conditioner"
        ):
            state.air_conditioner = (
                device["state"]
            )

        self.broadcast_state(state)

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


    # -------------------------
    # Broadcast state
    # -------------------------
    def broadcast_state(self, state):
        if not self.event_loop:
            return

        message = {
            "type": "twin_state",
            "data": asdict(state)
        }

        asyncio.run_coroutine_threadsafe(
            manager.broadcast(message),
            self.event_loop
        )

    # -------------------------
    # Handle events
    # -------------------------

    def handle_event(self, event):
        print(
            "Twin Event:",
            event.event_type,
            event.room,
            event.data
        )

    def get_room(self, room):
        # return self.rooms.get(room)    
        state = self.rooms.get(room)
        if state is None:
            return None
        return asdict(state)        

    def build_new_state(
        self,
        old_state,
        sensor
    ):
        if old_state is None:
            return RoomState(
                room=sensor["room"],
                sensor_id=sensor["sensor_id"],
                timestamp=sensor["timestamp"],
                temperature=sensor.get("temperature"),
                humidity=sensor.get("humidity"),
                light=sensor.get("light")
            )
        return RoomState(
            room=old_state.room,
            sensor_id=sensor.get(
                "sensor_id",
                old_state.sensor_id
            ),
            timestamp=sensor.get(
                "timestamp",
                old_state.timestamp
            ),
            temperature=sensor.get(
                "temperature",
                old_state.temperature
            ),
            humidity=sensor.get(
                "humidity",
                old_state.humidity
            ),
            light=sensor.get(
                "light",
                old_state.light
            ),
            air_conditioner=sensor.get(
                "air_conditioner",
                old_state.air_conditioner
            )
        )            

    # -------------------------
    # Detect changes
    # -------------------------

    def detect_events(
        self,
        old_state,
        new_state
    ):

        events = []

        if old_state is None:
            return events

        if (
            old_state.temperature
            != new_state.temperature
        ):
            events.append(
                TwinEvent(
                    event_type=
                        "temperature_changed",
                    room=new_state.room,
                    timestamp=
                        new_state.timestamp,
                    data={
                        "old_value":
                            old_state.temperature,
                        "new_value":
                            new_state.temperature
                    }
                )
            )

        if (
            old_state.humidity
            != new_state.humidity
        ):
            events.append(
                TwinEvent(
                    event_type=
                        "humidity_changed",
                    room=new_state.room,
                    timestamp=
                        new_state.timestamp,
                    data={
                        "old_value":
                            old_state.humidity,
                        "new_value":
                            new_state.humidity
                    }
                )
            )

        if (
            old_state.light
            != new_state.light
        ):
            events.append(
                TwinEvent(
                    event_type=
                        "light_changed",
                    room=new_state.room,
                    timestamp=
                        new_state.timestamp,
                    data={
                        "old_value":
                            old_state.light,
                        "new_value":
                            new_state.light
                    }
                )
            )
        return events

    def handle_alert(self, alert, state):

        print(
            "ALERT:",
            alert["type"],
            alert["severity"],
            state.room
        )

        recommendation = ai_agent.analyze(
            state,
            [alert]
        )

        print("AI Recommendation:")
        print(recommendation)

        if self.event_loop:
            asyncio.run_coroutine_threadsafe(
                manager.broadcast(message),
                self.event_loop
            )

    def handle_alerts(self, alerts, state):

        for alert in alerts:

            self.broadcast_alert(
                alert,
                state
            )

        recommendation = ai_agent.analyze(
            state,
            alerts
        )

        self.broadcast_ai_recommendation(
            state,
            recommendation
        )

    def broadcast_alert(
        self,
        alert,
        state
    ):
        message = {
            "type": "alert",
            "data": {
                "room":
                    state.room,
                **alert
            }
        }

        if self.event_loop:
            asyncio.run_coroutine_threadsafe(
                manager.broadcast(message),
                self.event_loop
            )

    def broadcast_ai_recommendation(
        self,
        state,
        recommendation
    ):

        message = {
            "type":
                "ai_recommendation",
            "data": {
                "room":
                    state.room,
                "recommendation":
                    recommendation
            }
        }

        if self.event_loop:
            asyncio.run_coroutine_threadsafe(
                manager.broadcast(message),
                self.event_loop
            )

twin_engine = TwinEngine()