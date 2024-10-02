import json
import logging
import os
import time

import Adafruit_DHT

import paho.mqtt.client as mqtt

import yaml


# Set up logging to log to stdout (systemd will capture this)
logging.basicConfig(
    level=logging.INFO,  # Adjust the logging level as needed
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Load configuration
script_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, "dht_sensor_config.yml")

logger.info(f"Loading configuration from {config_path}")
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
logger.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")


def get_sensor_readings():
    """Read humidity and temperature from the DHT11 sensor."""
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        logger.info(
            f"Sensor readings - Humidity: {humidity}%, Temperature: {temperature}C"  # noqa: E501
        )
        return humidity, temperature
    else:
        logger.error("Failed to retrieve data from sensor")
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
        logger.info(f"Published humidity data: {humidity_payload}")
        logger.info(f"Published temperature data: {temperature_payload}")
    else:
        logger.warning("No valid sensor data to publish")


# Main loop to publish sensor data periodically
try:
    while True:
        publish_sensor_data()
        time.sleep(60)  # Publish every 60 seconds (adjust as needed)
except KeyboardInterrupt:
    logger.info("Sensor service interrupted by user")
finally:
    client.disconnect()
    logger.info("Disconnected from MQTT broker")
