import time
import board
import busio
import adafruit_vl6180x
# RPi.GPIO durch gpiozero ersetzen
from gpiozero import LED, MotionSensor

# ===== Konfiguration =====
# GPIO Pins
MOTION_SENSOR_PIN = 16    # HC SR501 Motion Sensor
GREEN_LED_PIN = 20        # Grüne LED für freie Garage
RED_LED_PIN = 21          # Rote LED für besetzte Garage / Bewegungserkennung

# gpiozero Objekte initialisieren
motion_sensor = MotionSensor(MOTION_SENSOR_PIN)
green_led = LED(GREEN_LED_PIN)
red_led = LED(RED_LED_PIN)

# VL6180X Sensor Konfiguration
DISTANCE_THRESHOLD = 100  # Schwellenwert in mm (unter diesem Wert gilt ein Auto als erkannt)

# Initialer Zustand der LEDs
green_led.off()
red_led.off()

# ===== VL6180X Setup (I2C) =====
i2c = busio.I2C(board.SCL, board.SDA)  # SCL: Pin 4, SDA: Pin 5
try:
    vl6180x = adafruit_vl6180x.VL6180X(i2c)
    print("VL6180X-Sensor erfolgreich initialisiert")
except Exception as e:
    print(f"Fehler bei VL6180X-Initialisierung: {e}")
    exit(1)

# ===== Hilfsfunktionen =====
def get_distance():
    """
    Liest den Abstand vom VL6180X-Sensor.
    
    Returns:
        int: Abstand in mm oder -1 bei Fehler
    """
    try:
        return vl6180x.range
    except Exception as e:
        print(f"Fehler beim Lesen des Abstands: {e}")
        return -1

def is_garage_occupied():
    """
    Überprüft, ob die Garage belegt ist (Auto erkannt).
    
    Returns:
        bool: True wenn ein Auto erkannt wurde, False wenn nicht
    """
    distance = get_distance()
    if distance == -1:  # Fehler beim Lesen des Abstands
        print("Warnung: Konnte Abstand nicht lesen")
        return False
    
    print(f"Abstand: {distance} mm")
    return distance < DISTANCE_THRESHOLD

def blink_red_led(duration=5, blink_time=0.2):
    """
    Lässt die rote LED für eine bestimmte Zeit blinken.
    
    Args:
        duration: Gesamtdauer des Blinkens in Sekunden
        blink_time: Zeit für einen Blink-Zyklus (an/aus) in Sekunden
    """
    end_time = time.time() + duration
    while time.time() < end_time:
        red_led.on()
        time.sleep(blink_time)
        red_led.off()
        time.sleep(blink_time)
        
        # Überprüfen, ob der Bewegungssensor immer noch aktiviert ist
        if not motion_sensor.is_active:
            break

def update_leds(occupied):
    """
    Aktualisiert die LEDs basierend auf dem Garagenstatus.
    
    Args:
        occupied: True wenn die Garage belegt ist, False wenn frei
    """
    if occupied:
        # Garage belegt: Rote LED an, grüne LED aus
        green_led.off()
        red_led.on()
    else:
        # Garage frei: Grüne LED an, rote LED aus
        green_led.on()
        red_led.off()

# ===== Hauptprogramm =====
try:
    print("Garagen-Überwachungssystem gestartet. Drücken Sie Strg+C zum Beenden.")
    print(f"Distanzsensor VL6180X auf I2C (SDA=Pin 5, SCL=Pin 4)")
    print(f"Bewegungssensor HC SR501 auf Pin {MOTION_SENSOR_PIN}")
    print(f"Grüne LED auf Pin {GREEN_LED_PIN}, Rote LED auf Pin {RED_LED_PIN}")
    
    # Initiale Prüfung des Garagenstatus
    garage_occupied = is_garage_occupied()
    update_leds(garage_occupied)
    
    while True:
        # Überprüfen, ob sich der Garagenstatus geändert hat
        current_status = is_garage_occupied()
        if current_status != garage_occupied:
            garage_occupied = current_status
            print(f"Garagenstatus geändert: {'Belegt' if garage_occupied else 'Frei'}")
            update_leds(garage_occupied)
        
        # Bewegungserkennung
        if motion_sensor.is_active:
            print("Bewegung erkannt!")
            
            # Wenn die Garage belegt ist, blinkt die rote LED
            # Sonst bleibt die grüne LED an, aber die rote LED blinkt zusätzlich
            if garage_occupied:
                red_led.off()  # Kurz ausschalten für den Blink-Effekt
                blink_red_led(5)  # 5 Sekunden blinken
                # Nach dem Blinken wieder den normalen Status herstellen
                update_leds(garage_occupied)
            else:
                # Grüne LED bleibt an, rote LED blinkt
                blink_red_led(5)  # 5 Sekunden blinken
        
        time.sleep(0.5)  # Kurze Pause zur CPU-Entlastung

except KeyboardInterrupt:
    print("Programm wird beendet...")
finally:
    # Keine explizite Aufräumarbeit notwendig für gpiozero
    print("Programm beendet.")
