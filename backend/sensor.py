import random
import json
import time
from datetime import datetime

temperature = 25.0
humidity = 60

while True:

    temperature += random.uniform(-0.3,0.3)

    humidity += random.randint(-2,2)

    humidity = max(30,min(90,humidity))

    sensor = {
        "room":"Meeting Room",
        "sensor_id":"TEMP001",
        "timestamp": datetime.now().isoformat(),
        "temperature": round(temperature,1),
        "humidity": humidity,
        "light": random.choice(["ON","OFF"])
    }    

    print(json.dumps(sensor, indent=4))

    time.sleep(1)