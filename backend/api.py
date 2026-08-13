# from digital_twin.SmartRoomTwin import database
import asyncio
from fastapi import FastAPI
from models import SensorData
from database import engine
from db_models import Base
from database import SessionLocal
from db_models import SensorRecord
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket
from websocket_manager import manager
from ai_agent import ai_agent

from contextlib import asynccontextmanager
import threading

from mqtt_client import mqtt_subscriber
from twin_engine import twin_engine

# app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):

    # thread = threading.Thread(
    #     target=mqtt_subscriber.start,
    #     daemon=True
    # )

    # thread.start()

    loop = asyncio.get_running_loop()

    twin_engine.set_event_loop(loop)

    mqtt_subscriber.start_in_background()

    yield

app = FastAPI(lifespan=lifespan)

Base.metadata.create_all(bind=engine)

latest_sensor = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Smart Room Digital Twin"
    }


@app.post("/sensor")
async def receive_sensor(data: SensorData):

    db = SessionLocal()

    record = SensorRecord(
        room=data.room,
        sensor_id=data.sensor_id,
        timestamp=data.timestamp,
        temperature=data.temperature,
        humidity=data.humidity,
        light=data.light
    )

    db.add(record)
    db.commit()

    await manager.broadcast(data.model_dump())    

    db.close()

    return {
        "status": "saved"
    }    


@app.get("/sensor/latest")
def latest():

    # global latest_sensor

    # if latest_sensor is None:
    #     return {
    #         "message": "No data yet"
    #     }

    # return latest_sensor
    db = SessionLocal()

    row = (
        db.query(SensorRecord)
        .order_by(SensorRecord.id.desc())
        .first()
    )        
    return row


@app.get("/history")
def history():

    db = SessionLocal()

    rows = db.query(SensorRecord).all()
    # row = (
    #     db.query(SensorRecord)
    #     .order_by(SensorRecord.id.desc())
    #     .first()
    # )    

    db.close()

    return rows
    # return row

@app.get("/history/high-temp")
def high_temp():

    db = SessionLocal()

    rows = (
        db.query(SensorRecord)
          .filter(SensorRecord.temperature > 27)
          .all()
    )

    db.close()

    return rows    

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()

    except Exception:
        manager.disconnect(websocket)    

@app.post("/ai/analyze")
def ai_analysis(data: SensorData):
    print(156, data.model_dump())
    result = ai_agent.analyze_room(data.model_dump())

    return {

        "analysis": result

    }        

@app.get("/twin/{room}")
def get_twin(room: str):

    state = twin_engine.get_room(room)

    if state is None:

        return {
            "error": "Room not found"
        }

    return state    