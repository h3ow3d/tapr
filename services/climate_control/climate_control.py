import asyncio
import json
import logging
import os

import paho.mqtt.client as mqtt

from tapo import ApiClient

import yaml


# Set up logging
logging.basicConfig(
    level=logging.INFO,  # Adjust the logging level as needed
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Load configuration
script_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, "climate_control_config.yml")

logger.info(f"Loading configuration from {config_path}")
with open(config_path, "r") as config_file:
    config = yaml.safe_load(config_file)

# MQTT Configuration
MQTT_BROKER = config["mqtt"]["broker_host"]
MQTT_PORT = config["mqtt"]["broker_port"]
HUMIDITY_TOPIC = config["mqtt"]["topics"]["humidity_topic"]
TEMPERATURE_TOPIC = config["mqtt"]["topics"]["temperature_topic"]

# Tapo Device Configuration (from environment variables)
TAPO_USERNAME = os.getenv("TAPO_EMAIL")
TAPO_PASSWORD = os.getenv("TAPO_PASSWORD")
TAPO_IP_HUMIDIFIER = os.getenv("TAPO_IP_HUMIDIFIER")
TAPO_IP_HEATER = os.getenv("TAPO_IP_HEATER")

# Prescribed Ranges
HUMIDITY_RANGE = config["mqtt"]["ranges"]["humidity"]
TEMPERATURE_RANGE = config["mqtt"]["ranges"]["temperature"]

logger.info("Initializing Tapo client")
# Initialize Tapo client
tapo_client = ApiClient(TAPO_USERNAME, TAPO_PASSWORD)


async def control_device(device, action):
    """Control the Tapo device (on/off)."""
    device_info = await device.get_device_info()
    device_dict = device_info.to_dict()
    logger.info(f"Control device {device_dict['ip']} with action {action}")
    if action == "on":
        await device.on()
        logger.info(f"Device {device_dict['ip']} turned ON.")
    elif action == "off":
        await device.off()
        logger.info(f"Device {device_dict['ip']} turned OFF.")
    else:
        logger.error(f"Unknown action: {action}")


async def check_and_control(sensor_type, value, min_range, max_range):
    """Check if the value is within range and control the device."""
    logger.info(f"Checking and controlling for sensor type: {sensor_type}")
    logger.info(f"Value: {value}, Range: {min_range} - {max_range}")

    if sensor_type == "humidity":
        device = await tapo_client.p100(TAPO_IP_HUMIDIFIER)
        logger.info(f"Controlling humidifier at IP: {TAPO_IP_HUMIDIFIER}")
    elif sensor_type == "temperature":
        device = await tapo_client.p100(TAPO_IP_HEATER)
        logger.info(f"Controlling heater at IP: {TAPO_IP_HEATER}")
    else:
        logger.error(f"Unknown sensor type: {sensor_type}")
        return

    if min_range <= value <= max_range:
        logger.info(f"Value {value} is within the range, turning device OFF.")
        await control_device(device, "off")
    else:
        logger.info(f"Value {value} is outside the range, turning device ON.")
        await control_device(device, "on")


def on_connect(client, userdata, flags, rc):
    logger.info(f"Connected with result code {rc}")
    logger.info(
        f"Subscribing to topics: {HUMIDITY_TOPIC}, {TEMPERATURE_TOPIC}"
    )  # noqa: E501
    client.subscribe([(HUMIDITY_TOPIC, 0), (TEMPERATURE_TOPIC, 0)])


def on_message(client, userdata, msg):
    try:
        logger.info(
            f"Message received on topic {msg.topic}: {msg.payload.decode()}"
        )  # noqa: E501
        message = json.loads(msg.payload.decode())
        sensor_type = message.get("sensor_type")
        value = message.get("value")
        logger.info(
            f"Parsed message: sensor_type={sensor_type}, value={value}"
        )  # noqa: E501

        loop = asyncio.get_event_loop()
        if sensor_type == "humidity":
            loop.run_until_complete(
                check_and_control("humidity", value, *HUMIDITY_RANGE)
            )
        elif sensor_type == "temperature":
            loop.run_until_complete(
                check_and_control("temperature", value, *TEMPERATURE_RANGE)
            )
        else:
            logger.warning(f"Unknown sensor type received: {sensor_type}")
    except ValueError as e:
        logger.error(
            f"Failed to decode message: {msg.payload.decode()} with error: {e}"
        )
    except Exception as e:
        logger.error(f"Error processing message: {e}")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

logger.info(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
