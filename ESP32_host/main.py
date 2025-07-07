"""
ESP32 Remote Control with ST7789P3 3.2" Display
WC Control System Remote Interface
"""

import machine
import time
import network
import json
from umqtt.simple import MQTTClient
import ubinascii
from machine import Pin, SPI
from lib.st7789p3 import ST7789P3
from lib.simple_ui import SimpleUI
from lib.remote_control import RemoteControl
from lib.xpt2046 import XPT2046

# === Hardware Configuration ===
# ST7789P3 3.2" Display connections
SPI_SCLK = 14   # Serial Clock
SPI_MOSI = 13   # Master Out Slave In
SPI_CS = 15     # Chip Select
DC_PIN = 2      # Data/Command
RST_PIN = 3     # Reset
# BL_PIN không sử dụng vì backlight đã mặc định nối nguồn

# Status LED
STATUS_LED = 22

# === Network Configuration ===
WIFI_NETWORKS = [
    ("Michelle", "0908800130"),
    ("Vinternal", "Veg@s123")
]

# MQTT Configuration
MQTT_BROKER = "192.168.1.181"
MQTT_PORT = 1883
CLIENT_ID = f"wc_remote_{ubinascii.hexlify(machine.unique_id()).decode()[:8]}"

# === Device Configuration ===
DEVICE_NAME = "WC Remote Control"
VERSION = "1.0.0"

print(f"🎮 {DEVICE_NAME} v{VERSION}")
print(f"🆔 Client ID: {CLIENT_ID}")
print("🔧 Initializing hardware...")

# === WC Nodes Configuration ===
WC_NODES = [
    {"id": "room1_male", "name": "Room1 Male", "topic": "wc/room1_male/command"},
    {"id": "room1_female", "name": "Room1 Female", "topic": "wc/room1_female/command"},
    {"id": "room2_male", "name": "Room2 Male", "topic": "wc/room2_male/command"}
]

# Global variables
current_selection = 0
wifi_connected = False
mqtt_connected = False
node_status = {}
last_heartbeat = 0
display = None
ui = None
remote_control = None

# === Hardware Initialization ===

# Initialize status LED
status_led = Pin(STATUS_LED, Pin.OUT)
status_led.off()

# Initialize SPI for display
spi = SPI(2, baudrate=40000000, sck=Pin(SPI_SCLK), mosi=Pin(SPI_MOSI))

# Initialize display (không truyền BL_PIN)
display = ST7789P3(spi, SPI_CS, DC_PIN, RST_PIN)
display.init()
print("📺 Display initialized")

# Initialize UI
ui = SimpleUI(display)
print("🎨 UI initialized")

# Initialize all node status as offline
for node in WC_NODES:
    node_status[node["id"]] = {"status": "offline", "last_seen": 0}

print("✅ Hardware initialized")

# === Touch XPT2046 Configuration ===
TP_CLK   = 25    # TP_CLK   -> IO25
TP_CS    = 33    # TP_CS    -> IO33
TP_DIN   = 32    # TP_DIN   -> IO32
TP_DOUT  = 39    # TP_DOUT  -> IO39
TP_IRQ   = 36    # TP_IRQ   -> IO36

# Initialize SPI for touch
spi_touch = SPI(1, baudrate=1000000, sck=Pin(TP_CLK), mosi=Pin(TP_DIN), miso=Pin(TP_DOUT))
touch = XPT2046(spi_touch, cs=Pin(TP_CS), irq=Pin(TP_IRQ))

def show_startup_screen():
    """Show startup splash screen"""
    ui.clear_screen()
    ui.draw_header("WC Remote v1.0")
    
    # Draw startup message
    ui.display.text("Initializing...", 50, 100, ST7789P3.WHITE)
    ui.display.text("Connecting WiFi", 50, 120, ST7789P3.YELLOW)
    
    ui.draw_footer(wifi_connected, mqtt_connected)

def connect_wifi():
    """Connect to WiFi"""
    global wifi_connected
    
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    
    for ssid, password in WIFI_NETWORKS:
        print(f"🌐 Trying to connect to {ssid}...")
        
        # Update display
        ui.display.text(f"Trying: {ssid}", 50, 140, ST7789P3.CYAN)
        
        sta_if.connect(ssid, password)
        
        for i in range(20):
            if sta_if.isconnected():
                ip = sta_if.ifconfig()[0]
                print(f"✅ Connected to {ssid}. IP: {ip}")
                wifi_connected = True
                
                # Update display
                ui.display.text(f"Connected: {ip}", 50, 160, ST7789P3.GREEN)
                return True, ip
            
            print(".", end="")
            time.sleep(0.5)
        
        print(f"❌ Failed to connect to {ssid}")
    
    print("❌ WiFi connection failed")
    wifi_connected = False
    return False, None

def mqtt_callback(topic, msg):
    """Handle incoming MQTT messages"""
    global node_status
    
    topic_str = topic.decode()
    try:
        msg_str = msg.decode()
        print(f"📨 Received: {topic_str} = {msg_str}")
        
        # Parse JSON message
        if msg_str.startswith('{'):
            data = json.loads(msg_str)
        else:
            data = {"message": msg_str}
        
        # Handle status updates from WC nodes
        if topic_str.startswith("wc/") and topic_str.endswith("/status"):
            # Extract node ID from topic (e.g., "wc/room1_male/status" -> "room1_male")
            node_id = topic_str.split('/')[1]
            
            if node_id in node_status:
                node_status[node_id]["status"] = data.get("status", "online")
                node_status[node_id]["last_seen"] = time.time()
                print(f"📊 Updated {node_id} status: {data.get('status', 'online')}")
                
                # Update remote control status
                if remote_control:
                    remote_control.update_node_status(node_id, data.get("status", "online"))
                
                # Update display
                update_main_screen()
        
        # Blink LED to show activity
        status_led.on()
        time.sleep(0.1)
        status_led.off()
        
    except Exception as e:
        print(f"❌ MQTT callback error: {e}")

def send_flush_command(node):
    """Send flush command to selected node"""
    global remote_control
    
    if not remote_control or not remote_control.is_connected():
        print("❌ Remote control not connected")
        ui.show_message("Not Connected!", 2000)
        return False
    
    try:
        success = remote_control.send_flush_command(node)
        
        if success:
            # Visual feedback
            status_led.on()
            time.sleep(0.2)
            status_led.off()
            
            # Show confirmation on display
            ui.show_message(f"Flushing {node['name']}", 2000)
            return True
        else:
            ui.show_message("Send Failed!", 2000)
            return False
        
    except Exception as e:
        print(f"❌ Failed to send flush command: {e}")
        ui.show_message("Error!", 2000)
        return False

def update_main_screen():
    """Update the main screen display"""
    ui.clear_screen()
    ui.draw_header("WC Remote Control")
    
    # Draw node list
    ui.draw_node_list(WC_NODES, current_selection, node_status)
    
    # Draw footer with status
    ui.draw_footer(wifi_connected, mqtt_connected)

def connect_mqtt():
    """Connect to MQTT broker"""
    global remote_control, mqtt_connected
    
    print(f"🔗 Connecting to MQTT broker at {MQTT_BROKER}...")
    
    try:
        # Initialize remote control
        remote_control = RemoteControl(CLIENT_ID, MQTT_BROKER, MQTT_PORT)
        remote_control.set_callback(mqtt_callback)
        
        # Connect
        if remote_control.connect():
            mqtt_connected = True
            
            # Subscribe to WC nodes
            if remote_control.subscribe_to_nodes(WC_NODES):
                print("✅ Successfully subscribed to all WC nodes")
                return True
            else:
                print("⚠️ Connected but failed to subscribe")
                return False
        else:
            mqtt_connected = False
            return False
        
    except Exception as e:
        print(f"❌ MQTT connection failed: {e}")
        mqtt_connected = False
        return False

def check_touch_flush():
    """Check if touch is in any FLUSH button area and trigger flush command for the correct node"""
    if touch.touched():
        x, y = touch.get_touch()
        # Định nghĩa vùng cảm ứng cho từng nút FLUSH (chỉnh lại theo UI thực tế)
        FLUSH_BTN_AREAS = [
            (60, 60, 180, 120),   # Node 0 (Room1 Male)
            (60, 140, 180, 200),  # Node 1 (Room1 Female)
            (60, 220, 180, 280),  # Node 2 (Room2 Male)
        ]
        for idx, area in enumerate(FLUSH_BTN_AREAS):
            if area[0] <= x <= area[2] and area[1] <= y <= area[3]:
                selected_node = WC_NODES[idx]
                print(f"🖐️ Touch FLUSH button for {selected_node['name']} at ({x},{y})")
                send_flush_command(selected_node)
                time.sleep(0.5)  # Debounce touch
                break

def main_loop():
    """Main application loop"""
    global last_heartbeat
    print("🚀 Starting main loop...")
    update_main_screen()
    loop_count = 0
    while True:
        try:
            # Check for MQTT messages
            if remote_control and remote_control.is_connected():
                remote_control.check_messages()
            # Handle touch FLUSH
            check_touch_flush()
            # Send heartbeat every 30 seconds
            if remote_control and remote_control.should_send_heartbeat():
                selected_node_id = WC_NODES[current_selection]["id"] if WC_NODES else None
                remote_control.send_heartbeat(selected_node_id)
                last_heartbeat = time.time()
            
            # Throttle loop speed
            time.sleep(0.1)
            loop_count += 1
            
            # Update display every 5 loops (khoảng 0.5 giây)
            if loop_count >= 5:
                update_main_screen()
                loop_count = 0
        
        except Exception as e:
            print(f"❌ Main loop error: {e}")
            time.sleep(1)

# === Application Entry Point ===

# Show startup screen
show_startup_screen()

# Connect to WiFi
wifi_result, ip_address = connect_wifi()

# Connect to MQTT broker
mqtt_result = connect_mqtt()

# Start main loop
main_loop()