from pinpad import loop_keypad
from mqtt_handler import start_mqtt
from barrier_control import monitor_fsr_led
import threading


if __name__ == "__main__":
    print("System started.")

    # Start MQTT in background
    mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
    mqtt_thread.start()

     # Start FSR LED monitor in background
    led_thread = threading.Thread(target=monitor_fsr_led, daemon=True)
    led_thread.start()

    # Start keypad input loop
    loop_keypad()
