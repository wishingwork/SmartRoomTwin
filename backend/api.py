from fastapi import FastAPI
from models import SensorData

app = FastAPI()

latest_sensor = None


@app.get("/")
def home():
    return {
        "message": "Smart Room Digital Twin"
    }


@app.post("/sensor")
def receive_sensor(data: SensorData):

    global latest_sensor

    latest_sensor = data

    return {
        "status": "received"
    }


@app.get("/sensor/latest")
def latest():

    global latest_sensor

    if latest_sensor is None:
        return {
            "message": "No data yet"
        }

    return latest_sensor