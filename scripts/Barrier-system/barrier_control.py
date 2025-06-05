from gpiozero import AngularServo, Device, Button, LED
from gpiozero.pins.pigpio import PiGPIOFactory
import time
import paho.mqtt.client as mqtt




# Setup MQTT client
MQTT_BROKER = "localhost"  # oder IP-Adresse des Brokers
MQTT_TOPIC = "barrier"
client = mqtt.Client()
client.connect(MQTT_BROKER)




# fsr active flag
monitor_fsr = True

# force sensitve resistor
fsr = Button(13, pull_up=False)
led = LED(6)

# Use pigpio for smoother servo control
Device.pin_factory = PiGPIOFactory()

# Servo setup
myGPIO = 26
servo = AngularServo(myGPIO, min_angle=0, max_angle=90,
                     min_pulse_width=0.0005, max_pulse_width=0.0025)
servo.angle = 0  # Initial position = barrier down


def close_barrier():
    if fsr.is_pressed:
       client.publish(MQTT_TOPIC, 'FSR Sensor triggered, move your car!')
    
    # wait until no pressure is detected under the barrier
    while fsr.is_pressed:
        print("FSR is active, waiting for release...")
        time.sleep(0.1)

    print("Closing barrier...")
    value = 1000
    while value >= 0:
        if fsr.is_pressed:
            print("Pressure detected during closing, reopening barrier")
            # open barrier fully
            for reopen in range(value, 1001, 10):
                servo.value = round(reopen / 1000, 2) - 1
                time.sleep(0.01)

            # Wait until fsr is released
            while fsr.is_pressed:
                print("Still pressure, still waiting")
                time.sleep(0.5)
          
            print("Path clear restarting closing...")
            return close_barrier()  # start closing procedure again
        servo.value = round(value / 1000, 2) - 1
        time.sleep(0.01)
        value -= 5

    print("Barrier fully closed.")
    


def open_barrier():
    print("Barrier opening...")
    for value in range(0, 1001, 5):
        servo.value = round(value / 1000, 2) - 1  # move from -1 to 0
        time.sleep(0.01)
        
        
def monitor_fsr_led():
    global monitor_fsr
    while monitor_fsr:
        if fsr.is_pressed:
            led.on()
        else:
            led.off()
        time.sleep(0.05)         