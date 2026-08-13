import json
import ollama

class AIAgent:

    def __init__(self):
        self.model = "qwen:latest"

    def build_prompt(self, state, alerts):

        context = {
            "room": state.room,
            "temperature":
                state.temperature,
            "humidity":
                state.humidity,
            "light":
                state.light,
            "alerts":
                alerts
        }

        return f"""
You are a Digital Twin AI assistant.

Analyze the current state of a physical room.

Do not invent sensor values.

Current Digital Twin state:

{json.dumps(context, indent=2)}

Provide:

1. Situation assessment
2. Possible cause
3. Recommended action
4. Whether human intervention is required

Keep the answer concise.
"""

    def analyze(self, state, alerts):
        prompt = self.build_prompt(
            state,
            alerts
        )
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return response["message"]["content"]


    def analyze_room(self, sensor):

        prompt = f"""
    You are a smart building assistant.

    Analyze this room data:

    Temperature:
    {sensor["temperature"]} °C

    Humidity:
    {sensor["humidity"]} %

    Light:
    {sensor["light"]}

    Give:
    1. Current condition
    2. Possible problem
    3. Recommendation

    Keep answer short.
    """

        response = ollama.chat(

            model="qwen:latest",

            messages=[
                {
                    "role":"user",
                    "content":prompt
                }
            ]

        )

        return response["message"]["content"]

ai_agent = AIAgent()