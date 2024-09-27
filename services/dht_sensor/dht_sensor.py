import json
import os
import time

import Adafruit_DHT

import paho.mqtt.client as mqtt

import yaml


# Load configuration
script_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, "humidity_sensor_config.yml")

print(f"Loading configuration from {config_path}")
with open(config_path, "r") as config_file:
    config = yaml.safe_load(config_file)

# MQTT Configuration
MQTT_BROKER = config["mqtt"]["broker_host"]
MQTT_PORT = config["mqtt"]["broker_port"]
HUMIDITY_TOPIC = config["mqtt"]["topics"]["humidity_topic"]

# DHT11 Configuration
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = config["sensor"]["pin"]

# Initialize MQTT client
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)


def get_humidity_reading():
    """Read humidity from the DHT11 sensor."""
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None:
        return humidity
    else:
        print("Failed to retrieve data from humidity sensor")
        return None


def publish_humidity():
    humidity = get_humidity_reading()
    if humidity is not None:
        payload = {
            "sensor_type": "humidity",
            "value": humidity,
            "unit": "%",
        }
        client.publish(HUMIDITY_TOPIC, json.dumps(payload))
        print(f"Published humidity: {payload}")


# Main loop to publish humidity data periodically
try:
    while True:
        publish_humidity()
        time.sleep(60)  # Publish every 60 seconds (adjust as needed)
except KeyboardInterrupt:
    print("Humidity sensor service interrupted")
finally:
    client.disconnect()
