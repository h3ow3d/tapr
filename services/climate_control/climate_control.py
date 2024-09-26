import json
import os

import paho.mqtt.client as mqtt

from tapo import ApiClient

import yaml

# Load configuration
script_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, "climate_control_config.yml")

with open(config_path, "r") as config_file:
    config = yaml.safe_load(config_file)

# MQTT Configuration
MQTT_BROKER = config["mqtt"]["broker_host"]
MQTT_PORT = config["mqtt"]["broker_port"]
HUMIDITY_TOPIC = config["mqtt"]["topics"]["humidity_topic"]
TEMPERATURE_TOPIC = config["mqtt"]["topics"]["temperature_topic"]

# Tapo Device Configuration (from environment variables)
TAPO_EMAIL = os.getenv("TAPO_EMAIL")
TAPO_PASSWORD = os.getenv("TAPO_PASSWORD")
TAPO_IP_HUMIDIFIER = os.getenv("TAPO_IP_HUMIDIFIER")
TAPO_IP_HEATER = os.getenv("TAPO_IP_HEATER")

# Prescribed Ranges
HUMIDITY_RANGE = config["mqtt"]["ranges"]["humidity"]
TEMPERATURE_RANGE = config["mqtt"]["ranges"]["temperature"]

# Initialize Tapo client
tapo_client = ApiClient(TAPO_EMAIL, TAPO_PASSWORD)


def control_device(device, action):
    """Control the Tapo device (on/off)."""
    if action == "on":
        device.on()
        print(f"Device {device.ip} turned ON.")
    elif action == "off":
        device.off()
        print(f"Device {device.ip} turned OFF.")
    else:
        print(f"Unknown action: {action}")


def check_and_control(sensor_type, value, min_range, max_range):
    """Check if the value is within range and control the device."""
    if sensor_type == "humidity":
        device = tapo_client.p100(TAPO_IP_HUMIDIFIER)
    elif sensor_type == "temperature":
        device = tapo_client.p100(TAPO_IP_HEATER)
    else:
        print(f"Unknown sensor type: {sensor_type}")
        return

    if min_range <= value <= max_range:
        # Value is within range, turn the device off
        control_device(device, "off")
    else:
        # Value is out of range, turn the device on
        control_device(device, "on")


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe([(HUMIDITY_TOPIC, 0), (TEMPERATURE_TOPIC, 0)])


def on_message(client, userdata, msg):
    try:
        message = json.loads(msg.payload.decode())
        sensor_type = message.get("sensor_type")
        value = message.get("value")
        print(f"Received {sensor_type}: {value}")

        if sensor_type == "humidity":
            check_and_control("humidity", value, *HUMIDITY_RANGE)
        elif sensor_type == "temperature":
            check_and_control("temperature", value, *TEMPERATURE_RANGE)
        else:
            print(f"Unknown sensor type received: {sensor_type}")
    except ValueError as e:
        print(f"Failed to decode message: {msg.payload.decode()} " f"{e}")
    except Exception as e:
        print(f"Error processing message: {e}")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
