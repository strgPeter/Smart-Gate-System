import time
import paho.mqtt.client as mqtt
from gpiozero import LED, MotionSensor, DistanceSensor
import json # Importiere das json Modul

# ===== MQTT Konfiguration =====
MQTT_BROKER = "localhost"  # BITTE ANPASSEN: Adresse deines MQTT Brokers
MQTT_PORT = 1883
MQTT_TOPIC_GARAGE_CONTROL = "barrier"
MQTT_TOPIC_GARAGE_STATUS = "garage"

# ===== Konfiguration =====
# GPIO Pins
MOTION_SENSOR_PIN = 16    # HC SR501 Motion Sensor
GREEN_LED_PIN = 20        # Grüne LED für freie Garage
RED_LED_PIN = 21          # Rote LED für besetzte Garage / Bewegungserkennung
ULTRASONIC_TRIGGER_PIN = 23  # Trigger-Pin für Ultraschallsensor
ULTRASONIC_ECHO_PIN = 24     # Echo-Pin für Ultraschallsensor

# gpiozero Objekte initialisieren
motion_sensor = MotionSensor(MOTION_SENSOR_PIN)
green_led = LED(GREEN_LED_PIN)
red_led = LED(RED_LED_PIN)
distance_sensor = DistanceSensor(
    echo=ULTRASONIC_ECHO_PIN,
    trigger=ULTRASONIC_TRIGGER_PIN,
    max_distance=4.0
)

# Sensor Konfiguration
DISTANCE_THRESHOLD = 0.1  # Schwellenwert in Metern

# Globale Variablen
client = None # MQTT Client Instanz
garage_occupied = False
is_opening_garage = False # Zustand, ob die Garage gerade öffnet

# ===== Hilfsfunktionen =====
def get_distance():
    try:
        return distance_sensor.distance
    except Exception as e:
        print(f"Fehler beim Lesen des Abstands: {e}")
        return -1

def is_garage_occupied():
    distance = get_distance()
    if distance == -1:
        print("Warnung: Konnte Abstand nicht lesen, nehme 'nicht belegt' an.")
        return False # Im Fehlerfall als frei annehmen, um Blockaden zu vermeiden
    
    # print(f"Abstand: {distance:.2f} m") # Für Debugging bei Bedarf aktivieren
    return distance < DISTANCE_THRESHOLD

def blink_specific_led(led_obj, duration=5, blink_time=0.2):
    """Lässt eine spezifische LED für eine bestimmte Zeit blinken."""
    end_time = time.time() + duration
    led_obj.off() # Sicherstellen, dass die LED initial aus ist
    time.sleep(0.01) # Kurze Pause
    
    while time.time() < end_time:
        led_obj.on()
        time.sleep(blink_time)
        led_obj.off()
        time.sleep(blink_time)
    led_obj.off() # Sicherstellen, dass die LED am Ende aus ist

def update_leds(occupied_status):
    """Aktualisiert die LEDs basierend auf dem Garagenstatus, außer beim Öffnen."""
    global is_opening_garage
    if is_opening_garage:
        # Während des speziellen Öffnungsvorgangs (grünes Blinken)
        # wird die LED-Steuerung dort gehandhabt.
        return

    if occupied_status:
        green_led.off()
        red_led.on()
    else:
        green_led.on()
        red_led.off()

# ===== MQTT Callbacks =====
def on_connect(mqtt_client, userdata, flags, rc, properties=None): # 'properties' für paho-mqtt v2+
    if rc == 0:
        print("Erfolgreich mit MQTT Broker verbunden!")
        mqtt_client.subscribe(MQTT_TOPIC_GARAGE_CONTROL)
        mqtt_client.subscribe(MQTT_TOPIC_GARAGE_STATUS)
        print(f"Abonniert auf Topic: {MQTT_TOPIC_GARAGE_CONTROL}")
        print(f"Abonniert auf Topic: {MQTT_TOPIC_GARAGE_STATUS}")
    else:
        print(f"Verbindung zum MQTT Broker fehlgeschlagen, Rückgabecode: {rc}")

def open_garage_procedure():
    """Führt die Sequenz zum Öffnen der Garage aus."""
    global is_opening_garage, garage_occupied, client

    if is_opening_garage: # Verhindere parallele Ausführung
        print("Öffnungsvorgang läuft bereits.")
        return

    print("Öffnungsanfrage für Garage erhalten. Prüfe Bedingungen...")
    current_garage_occupied = is_garage_occupied() # Status vor dem Öffnen prüfen

    if not current_garage_occupied and not motion_sensor.is_active:
        print("Bedingungen erfüllt. Garage wird geöffnet (grüne LED blinkt für 10s).")
        is_opening_garage = True
        client.publish(MQTT_TOPIC_GARAGE_STATUS, "opening")

        # Alle LEDs aus, bevor das Blinken beginnt
        red_led.off()
        green_led.off()

        opening_duration = 10  # Sekunden
        blink_interval = 0.25  # An/Aus Zeit für grünes Blinken
        end_opening_time = time.time() + opening_duration
        
        green_led_currently_on = False
        while time.time() < end_opening_time:
            if motion_sensor.is_active:
                print("BEWEGUNG WÄHREND DES ÖFFNENS ERKANNT (LICHTSCHRANKE)!")
                is_opening_garage = False
                green_led.off() # Grüne LED sofort ausschalten
                client.publish(MQTT_TOPIC_GARAGE_STATUS, "interrupted_by_motion")
                
                print("Rote LED blinkt für 5 Sekunden.")
                blink_specific_led(red_led, duration=5, blink_time=0.2)
                
                garage_occupied = is_garage_occupied() # Status neu prüfen
                update_leds(garage_occupied) # Korrekte LEDs nach rotem Blinken
                client.publish(MQTT_TOPIC_GARAGE_STATUS, "occupied" if garage_occupied else "free")
                return # Prozedur beenden

            # Grünes Blinken fortsetzen
            if green_led_currently_on:
                green_led.off()
            else:
                green_led.on()
            green_led_currently_on = not green_led_currently_on
            time.sleep(blink_interval)

        is_opening_garage = False
        green_led.off() # Sicherstellen, dass sie aus ist
        print("Garagenöffnung (simuliert) abgeschlossen.")
        client.publish(MQTT_TOPIC_GARAGE_STATUS, "opened_successfully")
        
        garage_occupied = is_garage_occupied() # Status neu prüfen
        update_leds(garage_occupied) # Korrekte LEDs nach erfolgreichem Öffnen
        client.publish(MQTT_TOPIC_GARAGE_STATUS, "occupied" if garage_occupied else "free")

    elif current_garage_occupied:
        print("Garage ist belegt. Öffnen nicht möglich.")
        client.publish(MQTT_TOPIC_GARAGE_STATUS, "error_occupied")
    elif motion_sensor.is_active:
        print("Bewegung erkannt (vor Öffnungsversuch). Öffnen aus Sicherheitsgründen nicht möglich.")

def on_message(mqtt_client, userdata, msg):
    global garage_occupied # Zugriff auf die globale Variable
    payload_str = msg.payload.decode()
    print(f"Nachricht empfangen auf Topic '{msg.topic}': {payload_str}")
    
    if msg.topic == MQTT_TOPIC_GARAGE_CONTROL:
        try:
            data = json.loads(payload_str) # Versuche, den Payload als JSON zu parsen
            if isinstance(data, dict) and data.get("action") == "open":
                open_garage_procedure()
            else:
                print(f"Unbekannte JSON-Aktion oder Format: {data}")
        except json.JSONDecodeError:
            print(f"Fehler beim Parsen der JSON-Nachricht: {payload_str}")
            if payload_str == "STATUS_REQUEST": # Behalte die alte STATUS_REQUEST Logik bei, falls sie nicht JSON ist
                current_status_str = "occupied" if garage_occupied else "free"
                if is_opening_garage:
                    current_status_str = "opening"
                if client and client.is_connected():
                    client.publish(MQTT_TOPIC_GARAGE_STATUS, current_status_str)
    elif msg.topic == MQTT_TOPIC_GARAGE_CONTROL and payload_str == "STATUS_REQUEST":
        current_status_str = "occupied" if garage_occupied else "free"
        if is_opening_garage:
            current_status_str = "opening"
        if client and client.is_connected():
            client.publish(MQTT_TOPIC_GARAGE_STATUS, current_status_str)


# ===== Hauptprogramm =====
def main():
    global client, garage_occupied, is_opening_garage

    # MQTT Client initialisieren
    # Für paho-mqtt < 2.0: client = mqtt.Client()
    # Für paho-mqtt >= 2.0:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        print(f"Versuche, mit MQTT Broker auf {MQTT_BROKER}:{MQTT_PORT} zu verbinden...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"Konnte nicht mit MQTT Broker verbinden: {e}")
        print("Das Programm läuft ohne MQTT-Funktionalität weiter.")
        # Optional: return, um das Programm zu beenden, wenn MQTT kritisch ist

    client.loop_start() # Startet einen separaten Thread für die MQTT-Kommunikation

    print("Garagen-Überwachungssystem gestartet. Drücken Sie Strg+C zum Beenden.")
    print(f"Ultraschallsensor: Trigger Pin {ULTRASONIC_TRIGGER_PIN}, Echo Pin {ULTRASONIC_ECHO_PIN}")
    print(f"Bewegungssensor HC SR501 auf Pin {MOTION_SENSOR_PIN}")
    print(f"Grüne LED auf Pin {GREEN_LED_PIN}, Rote LED auf Pin {RED_LED_PIN}")
    
    # Initiale Prüfung und Setzen des Garagenstatus
    garage_occupied = is_garage_occupied()
    update_leds(garage_occupied)
    if client.is_connected():
         client.publish(MQTT_TOPIC_GARAGE_STATUS, "occupied" if garage_occupied else "free", retain=True)
    
    try:
        while True:
            if not is_opening_garage: # Nur wenn keine Öffnungssequenz läuft
                current_status_occupied = is_garage_occupied()
                if current_status_occupied != garage_occupied:
                    print(f"Garagenstatus geändert: {'Belegt' if current_status_occupied else 'Frei'}")
                    garage_occupied = current_status_occupied
                    update_leds(garage_occupied)
                    if client.is_connected():
                        client.publish(MQTT_TOPIC_GARAGE_STATUS, "occupied" if garage_occupied else "free", retain=True)

            time.sleep(0.5) # Hauptschleifen-Intervall

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
