import { useEffect, useRef, useState } from "react";
import api from "./api";
import AIStatus from "./components/AIStatus";
import DigitalTwin3D from "./DigitalTwin3D";

function App() {

  const [sensor, setSensor] = useState(null);
  const [analysis, setAnalysis] = useState("");
  const [alert, setAlert] = useState(null);
  const [aiRecommendation, setAiRecommendation] = useState(null);
  const [
    selectedObject,
    setSelectedObject
  ] = useState(null);
  const selectedDevice =
    selectedObject?.deviceId;
  const socketRef =
    useRef(null);

  async function loadSensor() {
    const res = await api.get("/sensor/latest");
    setSensor(res.data);
  }

  // useEffect(() => {
  //   loadSensor();
  //   const timer = setInterval(loadSensor, 1000);
  //   return () => clearInterval(timer);
  // }, []);

  function sendCommand(
    device,
    action
  ) {

    if (
      !socketRef.current ||
      socketRef.current.readyState
      !== WebSocket.OPEN
    ) {

      console.error(
        "WebSocket not connected"
      );

      return;
    }

    const command = {
      type: "command",
      data: {
        room: "meeting_room",
        device: device,
        action: action,
        source: "user"
      }
    };

    socketRef.current.send(
      JSON.stringify(command)
    );

  }

  useEffect(() => {
    const socket = new WebSocket("ws://127.0.0.1:8000/ws");


    socketRef.current =
      socket;

    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === "twin_state") {
        setSensor(message.data);
      }
      if (message.type === "alert") {
        setAlert(message.data);
      }
      if (message.type === "ai_recommendation") {
        setAiRecommendation(message.data);
      }
    }

    socket.onopen = () => {
      setInterval(() => {
        socket.send("ping")
      }, 30000)
    }

    return () => socket.close();

  }, []);

  if (!sensor) {
    return <h2>Loading...</h2>;
  }

  const hot = sensor.temperature > 27;

  function SensorCard({ title, value }) {

    return (
      <div
        style={{
          width: 220,
          border: "1px solid #ddd",
          borderRadius: 12,
          padding: 20
        }}
      >
        <h2>{title}</h2>
        <h1>{value}</h1>
      </div>
    )

  }

  function roomStatus(sensor) {
    if (sensor.temperature > 28)
      return "🔥 Room is Hot";

    if (sensor.humidity > 70)
      return "💧 Humidity High";

    return "✅ Comfortable";
  }

  async function getAI() {

    const response =
      await api.post(
        "/ai/analyze",
        sensor
      );

    setAnalysis(
      response.data.analysis
    );

  }

  return (

    <div style={{ padding: 40 }}>

      <h1>Smart Room Digital Twin</h1>

      <h2>{sensor.room}</h2>

      <DigitalTwin3D onObjectSelected={setSelectedObject} />
      <div>

        <h2>
          Selected Object
        </h2>

        {selectedObject && (

          <div>

            <p>
              Device:
              {
                selectedObject
                  .deviceId
              }
            </p>

            <p>
              Type:
              {
                selectedObject
                  .type
              }
            </p>

            <p>
              Room:
              {
                selectedObject
                  .room
              }
            </p>


            {selectedDevice === "ac-001" && (
              <div style={{ marginTop: "10px", display: "flex", gap: "10px" }}>
                <button
                  onClick={() =>
                    sendCommand(
                      "air_conditioner",
                      "turn_on"
                    )
                  }
                >
                  Turn ON
                </button>
                <button
                  onClick={() =>
                    sendCommand(
                      "air_conditioner",
                      "turn_off"
                    )
                  }
                >
                  Turn OFF
                </button>
              </div>
            )}

          </div>

        )}

      </div>

      <h2>{roomStatus(sensor)}</h2>

      <div style={{ display: "flex", gap: 20 }}>

        <SensorCard
          title="Temperature"
          value={`${sensor.temperature}°C`}
        />

        <SensorCard
          title="Humidity"
          value={`${sensor.humidity}%`}
        />

        <SensorCard
          title="Light"
          value={sensor.light}
        />

      </div>
      {alert && (
        <div>
          <h2>⚠️ {alert.severity}</h2>
          <p>{alert.message}</p>
        </div>
      )}

      {aiRecommendation && (
        <div>
          <h2>AI Recommendation</h2>
          <p>{aiRecommendation.recommendation}</p>
        </div>
      )}

      <button onClick={getAI}>
        Analyze Room
      </button>
      <AIStatus message={analysis} />
    </div>

  )

}

export default App;