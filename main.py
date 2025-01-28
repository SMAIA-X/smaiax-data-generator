import os
import json
import time
import random
import logging

import paho.mqtt.client as mqtt
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

mqtt_broker_host = os.getenv('MQTT_BROKER_HOST', 'localhost')
mqtt_port = int(os.getenv('MQTT_PORT', 1883))
mqtt_username = os.getenv('MQTT_USERNAME', "user")
mqtt_password = os.getenv('MQTT_PASSWORD', "password")
start_time = datetime.now()
time_interval = int(os.getenv('TIME_INTERVAL', 5))
smart_meter_id = os.getenv("SMART_METER_ID", "070dec95-56bb-4154-a2c4-c26faf9fff4d")
tenant_id = os.getenv("TENANT_ID", "2edce4d5-47ef-433e-b058-827d7cde050d")

def format_uptime(uptime_delta):
    total_seconds = int(uptime_delta.total_seconds())

    days = total_seconds // (24 * 3600)
    total_seconds %= (24 * 3600)
    hours = total_seconds // 3600
    total_seconds %= 3600
    minutes = total_seconds // 60
    seconds = total_seconds % 60

    # Format the uptime as 0000:hh:mm:ss
    return f"{days:04}:{hours:02}:{minutes:02}:{seconds:02}"


def generate_sensor_data():
    current_time = datetime.now().isoformat()

    data = {
        "smart_meter_id": smart_meter_id,
        "tenant_id": tenant_id,
        "timestamp": current_time,
        "voltage_phase_1": round(random.uniform(229.0, 230.0), 2),
        "voltage_phase_2": round(random.uniform(229.0, 230.0), 2),
        "voltage_phase_3": round(random.uniform(229.0, 230.0), 2),
        "current_phase_1": round(random.uniform(0.0, 0.1), 2),
        "current_phase_2": round(random.uniform(0.0, 0.1), 2),
        "current_phase_3": round(random.uniform(0.0, 0.1), 2),
        "positive_active_power": round(random.uniform(0.0, 5.0), 2),
        "negative_active_power": round(random.uniform(0.0, 1.0), 2),
        "positive_reactive_energy_total": round(random.uniform(80.0, 100.0), 2),
        "negative_reactive_energy_total": round(random.uniform(20.0, 30.0), 2),
        "positive_active_energy_total": round(random.uniform(700.0, 800.0), 2),
        "negative_active_energy_total": round(random.uniform(0.0, 50.0), 2)
    }

    return data

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info(f"Connected to MQTT Broker at {mqtt_broker_host}:{mqtt_port}")
    else:
        logging.error(f"Failed to connect to MQTT Broker, return code {rc}")

def connect_mqtt():
    client = mqtt.Client(client_id=f"connector-{smart_meter_id}")
    client.username_pw_set(mqtt_username, mqtt_password)
    client.on_connect = on_connect

    try:
        logging.info(f"Connecting to MQTT broker at {mqtt_broker_host}:{mqtt_port}")
        client.connect(mqtt_broker_host, mqtt_port, 60)
        client.loop_start()
        return client
    except Exception as ex:
        logging.error(f"Failed to connect to MQTT broker: {ex}")
        raise

def send_to_mqtt(client, data):
    payload = json.dumps(data)
    result = client.publish(f"smartmeter/{smart_meter_id}", payload)

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        logging.info(f"Sent data to MQTT at {data['timestamp']}")
    else:
        logging.error("Failed to send message to MQTT broker")

if __name__ == "__main__":
    try:
        mqtt_client = connect_mqtt()
        logging.info(f"smart meter id: {smart_meter_id}")

        while True:
            sensor_data = generate_sensor_data()
            send_to_mqtt(mqtt_client, sensor_data)

            time.sleep(time_interval)

    except Exception as e:
        logging.critical(f"An error occurred: {e}")