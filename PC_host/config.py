import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MQTT Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "192.168.1.181")
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