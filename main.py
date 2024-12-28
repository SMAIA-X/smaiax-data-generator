import os
import json
import time
import random
import logging
import uuid

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
topic = os.getenv('TEST_TOPIC', "test")

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


def generate_sensor_data(smart_meter_id):
    current_time = datetime.now().isoformat()
    uptime_delta = datetime.now() - start_time
    uptime_str = format_uptime(uptime_delta)

    data = {
        "SmartMeterId": smart_meter_id,
        "1.7.0": str(random.randint(150, 170)),
        "1.8.0": str(random.randint(1130000, 1138000)),
        "2.7.0": "0",
        "2.8.0": "0",
        "3.8.0": str(random.randint(3000, 4000)),
        "4.8.0": str(random.randint(700000, 720000)),
        "16.7.0": str(random.randint(150, 170)),
        "31.7.0": "{:.2f}".format(random.uniform(1.0, 1.1)),
        "32.7.0": "{:.2f}".format(random.uniform(229.0, 230.0)),
        "51.7.0": "{:.2f}".format(random.uniform(0.4, 0.5)),
        "52.7.0": "{:.2f}".format(random.uniform(229.0, 230.0)),
        "71.7.0": "{:.2f}".format(random.uniform(0.1, 0.2)),
        "72.7.0": "{:.2f}".format(random.uniform(229.0, 230.0)),
        "Uptime": uptime_str,
        "Timestamp": current_time
    }

    return data

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info(f"Connected to MQTT Broker at {mqtt_broker_host}:{mqtt_port}")
    else:
        logging.error(f"Failed to connect to MQTT Broker, return code {rc}")

def connect_mqtt():
    client_id = f"data-generator-{uuid.uuid4()}"
    logging.info(f"Generated client_id: {client_id}")

    client = mqtt.Client(client_id=client_id)
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
    result = client.publish(topic, payload)

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        logging.info(f"Sent data to MQTT at {data['Timestamp']} with uptime {data['Uptime']}")
    else:
        logging.error("Failed to send message to MQTT broker")

if __name__ == "__main__":
    try:
        mqtt_client = connect_mqtt()
        smart_meter_id = os.getenv("SMART_METER_ID")
        logging.info(f"smart meter id: {smart_meter_id}")
        if not smart_meter_id:
            smart_meter_id = str(uuid.uuid4())

        while True:
            sensor_data = generate_sensor_data(smart_meter_id)
            send_to_mqtt(mqtt_client, sensor_data)

            time.sleep(time_interval)

    except Exception as e:
        logging.critical(f"An error occurred: {e}")