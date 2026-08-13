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

rule_engine = RuleEngine()        