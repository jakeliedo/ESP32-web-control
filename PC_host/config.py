import os
import socket
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# MQTT Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER")
if not MQTT_BROKER or MQTT_BROKER in ["0.0.0.0", ""]:
    MQTT_BROKER = get_lan_ip()
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "pc_host")

# Flask Configuration
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "dev_key_change_in_production")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))

# Database Configuration
DB_PATH = os.getenv("DB_PATH", "wc_system.db")
DATABASE_PATH = DB_PATH  # Alias for compatibility

# Web Configuration
WEB_PORT = PORT  # Alias for web port

# WC System Configuration
WC_NODES = {
    "wc1": {"name": "Male Room 1", "type": "male", "location": "Floor 1"},
    "wc2": {"name": "Male Room 2", "type": "male", "location": "Floor 1"},
    "wc3": {"name": "Female Room 1", "type": "female", "location": "Floor 1"}
}