from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from influxdb_client import InfluxDBClient
import paho.mqtt.client as mqtt
import os
import json
import time

app = FastAPI(title="IoT Backend API")

# CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5173", # Vite
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 11883))
INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:18086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "adminpassword")
INFLUX_ORG = os.getenv("INFLUX_ORG", "my-org")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "iot_data")

# Influx Client
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = influx_client.query_api()

# MQTT Client (Publisher)
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    print(f"[API] Connected to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}")
except Exception as e:
    print(f"[API] MQTT Connection Failed: {e}")

class CommandRequest(BaseModel):
    device_id: str
    action: str # "ON", "OFF"
    component: str # "fan", "heater"

@app.get("/")
def read_root():
    return {"message": "IoT Backend API is running"}

@app.get("/api/data/{device_id}")
def get_sensor_data(device_id: str, minutes: int = 10):
    """
    Get sensor data for the last N minutes from InfluxDB
    """
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -{minutes}m)
      |> filter(fn: (r) => r["_measurement"] == "environment")
      |> filter(fn: (r) => r["device_id"] == "{device_id}")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    try:
        tables = query_api.query(query, org=INFLUX_ORG)
        results = []
        for table in tables:
            for record in table.records:
                results.append({
                    "time": record.get_time(),
                    "temperature": record.values.get("temperature"),
                    "humidity": record.values.get("humidity"),
                    "device_id": device_id
                })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/control")
def send_command(cmd: CommandRequest):
    """
    Send a control command via MQTT
    """
    topic = f"commands/{cmd.device_id}"
    payload = {
        cmd.component: cmd.action,
        "timestamp": time.time(),
        "source": "api"
    }
    try:
        mqtt_client.publish(topic, json.dumps(payload))
        return {"status": "sent", "topic": topic, "payload": payload}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
