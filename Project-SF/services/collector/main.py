import time
import json
import random
import paho.mqtt.client as mqtt
import os

# Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 11883))
TOPIC = "sensors/device_01"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[Collector] Connected to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}")
    else:
        print(f"[Collector] Failed to connect, return code {rc}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect

print(f"[Collector] Connecting to {MQTT_BROKER}:{MQTT_PORT}...")
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
except Exception as e:
    print(f"[Collector] Connection failed: {e}")
    exit(1)

client.loop_start()

while True:
    # Simulate sensor data
    payload = {
        "temperature": round(random.uniform(20.0, 30.0), 2),
        "humidity": round(random.uniform(40.0, 60.0), 2),
        "timestamp": time.time()
    }
    
    try:
        json_payload = json.dumps(payload)
        client.publish(TOPIC, json_payload)
        print(f"[Collector] Published to {TOPIC}: {json_payload}")
    except Exception as e:
        print(f"[Collector] Publish failed: {e}")
        
    time.sleep(2) # Send every 2 seconds
