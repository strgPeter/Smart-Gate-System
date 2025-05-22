# Smart Gate System with License Plate Recognition and Environmental Controls

## 1. Introduction

This project develops a smart access control system for a parking garage. It automates the opening and closing of a barrier gate and a garage door based on vehicle license plate recognition, sensor inputs, and environmental conditions. The system also includes features for manual override, safety, and remote monitoring via a web interface.

## 2. Core Functionalities

The system is comprised of several key functionalities:

*   **License Plate Recognition (LPR):**
    *   A camera module captures images of incoming vehicles.
    *   Image processing and machine learning techniques are used to recognize license plates.
    *   Recognized plates are matched against a list of authorized plates.

*   **Barrier Gate Control:**
    *   Upon successful LPR and authorization, a servo motor automatically opens the barrier gate.
    *   **PIN Fallback:** If a license plate is unknown or not in the system, a PIN can be entered via a local interface (Touch pHAT) to open the barrier gate.
    *   **Safety Mechanism:** A force-sensitive resistor (or light barrier as mentioned in requirements) detects if a vehicle is under the gate, preventing it from closing on the vehicle.

*   **Garage Access Management:**
    *   **Entry Request:** A button must be pressed to request access to the garage.
    *   **Occupancy Detection:** A distance sensor detects if the garage spot is currently occupied. The garage door will not open if the spot is already taken.
    *   **Door Safety:** A short flex sensor ensures no vehicle or object is under the garage door while it's opening or closing.
    *   **Door Closing:**
        *   Can be closed via a button inside the garage.
        *   Automatic closure can be triggered if the safety flex sensor hasn't been activated for 1 minute (indicating the car has left or never fully entered).
        *   Alternatively, a pressure sensor (or the distance sensor indicating occupancy) can trigger a close request after 30 seconds if a car is parked.

*   **Password Fallback (General Access):**
    *   If a vehicle is not recognized by LPR, a local interface allows manual password input to request access (distinct from the barrier gate PIN fallback, potentially for the garage door or as a general override).

*   **Light Automation:**
    *   A photocell sensor detects ambient light levels (day/night).
    *   If it's dark and the camera registers motion (e.g., an approaching vehicle), an exterior light turns on.
    *   The light remains on until no motion is registered for a specified period (e.g., 30 seconds).

*   **Web Interface (GUI):**
    *   Provides real-time system status visualization (e.g., "Gate Open", "Garage Occupied", "Light On").
    *   Displays a log of the last few detected vehicles and access events.

## 3. System Architecture

The system is built using multiple Raspberry Pi devices that communicate with each other and various sensors/actuators.
An **MQTT Server** acts as the central message broker, enabling decoupled communication between the different components.

*   **Input Components:** Camera, Photo Cell Sensor, Force Sensitive Resistor, Touch pHAT (for PIN entry), Button, Short Flex Sensor, Distance Ranging Sensor.
*   **Output Components:** Motors (for barrier gate and garage door), LED Light.
*   **Processing Units:** Raspberry Pi 4, Raspberry Pi Zero W, Raspberry Pi 3 Model B.
*   **User Interface:** WebUI for monitoring and potentially some control.

**(Refer to `system_diagram.png` for a visual representation of the architecture and data flow.)**
*(You would include the provided diagram image in your project repository with this name)*

## 4. Hardware Components

*   Raspberry Pi 4
*   Raspberry Pi Zero W Essential Kit
*   Raspberry Pi 3 Model B
*   Sensor pack 900 (containing Photo Cell Sensor, Force sensitive resistor)
*   2x DC Motor in Micro Servo Body (for barrier gate and garage door)
*   Adafruit Parts Pal (general prototyping parts)
*   Pimoroni Touch pHAT for Raspberry Pi Zero (for PIN/Password input)
*   Short Flex Sensor (for garage door safety)
*   Time of Flight Distance Ranging Sensor (for garage occupancy)
*   Raspberry Pi Zero v1.3 Camera Cable
*   Raspberry Pi Camera Board v2 - 8 Megapixels

## 5. Software and Technologies

*   **Operating System:** Raspberry Pi OS (or similar Linux distribution)
*   **Primary Language:** Python (assumed for Raspberry Pi development, image processing, ML)
*   **License Plate Recognition:** OpenCV, Tesseract OCR, or a dedicated LPR library/ML model.
*   **Communication Protocol:** MQTT
*   **Web Technologies:** HTML, CSS, JavaScript (for the WebUI), potentially a Python web framework (e.g., Flask, Django) for the backend.

## 6. Project Team & Responsibilities

The project is divided into modules, with each team member responsible for specific sensor-actuator combinations:

*   **Christian Donnabauer:** UI (Web Interface)
*   **Ryo Moschnitschka:** Garagensteuerung (Garage Door Control, Occupancy Sensing)
*   **Peter Leitner:** Einfahrtlicht (Entrance Light Automation)
*   **Tobias Wösenböck:** Schranke - LPR (Barrier Gate LPR System)
*   **Simon Wimmer:** Schranke - Buttons + Force Sensitive Resistor (Barrier Gate Manual Controls, PIN Fallback, Safety Sensor)

## 7. Project Timeline Overview

The project is structured in phases:

*   **Phase 1 (approx. 01.05 - 01.06):**
    *   Familiarization with hardware/software.
    *   Implementation of all needed functions for individual modules.
    *   Connection and integration of components via MQTT.
    *   Start of work on presentation and report.
    *   README and Demo Video creation.
*   **Phase 2 (approx. 05.06 - 13.06):**
    *   Final Presentation Meeting.
    *   Project Presentation.
    *   Final Report Meeting.
    *   Project Report submission.

## 8. Setup and Installation

*(This section would typically contain instructions on how to set up the hardware, install dependencies, configure the Raspberry Pis, and run the software. Placeholder for now.)*

1.  **Hardware Setup:**
    *   Connect all sensors and actuators to the respective Raspberry Pi units as per the system diagram.
2.  **Software Installation:**
    *   Flash Raspberry Pi OS onto SD cards.
    *   Install Python and necessary libraries (e.g., `paho-mqtt`, OpenCV, RPi.GPIO).
    *   Set up the MQTT broker (e.g., Mosquitto) on one of the Pis or a separate server.
    *   Clone this repository: `git clone <repository-url>`
3.  **Configuration:**
    *   Configure network settings for all Raspberry Pis.
    *   Update MQTT broker addresses in the scripts.
    *   Populate the authorized license plate list.
4.  **Running the System:**
    *   Execute the main Python scripts on each Raspberry Pi.
    *   Access the WebUI via a browser.

## 9. Usage

1.  **Vehicle Approach:** As a vehicle approaches, the LPR system attempts to recognize the license plate.
2.  **Authorized Access (Barrier):** If authorized, the barrier gate opens.
3.  **Fallback Access (Barrier):** If not recognized, the driver can enter a PIN on the Touch pHAT.
4.  **Garage Entry:** User presses the garage access button. If the garage is not occupied, the door opens.
5.  **Safety:** Sensors prevent the barrier and garage door from closing on obstructions.
6.  **Light Automation:** Exterior lights turn on automatically at night if motion is detected.
7.  **Monitoring:** System status and vehicle logs can be viewed on the WebUI.

## 10. License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details (if you choose to add one).
