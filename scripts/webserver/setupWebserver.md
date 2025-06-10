# Webserver Setup Guide

This guide explains how to set up and run the `webserver.py` Flask application for the Smart Gate System.

## What does `webserver.py` do?

The `webserver.py` script provides a web dashboard for monitoring and controlling the Smart Gate System. It connects to an MQTT broker, receives real-time status updates from the garage and barrier, and allows users to open or close the barrier gate via a web interface. The dashboard displays the current state of the garage and barrier, and shows a live log of MQTT messages.

## Setup Instructions

### 1. Clone the Repository

If you haven't already, clone the project repository:

```sh
git clone <repository-url>
cd Smart-Gate-System/scripts/webserver
```

### 2. Create and Activate a Virtual Environment (Recommended)
It is recommended to use a Python virtual environment to avoid dependency conflicts:

```sh
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install the required Python packages using pip:

```sh
pip install flask paho-mqtt
```

If you want to save these dependencies for future use, you can run:

```sh
pip freeze > requirements.txt
```

### 4. Configure the MQTT Broker Address
By default, the MQTT broker address is set to 10.0.0.1 in webserver.py.
If your broker runs on a different host, edit the MQTT_BROKER variable at the top of the file.

### 5. Run the Webserver
Start the Flask webserver with:

```sh
python webserver.py
```

The web interface will be available at http://localhost:5000.

### 6. Deactivate the Virtual Environment (Optional)
When you're done, you can deactivate the virtual environment:

```sh
deactivate
```

Note:
Make sure your MQTT broker is running and accessible from the machine where you start the webserver.