class RuleEngine:

    def __init__(self):
        self.active_alerts = set()

    def evaluate(self, state):

        alerts = []

        self.check_temperature(
            state,
            alerts
        )

        self.check_humidity(
            state,
            alerts
        )

        return alerts    

    def check_temperature(
        self,
        state,
        alerts
    ):

        key = (
            state.room,
            "high_temperature"
        )

        is_high = (
            state.temperature is not None
            and state.temperature > 30
        )

        if is_high:
            if key not in self.active_alerts:
                self.active_alerts.add(key)
                alerts.append({
                    "type":
                        "high_temperature",
                    "severity":
                        "warning",
                    "status":
                        "active",
                    "message":
                        "Temperature is above 30°C."
                })
        else:
            if key in self.active_alerts:
                self.active_alerts.remove(key)
                alerts.append({
                    "type":
                        "high_temperature",
                    "severity":
                        "info",
                    "status":
                        "resolved",
                    "message":
                        "Temperature returned to normal."
                })

    def check_humidity(self, state, alerts):
        key = (
            state.room,
            "high_humidity"
        )

        is_high = (
            state.humidity is not None
            and state.humidity > 70
        )

        if is_high:
            if key not in self.active_alerts:
                self.active_alerts.add(key)
                alerts.append({
                    "type":
                        "high_humidity",
                    "severity":
                        "warning",
                    "status":
                        "active",
                    "message":
                        "Humidity is above 70%."
                })
        else:
            if key in self.active_alerts:
                self.active_alerts.remove(key)
                alerts.append({
                    "type":
                        "high_humidity",
                    "severity":
                        "info",
                    "status":
                        "resolved",
                    "message":
                        "Humidity returned to normal."
                })

    def get_commands(self, state):

        commands = []

        if (
            state.temperature is not None
            and state.temperature > 25
            and state.humidity is not None
            and state.humidity > 30
            and state.air_conditioner != "ON"
        ):

            commands.append({
                "device":
                    "air_conditioner",
                "action":
                    "turn_on",
                "reason":
                    "High temperature and humidity",
                "source":
                    "rule"
            })
        
        if (
            state.temperature is not None
            and state.temperature < 25
            and state.air_conditioner != "OFF"
        ):

            commands.append({
                "device":
                    "air_conditioner",
                "action":
                    "turn_off",
                "reason":
                    "Low temperature and humidity",
                "source":
                    "rule"
            })

        return commands

rule_engine = RuleEngine()        