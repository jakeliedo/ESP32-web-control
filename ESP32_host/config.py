# ESP32 Remote Control Configuration
# Edit this file to customize your remote control settings

# === Network Configuration ===
WIFI_NETWORKS = [
    ("Michelle", "0908800130"),
    ("Vinternal", "Veg@s123"),
    # Add more networks as needed
    # ("YourWiFiName", "YourPassword"),
]

# MQTT Broker Configuration
MQTT_BROKER = "192.168.1.181"  # IP address of PC host
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

# === WC Nodes Configuration ===
WC_NODES = [
    {
        "id": "room1_male", 
        "name": "Room1 Male", 
        "topic": "wc/room1_male/command",
        "icon": "M"
    },
    {
        "id": "room1_female", 
        "name": "Room1 Female", 
        "topic": "wc/room1_female/command",
        "icon": "F"
    },
    {
        "id": "room2_male", 
        "name": "Room2 Male", 
        "topic": "wc/room2_male/command",
        "icon": "M"
    },
    # Add more nodes as needed
    # {
    #     "id": "room3_male", 
    #     "name": "Room3 Male", 
    #     "topic": "wc/room3_male/command",
    #     "icon": "M"
    # },
]

# === Hardware Pin Configuration ===
# ST7789P3 Display
SPI_SCLK = 14   #
SPI_MOSI = 13
SPI_CS = 15
DC_PIN = 2
RST_PIN = 3
# BL_PIN không sử dụng vì backlight đã mặc định nối nguồn

# Status LED
STATUS_LED = 22

# === Display Configuration ===
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 320
BACKLIGHT_ON = True

# UI Colors (RGB565)
UI_COLORS = {
    "bg_color": 0x0000,        # Black
    "header_color": 0x001F,    # Blue
    "text_color": 0xFFFF,      # White
    "selected_color": 0xFFE0,  # Yellow
    "online_color": 0x07E0,    # Green
    "offline_color": 0xF800,   # Red
    "border_color": 0x8410,    # Gray
    "male_color": 0x001F,      # Blue
    "female_color": 0xF81F,    # Magenta
}

# UI Layout
UI_LAYOUT = {
    "header_height": 40,
    "footer_height": 30,
    "node_height": 50,
    "margin": 10,
}

# === System Configuration ===
DEVICE_NAME = "WC Remote Control"
VERSION = "1.0.0"

# Timing (seconds)
HEARTBEAT_INTERVAL = 30
STATUS_TIMEOUT = 60  # Consider node offline after this time
BUTTON_DEBOUNCE = 0.3

# === Debug Configuration ===
DEBUG_ENABLED = True
VERBOSE_LOGGING = True

# === MQTT Topics ===
MQTT_TOPICS = {
    "remote_status": "wc/remote/status",
    "remote_heartbeat": "wc/remote/heartbeat",
    "command_suffix": "/command",
    "status_suffix": "/status"
}

# === Startup Messages ===
STARTUP_MESSAGES = [
    "Initializing...",
    "Connecting WiFi...",
    "Connecting MQTT...",
    "System Ready!"
]

# === Error Messages ===
ERROR_MESSAGES = {
    "wifi_failed": "WiFi Failed!",
    "mqtt_failed": "MQTT Failed!",
    "not_connected": "Not Connected!",
    "send_failed": "Send Failed!",
    "error": "Error!"
}
