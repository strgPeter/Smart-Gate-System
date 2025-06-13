# Smart Gate System with License Plate Recognition and Environmental Controls

## 1. Introduction

This project develops a smart access control system for a parking garage. It automates the opening and closing of a barrier gate and a garage door based on vehicle license plate recognition, sensor inputs, and environmental conditions. The system also includes features for manual override, safety, and remote monitoring via a web interface.

## 2. Core Functionalities Overview

The system integrates several key modules to manage garage access:

- **License Plate Recognition (LPR):**

  - A camera module (details to be provided with LPR module code) captures images of incoming vehicles for license plate recognition.
  - Recognized plates are intended to be matched against a list of authorized plates for automated access.

- **Barrier Gate Control:**

  - Manages the entry barrier to the parking area.
  - Includes automated opening upon authorization (e.g., via LPR or PIN).
  - Features a PIN fallback mechanism for manual entry.
  - Incorporates a safety mechanism (Force Sensitive Resistor) to prevent closing on a vehicle.
  - _(For detailed information, see `scripts/Barrier-system/README.md`)_

- **Garage Access Management:**

  - Controls access to an individual garage space.
  - Monitors garage occupancy using a distance sensor.
  - Includes a (simulated) opening procedure with safety checks using a motion sensor.
  - Provides status indication via LEDs.
  - _(For detailed information, see `scripts/garage-system/README.md`)_

- **Web Interface (GUI):**
  - Provides a web-based dashboard for real-time system status visualization (e.g., "Gate Open", "Garage Occupied").
  - Displays a log of MQTT messages.
  - Allows for some remote control actions, like opening the barrier.
  - _(For detailed information, see `scripts/webserver/README.md`)_

## 3. System Architecture

The system is built using multiple Raspberry Pi devices that communicate with each other and various sensors/actuators.
An **MQTT Server** acts as the central message broker, enabling decoupled communication between the different components.

- **Input Components:** Camera, Force Sensitive Resistor, Keypad (for PIN entry), Motion Sensor, Distance Sensor.
- **Output Components:** Motors (for barrier gate), LEDs (to simulate the garage gate).
- **Processing Units:** Raspberry Pi 4, Raspberry Pi Zero W, Raspberry Pi 3 Model B.
- **User Interface:** WebUI for monitoring and potentially some control.

## 4. Usage

1.  **Vehicle Approach:** As a vehicle approaches, the LPR system attempts to recognize the license plate.
2.  **Authorized Access (Barrier):** If authorized, the barrier gate opens.
3.  **Fallback Access (Barrier):** If not recognized, the driver can enter a PIN on the Touch pHAT.
4.  **Garage Entry:** User presses the garage access button. If the garage is not occupied, the door opens.
5.  **Safety:** Sensors prevent the barrier and garage door from closing on obstructions.
6.  **Light Automation:** Exterior lights turn on automatically at night if motion is detected.
7.  **Monitoring:** System status and vehicle logs can be viewed on the WebUI.
