import json

import paho.mqtt.client as mqtt
from command_models import DeviceCommand


class CommandEngine:

    def __init__(self):
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2
        )

    def validate(self, command):
        if command.device == "air_conditioner":
            if command.action not in [
                "turn_on",
                "turn_off"
            ]:
                return False
        return True

    def execute(self, command):

        if not self.validate(command):
            print("Command rejected:", command)
            return False

        topic = f"building/meeting_room/command"

        payload = {
            "device": command.device,
            "action": command.action,
            "reason": command.reason,
            "source": command.source
        }

        self.client.connect("localhost",1883)

        self.client.publish(topic, json.dumps(payload))

        self.client.disconnect()

        print("Command sent:", payload)

        return True

command_engine = CommandEngine()