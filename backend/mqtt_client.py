import asyncio
import json
import threading

import paho.mqtt.client as mqtt

from twin_engine import twin_engine
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

        twin_engine.update_sensor(sensor)


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