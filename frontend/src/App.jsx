import { useEffect, useState } from "react";
import api from "./api";
import AIStatus from "./components/AIStatus";

function App() {

  const [sensor, setSensor] = useState(null);
  const [analysis, setAnalysis] = useState("");

  async function loadSensor() {

    const res = await api.get("/sensor/latest");

    setSensor(res.data);
  }

  // useEffect(() => {

  //   loadSensor();

  //   const timer = setInterval(loadSensor, 1000);

  //   return () => clearInterval(timer);

  // }, []);

  useEffect(() => {

    const socket =
      new WebSocket("ws://127.0.0.1:8000/ws");

    socket.onmessage = (event) => {

      const sensor =
        JSON.parse(event.data);

      setSensor(sensor);

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

      <h2>

        {roomStatus(sensor)}

      </h2>
      <div
        style={{
          display: "flex",
          gap: 20
        }}
      >

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
      <button onClick={getAI}>
        Analyze Room
      </button>
      <AIStatus message={analysis} />
    </div>

  )

}

export default App;