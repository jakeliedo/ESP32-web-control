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

# === Hardware Configuration ===
# ST7789P3 3.2" Display connections
SPI_SCLK = 18   # Serial Clock
SPI_MOSI = 23   # Master Out Slave In
SPI_CS = 5      # Chip Select
DC_PIN = 2      # Data/Command
RST_PIN = 4     # Reset
BL_PIN = 15     # Backlight

# Physical buttons
BTN_UP = 32
BTN_DOWN = 33
BTN_LEFT = 25
BTN_RIGHT = 26
BTN_SELECT = 27

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

# Initialize buttons
btn_up = Pin(BTN_UP, Pin.IN, Pin.PULL_UP)
btn_down = Pin(BTN_DOWN, Pin.IN, Pin.PULL_UP)
btn_left = Pin(BTN_LEFT, Pin.IN, Pin.PULL_UP)
btn_right = Pin(BTN_RIGHT, Pin.IN, Pin.PULL_UP)
btn_select = Pin(BTN_SELECT, Pin.IN, Pin.PULL_UP)

# Initialize status LED
status_led = Pin(STATUS_LED, Pin.OUT)
status_led.off()

# Initialize SPI for display
spi = SPI(2, baudrate=40000000, sck=Pin(SPI_SCLK), mosi=Pin(SPI_MOSI))

# Initialize display
display = ST7789P3(spi, SPI_CS, DC_PIN, RST_PIN, BL_PIN)
display.init()
print("📺 Display initialized")

# Initialize UI
ui = SimpleUI(display)
print("🎨 UI initialized")

# Initialize all node status as offline
for node in WC_NODES:
    node_status[node["id"]] = {"status": "offline", "last_seen": 0}

print("✅ Hardware initialized")

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

def handle_button_press():
    """Handle button press events"""
    global current_selection
    
    # Button debouncing
    time.sleep(0.1)
    
    if not btn_up.value():  # UP pressed (active low)
        current_selection = (current_selection - 1) % len(WC_NODES)
        print(f"⬆️  Selection: {WC_NODES[current_selection]['name']}")
        update_main_screen()
        return True
    
    if not btn_down.value():  # DOWN pressed
        current_selection = (current_selection + 1) % len(WC_NODES)
        print(f"⬇️  Selection: {WC_NODES[current_selection]['name']}")
        update_main_screen()
        return True
    
    if not btn_select.value():  # SELECT pressed
        selected_node = WC_NODES[current_selection]
        print(f"✅ Selected: {selected_node['name']}")
        send_flush_command(selected_node)
        return True
    
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

def main_loop():
    """Main application loop"""
    global last_heartbeat
    
    print("🚀 Starting main loop...")
    
    # Show main screen
    update_main_screen()
    
    loop_count = 0
    
    while True:
        try:
            # Check for MQTT messages
            if remote_control and remote_control.is_connected():
                remote_control.check_messages()
            
            # Handle button presses
            if handle_button_press():
                time.sleep(0.3)  # Debounce delay
            
            # Send heartbeat every 30 seconds
            if remote_control and remote_control.should_send_heartbeat():
                selected_node_id = WC_NODES[current_selection]["id"] if WC_NODES else None
                if remote_control.send_heartbeat(selected_node_id):
                    # Update connection status on display
                    update_main_screen()
            
            # Periodic status LED blink
            if loop_count % 100 == 0:
                status_led.on()
                time.sleep(0.05)
                status_led.off()
            
            loop_count += 1
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Main loop error: {e}")
            status_led.on()  # Indicate error
            time.sleep(1)
            status_led.off()
            
            # Try to reconnect if MQTT disconnected
            if remote_control and not remote_control.is_connected():
                print("🔄 Attempting MQTT reconnection...")
                if remote_control.reconnect():
                    print("✅ MQTT reconnected")
                    remote_control.subscribe_to_nodes(WC_NODES)
                else:
                    print("❌ MQTT reconnection failed")

def main():
    """Main application entry point"""
    global last_heartbeat
    
    # Show startup screen
    show_startup_screen()
    time.sleep(2)
    
    # Connect to WiFi
    connected, ip = connect_wifi()
    if not connected:
        ui.show_message("WiFi Failed!", 5000)
        return
    
    time.sleep(1)
    
    # Connect to MQTT
    if not connect_mqtt():
        ui.show_message("MQTT Failed!", 5000)
        return
    
    time.sleep(1)
    
    # Initialize heartbeat timer
    last_heartbeat = time.time()
    
    # Show success message
    ui.show_message("System Ready!", 2000)
    
    # Start main loop
    main_loop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        # Keep LED on to indicate error
        status_led.on()