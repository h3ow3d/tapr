import json
import os
import time

import Adafruit_DHT

import paho.mqtt.client as mqtt

import yaml

# Load configuration
script_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, "dht_sensor_config.yml")

print(f"Loading configuration from {config_path}")
with open(config_path, "r") as config_file:
    config = yaml.safe_load(config_file)

# MQTT Configuration
MQTT_BROKER = config["mqtt"]["broker_host"]
MQTT_PORT = config["mqtt"]["broker_port"]
HUMIDITY_TOPIC = config["mqtt"]["topics"]["humidity_topic"]
TEMPERATURE_TOPIC = config["mqtt"]["topics"]["temperature_topic"]

# DHT11 Configuration
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = config["sensor"]["pin"]

# Initialize MQTT client
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)


def get_sensor_readings():
    """Read humidity and temperature from the DHT11 sensor."""
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        return humidity, temperature
    else:
        print("Failed to retrieve data from sensor")
        return None, None


def publish_sensor_data():
    humidity, temperature = get_sensor_readings()
    if humidity is not None and temperature is not None:
        humidity_payload = {
            "sensor_type": "humidity",
            "value": humidity,
            "unit": "%",
        }
        temperature_payload = {
            "sensor_type": "temperature",
            "value": temperature,
            "unit": "C",
        }
        client.publish(HUMIDITY_TOPIC, json.dumps(humidity_payload))
        client.publish(TEMPERATURE_TOPIC, json.dumps(temperature_payload))
        print(f"Published humidity: {humidity_payload}")
        print(f"Published temperature: {temperature_payload}")


# Main loop to publish sensor data periodically
try:
    while True:
        publish_sensor_data()
        time.sleep(60)  # Publish every 60 seconds (adjust as needed)
except KeyboardInterrupt:
    print("Sensor service interrupted")
finally:
    client.disconnect()
