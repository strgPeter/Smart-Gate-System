import paho.mqtt.client as mqtt
import json
from barrier_control import open_barrier, close_barrier
import paho.mqtt.client as mqtt
import time


# MQTT setup
MQTT_BROKER = "localhost"
MQTT_TOPIC = "barrier"




def on_message(client, userdata, message):
    print(f"Message received: {message.payload.decode()}")
    try:
        data = json.loads(message.payload.decode())

        if data.get("action") == "open":
            print("Barrier opening...")
            open_barrier()
            time.sleep(5)  # Wait for vehicle to pass
            close_barrier()
            client.publish(MQTT_TOPIC, '{"action": "closed"}')
        elif data.get("action")=="close":
            print("Manual closing via MQTT...")
            close_barrier()
        

    except Exception as e:
        print("Error processing message:", e)


def start_mqtt():
    print("Starting MQTT listener...")
    client = mqtt.Client()
    client.connect(MQTT_BROKER)
    client.subscribe(MQTT_TOPIC)
    client.on_message = on_message
    client.loop_forever()