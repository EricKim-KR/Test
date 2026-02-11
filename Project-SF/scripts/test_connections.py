import time
import sys
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient

# Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 11883
INFLUX_URL = "http://localhost:18086"
INFLUX_TOKEN = "adminpassword" # As set in docker-compose
INFLUX_ORG = "my-org"
INFLUX_BUCKET = "iot_data"

def test_mqtt():
    print(f"Testing MQTT Connection to {MQTT_BROKER}:{MQTT_PORT}...")
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print("[OK] MQTT Connection Successful!")
        client.disconnect()
        return True
    except Exception as e:
        print(f"[ERROR] MQTT Connection Failed: {e}")
        return False

def test_influxdb():
    print(f"Testing InfluxDB Connection to {INFLUX_URL}...")
    try:
        client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        health = client.health()
        if health.status == "pass":
            print("[OK] InfluxDB Connection Successful!")
            return True
        else:
            print(f"[ERROR] InfluxDB Health Check Failed: {health.status}")
            return False
    except Exception as e:
        print(f"[ERROR] InfluxDB Connection Failed: {e}")
        return False

if __name__ == "__main__":
    print("--- Infrastructure Connectivity Check ---")
    mqtt_ok = test_mqtt()
    influx_ok = test_influxdb()
    
    if mqtt_ok and influx_ok:
        print("\nAll systems operational.")
        sys.exit(0)
    else:
        print("\nSome systems failed.")
        sys.exit(1)
