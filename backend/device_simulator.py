import fractions
import json

import paho.mqtt.client as mqtt
from datetime import datetime


class DeviceSimulator:

    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(
        self,
        client,
        userdata,
        flags,
        reason_code,
        properties
    ):
        print("Device connected to MQTT")
        client.subscribe("building/meeting_room/command")

    def on_message(
        self,
        client,
        userdata,
        msg
    ):
        command = json.loads(msg.payload.decode())
        print("Device received:", command)
        self.execute(command)

    def execute(self, command):
        device = command["device"]
        action = command["action"]

        if device == "air_conditioner":
            if action in ["turn_on", "turn on"]:
                print("❄️ Air conditioner ON")
                self.client.publish(
                    "building/meeting_room/device_state",
                    json.dumps({
                        "room": "meeting_room",
                        "device": "air_conditioner",
                        "state": "ON"
                    })
                )   

            elif action in ["turn_off", "turn off"]:
                print("Air conditioner OFF")
                self.client.publish(
                    "building/meeting_room/device_state",
                    json.dumps({
                        "room": "meeting_room",
                        "device": "air_conditioner",
                        "state": "OFF"
                    })
                )

    def start(self):
        self.client.connect("localhost",1883)
        self.client.loop_forever()


device = DeviceSimulator()
device.start()