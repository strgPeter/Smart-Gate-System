from flask import Flask, render_template_string, request, redirect
import paho.mqtt.client as mqtt
from threading import Thread
from datetime import datetime
import json

app = Flask(__name__)

log = []
state = {
    "garage": "unknown",
    "barrier": "unknown"
}

MQTT_BROKER = "10.0.0.1"

#MQTT_TOPICS = ["garage", "barrier", "plate"]
MQTT_TOPICS = ["#"]

mqtt_client = mqtt.Client()

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    timestamp = datetime.now().strftime("%H:%M:%S")
    log.insert(0, {
        "time": timestamp,
        "topic": msg.topic,
        "payload": payload
    })
    if len(log) > 100:
        log.pop()

    # Status speichern für die Ampeln
    if msg.topic == "garage":
        state["garage"] = payload
    elif msg.topic == "barrier":
        try:
            data = json.loads(payload)
            action = data.get("action", "")
            if action == "open":
                state["barrier"] = "open"
            elif action == "closed":
                state["barrier"] = "closed"
        except json.JSONDecodeError:
            state["barrier"] = "unknown"

def mqtt_thread():
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER)
    for topic in MQTT_TOPICS:
#        mqtt_client.subscribe(topic)
        mqtt_client.subscribe("#")
    mqtt_client.loop_forever()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "open_gate":
            mqtt_client.publish("barrier", '{"action":"open"}')
        elif action == "close_gate":
            mqtt_client.publish("barrier", '{"action":"close"}')
        return redirect("/")

    # Farbenlogik für Ampeln
    garage_color = "gray"
    if state["garage"] == "occupied" or state["garage"] == "error_occupied":
        garage_color = "red"
    elif state["garage"] == "free":
        garage_color = "green"

    barrier_color = "gray"
    if state["barrier"] == "open":
        barrier_color = "green"
    elif state["barrier"] == "closed":
        barrier_color = "red"
        
    return render_template_string("""
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }
                h2, h3 { color: #333; }

                .status-box { display: flex; gap: 20px; margin-bottom: 20px; }
                .ampel {
                    width: 100px; height: 100px; border-radius: 50%;
                    display: flex; align-items: center; justify-content: center;
                    font-weight: bold; color: white; font-size: 1em;
                }

                .gray { background: #aaa; }
                .green { background: #4CAF50; }
                .red { background: #f44336; }
                .yellow { background: #ffcc00; color: black; }

                button { margin: 5px; padding: 10px; border-radius: 5px; border: none; background: #008CBA; color: white; cursor: pointer; }
                button:hover { background: #0079a1; }

                .log { background: #fff; border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: scroll; }
                .entry { padding: 5px; border-bottom: 1px solid #eee; }
                .garage { color: darkblue; }
                .barrier { color: darkgreen; }
                .plate { color: darkred; }
                .time { font-size: 0.85em; color: #666; margin-right: 10px; }
            </style>
        </head>
        <body>
            <h2>Smart-Gate Dashboard</h2>

            <div class="status-box">
                <div>
                    <div class="ampel {{ garage_color }}">Garage</div>
                    <p>Status: {{ state.garage }}</p>
                </div>
                <div>
                    <div class="ampel {{ barrier_color }}">Schranke</div>
                    <p>Status: {{ state.barrier }}</p>
                </div>
            </div>

            <h3>Aktionen</h3>
            <form method="post">
                <button name="action" value="open_gate">Schranke öffnen</button>
                <button name="action" value="close_gate">Schranke schließen</button>
            </form>

            <h3>MQTT Log</h3>
            <div class="log">
                {% for entry in log %}
                    <div class="entry {{ entry.topic }}">
                        <span class="time">[{{ entry.time }}]</span>
                        <strong>{{ entry.topic }}</strong>: {{ entry.payload }}
                    </div>
                {% endfor %}
            </div>
            <meta http-equiv="refresh" content="2">
        </body>
        </html>
    """, log=log, state=state, garage_color=garage_color, barrier_color=barrier_color)

if __name__ == "__main__":
    Thread(target=mqtt_thread, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)

