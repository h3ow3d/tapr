import json
import os
import asyncio

import paho.mqtt.client as mqtt
from tapo import ApiClient
import yaml

# Load configuration
script_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, "climate_control_config.yml")

print(f"Loading configuration from {config_path}")
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

print("Initializing Tapo client")
# Initialize Tapo client
tapo_client = ApiClient(TAPO_USERNAME, TAPO_PASSWORD)

async def control_device(device, action):
    """Control the Tapo device (on/off)."""
    device_info = await device.get_device_info()
    device_dict = device_info.to_dict()
    print(f"Control device {device_dict['ip']} with action {action}")
    if action == "on":
        await device.on()
        print(f"Device {device_dict['ip']} turned ON.")
    elif action == "off":
        await device.off()
        print(f"Device {device_dict['ip']} turned OFF.")
    else:
        print(f"Unknown action: {action}")

async def check_and_control(sensor_type, value, min_range, max_range):
    """Check if the value is within range and control the device."""
    print(f"Checking and controlling for sensor type: {sensor_type}")
    print(f"Value: {value}, Range: {min_range} - {max_range}")

    if sensor_type == "humidity":
        device = await tapo_client.p100(TAPO_IP_HUMIDIFIER)
        print(f"Controlling humidifier at IP: {TAPO_IP_HUMIDIFIER}")
    elif sensor_type == "temperature":
        device = await tapo_client.p100(TAPO_IP_HEATER)
        print(f"Controlling heater at IP: {TAPO_IP_HEATER}")
    else:
        print(f"Unknown sensor type: {sensor_type}")
        return

    if min_range <= value <= max_range:
        print(f"Value {value} is within the range, turning device OFF.")
        await control_device(device, "off")
    else:
        print(f"Value {value} is outside the range, turning device ON.")
        await control_device(device, "on")

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    print(f"Subscribing to topics: {HUMIDITY_TOPIC}, {TEMPERATURE_TOPIC}")
    client.subscribe([(HUMIDITY_TOPIC, 0), (TEMPERATURE_TOPIC, 0)])

def on_message(client, userdata, msg):
    try:
        print(f"Message received on topic {msg.topic}: {msg.payload.decode()}")
        message = json.loads(msg.payload.decode())
        sensor_type = message.get("sensor_type")
        value = message.get("value")
        print(f"Parsed message: sensor_type={sensor_type}, value={value}")

        loop = asyncio.get_event_loop()
        if sensor_type == "humidity":
            loop.run_until_complete(check_and_control("humidity", value, *HUMIDITY_RANGE))
        elif sensor_type == "temperature":
            loop.run_until_complete(check_and_control("temperature", value, *TEMPERATURE_RANGE))
        else:
            print(f"Unknown sensor type received: {sensor_type}")
    except ValueError as e:
        print(f"Failed to decode message: {msg.payload.decode()} with error: {e}")
    except Exception as e:
        print(f"Error processing message: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()

