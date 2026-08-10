import asyncio
import json
import threading

import paho.mqtt.client as mqtt

from database import SessionLocal
from db_models import SensorRecord
from websocket_manager import manager


class MQTTSubscriber:

    def __init__(self):

        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2
        )

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.event_loop = None

    def set_event_loop(self, loop):

        self.event_loop = loop


    def on_connect(
        self,
        client,
        userdata,
        flags,
        reason_code,
        properties,
    ):

        print("Connected to MQTT")

        client.subscribe(
            "building/meeting_room/sensor"
        )

    def on_message(
        self,
        client,
        userdata,
        msg,
    ):

        # sensor = json.loads(msg.payload)

        # print(sensor)


        sensor = json.loads(
            msg.payload.decode()
        )

        print("MQTT received:")
        print(sensor)

        # -------------------------
        # Save to SQLite
        # -------------------------        

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
        # Broadcast to WebSocket
        # -------------------------
        if self.event_loop:
            asyncio.run_coroutine_threadsafe(
                manager.broadcast(sensor),
                self.event_loop
            )


    def start(self):

        self.client.connect("localhost",1883)
        self.client.loop_forever()

    def start_in_background(self):

        thread = threading.Thread(
            target=self.start,
            daemon=True
        )

        thread.start()

mqtt_subscriber = MQTTSubscriber()