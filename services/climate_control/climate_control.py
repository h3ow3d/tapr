import json
import os

import paho.mqtt.client as mqtt

from tapo import ApiClient

import yaml


with open("climate_control_config.yml", "r") as config_file:
    config = yaml.safe_load(config_file)

MQTT_BROKER = config["mqtt"]["broker_host"]
MQTT_PORT = config["mqtt"]["broker_port"]
HUMIDITY_TOPIC = config["mqtt"]["topics"]["humidity_topic"]
TEMPERATURE_TOPIC = config["mqtt"]["topics"]["temperature_topic"]

TAPO_EMAIL = os.getenv("TAPO_EMAIL")
TAPO_PASSWORD = os.getenv("TAPO_PASSWORD")
TAPO_IP_HUMIDIFIER = os.getenv("TAPO_IP_HUMIDIFIER")
TAPO_IP_HEATER = os.getenv("TAPO_IP_HEATER")

HUMIDITY_RANGE = config["mqtt"]["ranges"]["humidity"]
TEMPERATURE_RANGE = config["mqtt"]["ranges"]["temperature"]

tapo_client = ApiClient(TAPO_EMAIL, TAPO_PASSWORD)


async def control_device(device, action):
    """Control the Tapo device (on/off)."""
    if action == "on":
        await device.on()
        print(f"Device {device.ip} turned ON.")
    elif action == "off":
        await device.off()
        print(f"Device {device.ip} turned OFF.")
    else:
        print(f"Unknown action: {action}")


async def check_and_control(sensor_type, value, min_range, max_range):
    """Check if the value is within range and control the device accordingly."""  # noqa: E501
    if sensor_type == "humidity":
        device = await tapo_client.p100(TAPO_IP_HUMIDIFIER)
    elif sensor_type == "temperature":
        device = await tapo_client.p100(TAPO_IP_HEATER)
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
        print(
            f"Failed to decode message: {msg.payload.decode()} with error {e}"
        )  # noqa: E501
    except Exception as e:
        print(f"Error processing message: {e}")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
