from command_models import DeviceCommand
from command_engine import command_engine


command = DeviceCommand(
    room="meeting_room",
    device="air_conditioner",
    action="turn_on",
    reason="Room temperature is too high",
    source="rule"
)


command_engine.execute(command)