# app.py
from flask import Flask, render_template_string, request, redirect
import requests

# Địa chỉ IP của ESP32 (thay bằng IP thực tế của bạn)
ESP32_IP = "http://192.168.100.72"

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app)

# Initialize MQTT Handler with socketio for real-time updates
mqtt_handler = MQTTHandler(socketio)

# Connect to MQTT broker
if not mqtt_handler.connect():
    print("Warning: Could not connect to MQTT broker. Running in limited mode.")

# Routes
@app.route('/')
def index():
    if request.method == "POST":
        action = request.form.get("action")
        # Gửi lệnh tới ESP32
        try:
            resp = requests.post(f"{ESP32_IP}/control", data={"ch": action}, timeout=2)
        except Exception as e:
            print("Lỗi gửi lệnh tới ESP32:", e)
        return redirect("/")
    return render_template_string(HTML)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')