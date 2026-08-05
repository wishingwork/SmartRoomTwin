import ollama


def analyze_room(sensor):

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