import time
import json
import os
import numpy as np
from sklearn.linear_model import LinearRegression
from influxdb_client import InfluxDBClient
import paho.mqtt.client as mqtt

# Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 11883))
INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:18086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "adminpassword")
INFLUX_ORG = os.getenv("INFLUX_ORG", "my-org")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "iot_data")

def fetch_data():
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query_api = client.query_api()
    
    # Get last 50 points of temperature
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -10m)
      |> filter(fn: (r) => r["_measurement"] == "environment")
      |> filter(fn: (r) => r["_field"] == "temperature")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    try:
        tables = query_api.query(query, org=INFLUX_ORG)
        data = []
        for table in tables:
            for record in table.records:
                data.append(record.values.get("temperature"))
        return data
    except Exception as e:
        print(f"[AI] Fetch Error: {e}")
        return []

def train_and_predict(data):
    if len(data) < 10:
        return None
    
    X = np.array(range(len(data))).reshape(-1, 1)
    y = np.array(data)
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict next step
    next_step = np.array([[len(data) + 5]])
    prediction = model.predict(next_step)[0]
    
    slope = model.coef_[0]
    return prediction, slope

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
except:
    pass

print("[AI Engine] Starting analysis loop...")

while True:
    data = fetch_data()
    print(f"[AI] Analyze {len(data)} points...")
    
    if len(data) >= 10:
        pred, slope = train_and_predict(data)
        print(f"[AI] Prediction: {pred:.2f}, Trend: {slope:.4f}")
        
        if slope > 0.05:
            alert = {
                "type": "PREDICTION",
                "message": "Temperature Rising Rapidly!",
                "predicted_value": round(pred, 2),
                "trend": "UP"
            }
            mqtt_client.publish("alerts/ai", json.dumps(alert))
    
    time.sleep(10)
