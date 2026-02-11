import json
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os

# Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 11883))
MQTT_TOPIC = "sensors/#"

INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:18086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "adminpassword")
INFLUX_ORG = os.getenv("INFLUX_ORG", "my-org")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "iot_data")

# InfluxDB Client
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"[Bridge] Connected to MQTT with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"[Bridge] Received: {payload} on {msg.topic}")
        
        # Create InfluxDB Point
        # Assuming payload has keys like 'temperature', 'humidity'
        # and we use the topic as a tag (e.g., device_id)
        
        device_id = msg.topic.split('/')[-1]
        
        point = Point("environment") \
            .tag("device_id", device_id)
            
        if "temperature" in payload:
            point = point.field("temperature", float(payload["temperature"]))
        if "humidity" in payload:
            point = point.field("humidity", float(payload["humidity"]))
            
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        print("[Bridge] Data written to InfluxDB")
        
    except Exception as e:
        print(f"[Bridge] Error processing message: {e}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

print(f"[Bridge] Connecting to MQTT {MQTT_BROKER}:{MQTT_PORT} and InfluxDB {INFLUX_URL}")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

client.loop_forever()
