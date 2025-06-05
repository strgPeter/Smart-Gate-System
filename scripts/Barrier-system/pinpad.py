
import Keypad
from barrier_control import open_barrier, close_barrier
import time
import paho.mqtt.client as mqtt


# Keypad-configuration
ROWS = 4
COLS = 4
keys = [ '1','2','3','A',
         '4','5','6','B',
         '7','8','9','C',
         '*','0','#','D' ]
rowsPins = [18, 23, 24, 25]
colsPins = [10, 22, 27, 17]

CORRECT_PIN = "1234"

# Setup MQTT client
MQTT_BROKER = "localhost"  
MQTT_TOPIC = "barrier"
client = mqtt.Client()
client.connect(MQTT_BROKER)

keypad = Keypad.Keypad(keys, rowsPins, colsPins, ROWS, COLS)
keypad.setDebounceTime(50)

pin_input = ""

def loop_keypad():
    global pin_input
    print("PIN pad active - enter 4-digit code")
    while True:
        key = keypad.getKey()
        if key != keypad.NULL:
            print(f"Pressed: {key}")
            if key == '#':
                print("Entered PIN:", pin_input)
                if pin_input == CORRECT_PIN:
                    print("PIN correct. Opening barrier.")
                    client.publish(MQTT_TOPIC, '{"action": "open"}')
                else:
                    print("Incorrect PIN.")
                pin_input = ""
            elif key == '*':
                pin_input = ""
                print("PIN cleared")
            else:
                pin_input += key
                if len(pin_input) > 4:
                    pin_input = pin_input[:4]

