
# Climate Control System

## Overview

The **Climate Control System** is designed to monitor and manage environmental conditions using a combination of MQTT, sensors, and an external API. This project includes the installation and configuration of an MQTT broker (Mosquitto) and a service that handles temperature and humidity data. The system can automatically control devices based on the sensor data to maintain desired climate conditions.

## Features

- **MQTT Broker Installation**: Automatically installs and configures Mosquitto on a Raspberry Pi.
- **Temperature and Humidity Monitoring**: The service consumes MQTT messages with temperature and humidity data.
- **Automated Device Control**: Based on sensor data, the system sends control messages to an external API to manage climate control devices.
- **Flexible Configuration**: The project allows for easy updates and scaling to include additional sensors or monitoring capabilities.

## Project Structure

```plaintext
├── README.md
├── ansible
│   ├── ansible.cfg
│   ├── inventory
│   │   └── hosts.ini
│   └── playbooks
│       ├── install_climate_control.yml
│       ├── install_mqtt.yml
│       └── templates
│           └── climate_control_service.j2
└── services
    └── climate_control
        ├── climate_control.py
        ├── climate_control_config.yml
        └── requirements.txt
```

## Sensor Service Message Schema

The climate control service publishes and consumes messages to/from the MQTT broker in JSON format. Below is the schema for the messages.

### JSON Message Schema

```json
{
  "sensor_id": "string",        // Unique identifier for the sensor
  "sensor_type": "string",      // Type of the sensor ("humidity" or "temperature")
  "location": "string",         // Location of the sensor (e.g., "living_room", "greenhouse")
  "timestamp": "string",        // ISO 8601 formatted timestamp when the reading was taken
  "value": "number",            // The measured value (e.g., 45.3 for humidity, 22.5 for temperature)
  "unit": "string"              // Unit of the measured value ("%" for humidity, "C" or "F" for temperature)
}
```

### Example Messages

#### 1. **Humidity Sensor Example**

```json
{
  "sensor_id": "humidity_sensor_1",
  "sensor_type": "humidity",
  "location": "greenhouse",
  "timestamp": "2024-09-26T12:34:56Z",
  "value": 45.3,
  "unit": "%"
}
```

#### 2. **Temperature Sensor Example**

```json
{
  "sensor_id": "temperature_sensor_1",
  "sensor_type": "temperature",
  "location": "living_room",
  "timestamp": "2024-09-26T12:34:56Z",
  "value": 22.5,
  "unit": "C"
}
```

### Explanation of Fields

- **`sensor_id`**: A unique identifier for each sensor. This helps distinguish between different sensors, especially when multiple sensors of the same type are deployed.

- **`sensor_type`**: Indicates whether the sensor is measuring humidity or temperature. This field is useful for the consumers to know how to interpret the `value`.

- **`location`**: The physical location of the sensor. This is especially useful in systems with multiple sensors spread across different locations.

- **`timestamp`**: The time when the sensor reading was taken. Using an ISO 8601 format ensures consistency and ease of parsing across different systems.

- **`value`**: The actual measured value from the sensor. For humidity, this would typically be a percentage, and for temperature, it could be in degrees Celsius or Fahrenheit.

- **`unit`**: The unit of the `value`. For humidity, this would be `%`, and for temperature, this could be `C` (Celsius) or `F` (Fahrenheit).

## Setup and Installation

### 1. Prerequisites

Ensure that your Raspberry Pi is up to date:

```bash
sudo apt update
sudo apt upgrade -y
```

Install Ansible if it’s not already installed:

```bash
sudo apt install ansible -y
```

### 2. Clone the Repository

Clone this project to your Raspberry Pi:

```bash
git clone https://github.com/your-username/climate-control-system.git
cd climate-control-system
```

### 3. Installing Mosquitto MQTT Broker

Run the following Ansible playbook to install and configure Mosquitto:

```bash
cd ansible
ansible-playbook playbooks/install_mqtt.yml
```

### 4. Installing and Configuring the Climate Control Service

This service monitors temperature and humidity data via MQTT, determines if the values fall within a prescribed range, and sends control messages to devices.

```bash
ansible-playbook playbooks/install_climate_control.yml
```

## Usage

### Starting Services

The climate control service is managed by systemd and should start automatically after installation. You can manage it using the following commands:

- **Start the service**:

  ```bash
  sudo systemctl start climate_control_service
  ```

- **Stop the service**:

  ```bash
  sudo systemctl stop climate_control_service
  ```

- **Restart the service**:

  ```bash
  sudo systemctl restart climate_control_service
  ```

- **Check the status of the service**:

  ```bash
  sudo systemctl status climate_control_service
  ```

### Viewing Logs

You can view the logs for the service using the `journalctl` command:

```bash
sudo journalctl -u climate_control_service -f
```

## Customization

### MQTT Configuration

The Mosquitto configuration can be modified by editing the `/etc/mosquitto/mosquitto.conf` file. To apply changes, reload the service:

```bash
sudo systemctl reload mosquitto
```

### API Endpoints

The API endpoints used by the `climate_control.py` script can be updated directly in the script or by modifying environment variables, if configured.

## Contributing

Feel free to submit issues, fork the repository, and send pull requests. Contributions are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions, please contact [your-email@example.com](mailto:your-email@example.com).
