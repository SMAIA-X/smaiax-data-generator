import os
import pika
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

protocol = os.getenv('PROTOCOL', 'AMQP').upper()
rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
amqp = int(os.getenv('AMQP_PORT', 5672))
mqtt_port = int(os.getenv('MQTT_PORT', 1883))
rabbitmq_username = 'user'
rabbitmq_password = 'user'
start_time = datetime.now()

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
    uptime_delta = datetime.now() - start_time
    uptime_str = format_uptime(uptime_delta)

    data = {
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
        "uptime": uptime_str,
        "timestamp": current_time
    }

    return data


def connect_amqp():
    credentials = pika.PlainCredentials(rabbitmq_username, rabbitmq_password)
    parameters = pika.ConnectionParameters(rabbitmq_host, amqp, '/', credentials)

    try:
        connection = pika.BlockingConnection(parameters)
        logging.info(f"Connected to RabbitMQ at {rabbitmq_host}:{amqp}")
        return connection.channel()
    except Exception as ex:
        logging.error(f"Failed to connect to RabbitMQ: {ex}")
        raise


def send_to_amqp(channel, data):
    channel.queue_declare(queue='sensor_data')
    channel.basic_publish(
        exchange='',
        routing_key='sensor_data',
        body=json.dumps(data)
    )
    logging.info(f"Sent data at {data['timestamp']} with uptime {data['uptime']}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info(f"Connected to MQTT Broker at {rabbitmq_host}:{mqtt_port}")
    else:
        logging.error(f"Failed to connect to MQTT Broker, return code {rc}")

def connect_mqtt():
    client = mqtt.Client()
    client.username_pw_set(rabbitmq_username, rabbitmq_password)
    client.on_connect = on_connect

    try:
        client.connect(rabbitmq_host, mqtt_port, 60)
        client.loop_start()
        return client
    except Exception as ex:
        logging.error(f"Failed to connect to MQTT broker: {ex}")
        raise

def send_to_mqtt(client, data):
    topic = "SHRDZM/483FDA074B86/483FDA074B86/sensor"
    payload = json.dumps(data)
    result = client.publish(topic, payload)

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        logging.info(f"Sent data to MQTT at {data['timestamp']} with uptime {data['uptime']}")
    else:
        logging.error("Failed to send message to MQTT broker")

if __name__ == "__main__":
    try:
        if protocol == "AMQP":
            channel = connect_amqp()
            logging.info("Using AMQP")
        elif protocol == "MQTT":
            mqtt_client = connect_mqtt()
            logging.info("Using MQTT")
        else:
            raise ValueError("Unknown protocol specified. Use 'AMQP' or 'MQTT'.")

        while True:
            sensor_data = generate_sensor_data()

            if protocol == "AMQP":
                send_to_amqp(channel, sensor_data)
            elif protocol == "MQTT":
                send_to_mqtt(mqtt_client, sensor_data)

            time.sleep(5)

    except Exception as e:
        logging.critical(f"An error occurred: {e}")