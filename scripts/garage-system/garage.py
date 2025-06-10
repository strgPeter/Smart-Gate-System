import time
import paho.mqtt.client as mqtt
from gpiozero import LED, MotionSensor, DistanceSensor
import json

# MQTT Configuration
MQTT_BROKER = "10.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC_GARAGE_CONTROL = "barrier"  # Topic to listen for garage control commands
MQTT_TOPIC_GARAGE_STATUS = "garage"    # Topic to publish garage status

# GPIO Pins
MOTION_SENSOR_PIN = 16      # HC SR501 Motion Sensor
GREEN_LED_PIN = 20          # Green LED for free garage
RED_LED_PIN = 21            # Red LED for occupied garage / motion detection
ULTRASONIC_TRIGGER_PIN = 23 # Ultrasonic sensor trigger pin
ULTRASONIC_ECHO_PIN = 24    # Ultrasonic sensor echo pin

# gpiozero objects
motion_sensor = MotionSensor(
    MOTION_SENSOR_PIN,
    queue_len=10,      # Number of readings to average for motion detection
    sample_rate=10,    # Readings per second
    threshold=0.8      # Percentage of queue_len that must be active to trigger
)
green_led = LED(GREEN_LED_PIN)
red_led = LED(RED_LED_PIN)
distance_sensor = DistanceSensor(
    echo=ULTRASONIC_ECHO_PIN,
    trigger=ULTRASONIC_TRIGGER_PIN,
    max_distance=4.0  # Max distance in meters
)

# Sensor Configuration
DISTANCE_THRESHOLD = 0.1  # Threshold in meters to consider garage occupied

# Global state variables
client = None
garage_occupied = False
is_opening_garage = False # Flag indicating if the garage opening sequence is active

def get_distance():
    try:
        return distance_sensor.distance
    except Exception as e:
        print(f"Fehler beim Lesen des Abstands: {e}")
        return -1 # Return -1 on error

def is_garage_occupied():
    distance = get_distance()
    if distance == -1:
        print("Warnung: Konnte Abstand nicht lesen, nehme 'nicht belegt' an.")
        return False # Assume free on error to avoid blocking
    return distance < DISTANCE_THRESHOLD

def blink_specific_led(led_obj, duration=5, blink_time=0.2):
    """Blinks a specific LED for a given duration."""
    end_time = time.time() + duration
    led_obj.off()
    time.sleep(0.01) 
    
    while time.time() < end_time:
        led_obj.on()
        time.sleep(blink_time)
        led_obj.off()
        time.sleep(blink_time)
    led_obj.off()

def update_leds(occupied_status):
    """Updates LEDs based on garage status, unless an opening sequence is active."""
    if is_opening_garage:
        return # LED control is handled by open_garage_procedure during opening

    if occupied_status:
        green_led.off()
        red_led.on()
    else:
        green_led.on()
        red_led.off()

def on_connect(mqtt_client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Erfolgreich mit MQTT Broker verbunden!")
        mqtt_client.subscribe(MQTT_TOPIC_GARAGE_CONTROL)
        print(f"Abonniert auf Topic: {MQTT_TOPIC_GARAGE_CONTROL}")
    else:
        print(f"Verbindung zum MQTT Broker fehlgeschlagen, Rückgabecode: {rc}")

def open_garage_procedure():
    """Handles the garage opening sequence, including safety checks."""
    global is_opening_garage, garage_occupied, client

    if is_opening_garage: # Prevent concurrent execution
        print("Öffnungsvorgang läuft bereits.")
        return

    print("Öffnungsanfrage für Garage erhalten. Prüfe Bedingungen...")
    current_garage_occupied = is_garage_occupied()

    if not current_garage_occupied and not motion_sensor.is_active:
        print("Bedingungen erfüllt. Garage wird geöffnet (grüne LED blinkt für 10s).")
        is_opening_garage = True
        if client and client.is_connected():
            client.publish(MQTT_TOPIC_GARAGE_STATUS, "opening")

        red_led.off()
        green_led.off()

        opening_duration = 10  # seconds
        blink_interval = 0.25
        end_opening_time = time.time() + opening_duration
        
        green_led_currently_on = False
        while time.time() < end_opening_time:
            if motion_sensor.is_active:
                print("BEWEGUNG WÄHREND DES ÖFFNENS ERKANNT (LICHTSCHRANKE)!")
                is_opening_garage = False
                green_led.off()
                if client and client.is_connected():
                    client.publish(MQTT_TOPIC_GARAGE_STATUS, "interrupted_by_motion")
                
                print("Rote LED blinkt für 5 Sekunden.")
                blink_specific_led(red_led, duration=5, blink_time=0.2)
                
                garage_occupied = is_garage_occupied()
                update_leds(garage_occupied)
                if client and client.is_connected():
                    client.publish(MQTT_TOPIC_GARAGE_STATUS, "occupied" if garage_occupied else "free")
                return

            if green_led_currently_on:
                green_led.off()
            else:
                green_led.on()
            green_led_currently_on = not green_led_currently_on
            time.sleep(blink_interval)

        is_opening_garage = False
        green_led.off()
        print("Garagenöffnung (simuliert) abgeschlossen.")
        if client and client.is_connected():
            client.publish(MQTT_TOPIC_GARAGE_STATUS, "opened_successfully")
        
        garage_occupied = is_garage_occupied()
        update_leds(garage_occupied)
        if client and client.is_connected():
            client.publish(MQTT_TOPIC_GARAGE_STATUS, "occupied" if garage_occupied else "free")

    elif current_garage_occupied:
        print("Garage ist belegt. Öffnen nicht möglich.")
        if client and client.is_connected():
            client.publish(MQTT_TOPIC_GARAGE_STATUS, "error_occupied")
    elif motion_sensor.is_active:
        print("Bewegung erkannt (vor Öffnungsversuch). Öffnen aus Sicherheitsgründen nicht möglich.")
        # Optionally publish a status for this case, e.g., "error_motion_before_open"

def on_message(mqtt_client, userdata, msg):
    payload_str = msg.payload.decode()
    print(f"Nachricht empfangen auf Topic '{msg.topic}': {payload_str}")
    
    if msg.topic == MQTT_TOPIC_GARAGE_CONTROL:
        if payload_str == "STATUS_REQUEST": # Handle simple text command
            print("Statusanfrage (Text) empfangen.")
            current_status_str = "opening" if is_opening_garage else ("occupied" if garage_occupied else "free")
            if client and client.is_connected():
                client.publish(MQTT_TOPIC_GARAGE_STATUS, current_status_str)
        else: # Assume JSON for other commands
            try:
                data = json.loads(payload_str) 
                if isinstance(data, dict) and data.get("action") == "open":
                    print("Öffnungsanfrage (JSON) empfangen.")
                    open_garage_procedure()
                else:
                    print(f"Unbekannte JSON-Aktion oder Format in '{payload_str}': {data}")
            except json.JSONDecodeError:
                print(f"Konnte Nachricht nicht als JSON parsen und keine bekannte Text-Aktion: {payload_str}")

def main():
    global client, garage_occupied, is_opening_garage

    # For paho-mqtt >= 2.0:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    # For paho-mqtt < 2.0: client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        print(f"Versuche, mit MQTT Broker auf {MQTT_BROKER}:{MQTT_PORT} zu verbinden...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"Konnte nicht mit MQTT Broker verbinden: {e}")
        print("Das Programm läuft ohne MQTT-Funktionalität weiter.")

    client.loop_start() # Starts a separate thread for MQTT communication

    print("Garagen-Überwachungssystem gestartet. Drücken Sie Strg+C zum Beenden.")
    print(f"Ultraschallsensor: Trigger Pin {ULTRASONIC_TRIGGER_PIN}, Echo Pin {ULTRASONIC_ECHO_PIN}")
    print(f"Bewegungssensor HC SR501 auf Pin {MOTION_SENSOR_PIN}")
    print(f"Grüne LED auf Pin {GREEN_LED_PIN}, Rote LED auf Pin {RED_LED_PIN}")
    
    garage_occupied = is_garage_occupied()
    update_leds(garage_occupied)
    if client.is_connected():
         client.publish(MQTT_TOPIC_GARAGE_STATUS, "occupied" if garage_occupied else "free", retain=True)
    
    try:
        while True:
            if not is_opening_garage: # Only check sensors if no opening sequence is active
                current_status_occupied = is_garage_occupied()
                if current_status_occupied != garage_occupied:
                    print(f"Garagenstatus geändert: {'Belegt' if current_status_occupied else 'Frei'}")
                    garage_occupied = current_status_occupied
                    update_leds(garage_occupied)
                    if client.is_connected():
                        client.publish(MQTT_TOPIC_GARAGE_STATUS, "occupied" if garage_occupied else "free", retain=True)
            time.sleep(0.5) # Main loop interval
    except KeyboardInterrupt:
        print("Programm wird beendet (Strg+C)...")
    finally:
        if client and client.is_connected():
            client.loop_stop()
            client.disconnect()
            print("MQTT-Verbindung getrennt.")
        green_led.off()
        red_led.off()
        print("LEDs ausgeschaltet. Programm beendet.")

if __name__ == '__main__':
    main()
