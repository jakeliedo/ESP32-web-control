# app.py
from flask import Flask, render_template_string, request, redirect
import requests

# Địa chỉ IP của ESP32 (thay bằng IP thực tế của bạn)
ESP32_IP = "http://192.168.100.72"

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app)
csrf = CSRFProtect(app)
# Initialize MQTT Handler with socketio for real-time updates
mqtt_handler = MQTTHandler(socketio)

def check_and_start_mosquitto():
    """Check if Mosquitto service is running and try to start it if not"""
    try:
        # Check status
        result = subprocess.run(['sc', 'query', 'mosquitto'], 
                            capture_output=True, text=True)
        
        if "RUNNING" not in result.stdout:
            print("⚠️ Mosquitto service is not running. Attempting to start it...")
            try:
                # Try to start the service
                subprocess.run(['net', 'start', 'mosquitto'], 
                            capture_output=True, text=True)
                
                # Wait for service to start
                time.sleep(2)
                
                # Check if started successfully
                result = subprocess.run(['sc', 'query', 'mosquitto'], 
                                    capture_output=True, text=True)
                
                if "RUNNING" in result.stdout:
                    print("✅ Successfully started Mosquitto service")
                    return True
                else:
                    print("❌ Failed to start Mosquitto service")
                    print("Please make sure Mosquitto is installed correctly as a service")
                    return False
            except Exception as e:
                print(f"❌ Error starting Mosquitto service: {e}")
                return False
        else:
            print("✅ Mosquitto service is already running")
            return True
    except Exception as e:
        print(f"❌ Error checking Mosquitto service: {e}")
        return False

def check_mqtt_broker():
    """Check if MQTT broker is accessible"""
    import socket
    try:
        from config import MQTT_BROKER, MQTT_PORT
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((MQTT_BROKER, MQTT_PORT))
        s.close()
        if result == 0:
            print(f"✅ MQTT broker at {MQTT_BROKER}:{MQTT_PORT} is available")
            return True
        else:
            print(f"❌ MQTT broker at {MQTT_BROKER}:{MQTT_PORT} is not accessible")
            print("Please check if Mosquitto service is running")
            return False
    except Exception as e:
        print(f"❌ Error checking MQTT connection: {e}")
        return False

# Check Mosquitto service status and start if needed
check_and_start_mosquitto()

# Connect to MQTT broker
if check_mqtt_broker():
    if mqtt_handler.connect():
        print("✅ Successfully connected to MQTT broker")
    else:
        print("⚠️ Could not connect to MQTT broker. Running in limited mode.")
else:
    print("⚠️ MQTT broker is not accessible. Running in limited mode.")

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