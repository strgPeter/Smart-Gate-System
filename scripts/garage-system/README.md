# Garage Control System (`garage.py`)

## Overview

`garage.py` is a Python script designed to manage access to a garage space using a Raspberry Pi. It monitors the garage's occupancy status using an ultrasonic distance sensor and controls LED indicators. It also includes a safety feature using a motion sensor to prevent the garage door from (simulated) opening if motion is detected or if the garage is already occupied. The script communicates its status and receives commands via MQTT.

## Hardware Interaction

The script interacts with the following hardware components connected to a Raspberry Pi:

- **Ultrasonic Distance Sensor (HC-SR04 or similar):**
  - Connected to `ULTRASONIC_TRIGGER_PIN` and `ULTRASONIC_ECHO_PIN`.
  - Used to measure the distance to objects in the garage, determining if it's occupied or free.
- **Motion Sensor (HC-SR501 PIR):**
  - Connected to `MOTION_SENSOR_PIN`.
  - Used as a safety measure to detect motion during the garage opening sequence or before attempting to open.
- **LEDs:**
  - **Green LED:** Connected to `GREEN_LED_PIN`. Indicates the garage is free.
  - **Red LED:** Connected to `RED_LED_PIN`. Indicates the garage is occupied or an error condition (e.g., motion detected during opening).

## MQTT Interface

The script uses MQTT for communication:

- **Subscribes to:**
  - `MQTT_TOPIC_GARAGE_CONTROL` (default: `"barrier"`): Listens for commands.
    - **JSON command:** `{"action": "open"}` - Initiates the garage opening procedure.
    - **Text command:** `"STATUS_REQUEST"` - Responds with the current garage status.
- **Publishes to:**
  - `MQTT_TOPIC_GARAGE_STATUS` (default: `"garage"`): Publishes the current state of the garage.
    - `"free"`: Garage is not occupied.
    - `"occupied"`: Garage is occupied.
    - `"opening"`: Garage opening sequence is in progress.
    - `"opened_successfully"`: Garage opening sequence completed without interruption.
    - `"interrupted_by_motion"`: Garage opening was interrupted by motion detection.
    - `"error_occupied"`: Attempted to open while already occupied.
    - Status messages indicating occupancy (`"free"`, `"occupied"`) are published with `retain=True`.

## Key Logic

- **Occupancy Detection:** Continuously checks the distance sensor. If the measured distance is below `DISTANCE_THRESHOLD`, the garage is considered occupied.
- **Garage Opening Procedure (`open_garage_procedure`):**
  1.  Triggered by an MQTT "open" command.
  2.  Checks if the garage is currently free AND no motion is detected by the PIR sensor.
  3.  If conditions are met:
      - Publishes "opening" status.
      - Simulates garage door opening by blinking the green LED for a defined duration (`opening_duration`).
      - During this blinking period, if the motion sensor detects movement, the opening is immediately interrupted:
        - Publishes "interrupted_by_motion" status.
        - Blinks the red LED to signal an error.
        - Re-evaluates and publishes the final occupancy status.
      - If the opening completes without interruption, publishes "opened_successfully" and then the final occupancy status.
  4.  If conditions are not met (garage occupied or motion detected initially), it publishes an appropriate error status (e.g., "error_occupied").
- **LED Status Indicators:**
  - Green LED ON: Garage is free.
  - Red LED ON: Garage is occupied.
  - Green LED Blinking: Garage is in the process of opening.
  - Red LED Blinking: Error condition (e.g., motion detected during opening).

## Configuration

Key parameters can be configured at the beginning of the `garage.py` script:

- `MQTT_BROKER`, `MQTT_PORT`: MQTT broker connection details.
- `MQTT_TOPIC_GARAGE_CONTROL`, `MQTT_TOPIC_GARAGE_STATUS`: MQTT topics for control and status.
- `MOTION_SENSOR_PIN`, `GREEN_LED_PIN`, `RED_LED_PIN`, `ULTRASONIC_TRIGGER_PIN`, `ULTRASONIC_ECHO_PIN`: GPIO pin assignments for connected hardware.
- `DISTANCE_THRESHOLD`: The distance (in meters) below which the garage is considered occupied.
- Motion sensor parameters (`queue_len`, `sample_rate`, `threshold`) for `gpiozero.MotionSensor`.
- Durations and intervals for LED blinking and opening sequence.

## Dependencies

- **paho-mqtt:** For MQTT communication.
  - Install via `pip install paho-mqtt`
- **gpiozero:** For easy interfacing with Raspberry Pi GPIO devices.
  - Typically pre-installed on Raspberry Pi OS. Install via `pip install gpiozero` if needed.
  - May require `pigpio` for certain functionalities (`sudo apt install pigpio python3-pigpio`).

## How to Run

1.  Ensure all hardware (sensors, LEDs) is correctly connected to the Raspberry Pi GPIO pins as defined in the script.
2.  Make sure an MQTT broker is running and accessible from the Raspberry Pi.
3.  Update the configuration variables at the top of the script (especially MQTT broker address and GPIO pins) if necessary.
4.  Execute the script from a terminal on the Raspberry Pi:
    ```sh
    python3 garage.py
    ```
    The script requires appropriate permissions to access GPIO pins.

The script will then connect to the MQTT broker, start monitoring the sensors, and update the LEDs and MQTT status accordingly.
