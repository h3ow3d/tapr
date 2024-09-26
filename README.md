# Climate Control System

## Overview

The **Climate Control System** is designed to monitor and manage environmental conditions using a combination of MQTT, sensors, and an external API. This project includes the installation and configuration of an MQTT broker (Mosquitto) and services that handle temperature and humidity data. The system can automatically control devices based on the sensor data to maintain desired climate conditions.

## Features

- **MQTT Broker Installation**: Automatically installs and configures Mosquitto on a Raspberry Pi.
- **Temperature and Humidity Monitoring**: Services that consume MQTT messages with temperature and humidity data.
- **Automated Device Control**: Based on sensor data, the system sends control messages to an external API to manage climate control devices.
- **Flexible Configuration**: The project allows for easy updates and scaling to include additional sensors or monitoring capabilities.

## Project Structure

```plaintext
my_project/
├── ansible/
│   ├── playbooks/
│   │   ├── install_mosquitto.yml
│   │   ├── install_climate_control_service.yml
│   │   ├── install_humidity_sensor.yml
│   │   ├── install_temperature_sensor.yml
│   │   ├── install_all_services.yml
│   ├── templates/
│   │   ├── climate_control_service.j2
│   │   ├── humidity_sensor_service.j2
│   │   ├── temperature_sensor_service.j2
│   ├── inventory/
│   │   └── hosts.ini
│   └── ansible.cfg
├── services/
│   ├── climate_control/
│   │   ├── climate_control.py
│   │   ├── requirements.txt
│   ├── humidity_sensor/
│   │   ├── humidity_sensor.py
│   │   ├── requirements.txt
│   ├── temperature_sensor/
│   │   ├── temperature_sensor.py
│   │   ├── requirements.txt
├── .pre-commit-config.yaml
├── .gitignore
└── README.md
```

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
ansible-playbook playbooks/install_mosquitto.yml
```

### 4. Installing and Configuring Services

#### a. Climate Control Service

This service monitors temperature and humidity data via MQTT, determines if the values fall within a prescribed range, and sends control messages to devices.

```bash
ansible-playbook playbooks/install_climate_control_service.yml
```

#### b. Humidity Sensor Service

This service reads humidity data from a sensor and publishes it to an MQTT topic.

```bash
ansible-playbook playbooks/install_humidity_sensor.yml
```

#### c. Temperature Sensor Service

This service reads temperature data from a sensor and publishes it to an MQTT topic.

```bash
ansible-playbook playbooks/install_temperature_sensor.yml
```

### 5. Installing All Services

To install and configure all services at once, run:

```bash
ansible-playbook playbooks/install_all_services.yml
```

## Usage

### Starting Services

The services are managed by systemd and should start automatically after installation. You can manage them using the following commands:

- **Start a service**:

  ```bash
  sudo systemctl start climate_control_service
  ```

- **Stop a service**:

  ```bash
  sudo systemctl stop climate_control_service
  ```

- **Restart a service**:

  ```bash
  sudo systemctl restart climate_control_service
  ```

- **Check the status of a service**:

  ```bash
  sudo systemctl status climate_control_service
  ```

### Viewing Logs

You can view the logs for any of the services using the `journalctl` command:

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
