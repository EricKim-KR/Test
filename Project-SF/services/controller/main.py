import json
import paho.mqtt.client as mqtt
import os

# Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 11883))
MQTT_TOPIC_SENSORS = "sensors/#"
MQTT_TOPIC_COMMANDS = "commands/"

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"[Controller] Connected to MQTT with result code {rc}")
    client.subscribe(MQTT_TOPIC_SENSORS)

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        device_id = topic.split('/')[-1]
        
        # Simple Logic Rule
        if "temperature" in payload:
            temp = float(payload["temperature"])
            command_topic = f"{MQTT_TOPIC_COMMANDS}{device_id}"
            
            if temp > 28.0:
                command = {"fan": "ON", "reason": "High Temp"}
                client.publish(command_topic, json.dumps(command))
                print(f"[Controller] High Temp ({temp}C). Sent ON to {command_topic}")
            elif temp < 22.0:
                command = {"heater": "ON", "reason": "Low Temp"}
                client.publish(command_topic, json.dumps(command))
                print(f"[Controller] Low Temp ({temp}C). Sent ON to {command_topic}")
            else:
                # Optional: Send OFF or do nothing
                pass
                
    except Exception as e:
        print(f"[Controller] Error processing rule: {e}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

print(f"[Controller] Connecting to {MQTT_BROKER}:{MQTT_PORT}...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

client.loop_forever()
