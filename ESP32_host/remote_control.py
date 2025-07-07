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

# === Hardware Initialization ===
from machine import Pin, SPI, Timer

# Initialize buttons
btn_up = Pin(BTN_UP, Pin.IN, Pin.PULL_UP)
btn_down = Pin(BTN_DOWN, Pin.IN, Pin.PULL_UP)
btn_left = Pin(BTN_LEFT, Pin.IN, Pin.PULL_UP)
btn_right = Pin(BTN_RIGHT, Pin.IN, Pin.PULL_UP)
btn_select = Pin(BTN_SELECT, Pin.IN, Pin.PULL_UP)

# Initialize status LED
status_led = Pin(STATUS_LED, Pin.OUT)
status_led.off()

# Initialize backlight
backlight = Pin(BL_PIN, Pin.OUT)
backlight.on()  # Turn on backlight

print("✅ Hardware initialized")

# === Global Variables ===
wifi_connected = False
mqtt_connected = False
mqtt_client = None
selected_node = 0  # Currently selected node (0-3)
nodes_status = ["offline", "offline", "offline", "offline"]
node_names = ["Room1 (M)", "Room2 (M)", "Room1 (F)", "Room2 (F)"]
node_ids = ["wc_male_01", "wc_male_02", "wc_female_01", "wc_female_02"]

# Button state tracking
last_button_time = 0
BUTTON_DEBOUNCE = 200  # ms

# === Display Functions (Simplified for now) ===
def init_display():
    """Initialize ST7789P3 display"""
    # TODO: Initialize ST7789P3 display driver
    # For now, we'll use LED indicators
    print("📺 Display initialized (LED simulation)")

def update_display():
    """Update display with current UI state"""
    # TODO: Draw UI on ST7789P3 display
    # For now, print to console
    print("┌─────────────────────┐")
    print("│   WC Remote Control │")
    print("├─────────────────────┤")
    for i, (name, status) in enumerate(zip(node_names, nodes_status)):
        indicator = "►" if i == selected_node else " "
        status_icon = "🟢" if status == "online" else "🔴"
        print(f"│{indicator} {name:<10} {status_icon} │")
    print("└─────────────────────┘")
    print(f"WiFi: {'🟢' if wifi_connected else '🔴'} | MQTT: {'🟢' if mqtt_connected else '🔴'}")
    print()

# === Network Functions ===
def connect_wifi():
    """Connect to available WiFi networks"""
    global wifi_connected
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # Scan for available networks
    print("📡 Scanning for WiFi networks...")
    networks = [n[0].decode() for n in wlan.scan()]
    
    for ssid, password in WIFI_NETWORKS:
        if ssid in networks:
            print(f"📶 Connecting to {ssid}...")
            wlan.connect(ssid, password)
            
            # Wait for connection
            for i in range(20):
                if wlan.isconnected():
                    wifi_connected = True
                    ip = wlan.ifconfig()[0]
                    print(f"✅ Connected to {ssid}! IP: {ip}")
                    return True
                time.sleep(0.5)
                print(".", end="")
            print()
    
    wifi_connected = False
    print("❌ Failed to connect to any WiFi network")
    return False

def connect_mqtt():
    """Connect to MQTT broker"""
    global mqtt_connected, mqtt_client
    
    try:
        print(f"📡 Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT}...")
        mqtt_client = MQTTClient(CLIENT_ID, MQTT_BROKER, MQTT_PORT)
        mqtt_client.set_callback(mqtt_callback)
        mqtt_client.connect()
        
        # Subscribe to node status updates
        for node_id in node_ids:
            topic = f"wc/{node_id}/status"
            mqtt_client.subscribe(topic)
            print(f"📥 Subscribed to {topic}")
        
        mqtt_connected = True
        print("✅ Connected to MQTT broker!")
        
        # Send remote control online status
        status_data = {
            "device": "remote_control",
            "status": "online",
            "client_id": CLIENT_ID,
            "timestamp": time.time()
        }
        mqtt_client.publish("wc/remote/status", json.dumps(status_data))
        
        return True
        
    except Exception as e:
        mqtt_connected = False
        print(f"❌ MQTT connection failed: {e}")
        return False

def mqtt_callback(topic, message):
    """Handle incoming MQTT messages"""
    global nodes_status
    
    try:
        topic_str = topic.decode()
        msg_str = message.decode()
        print(f"📨 MQTT: {topic_str} = {msg_str}")
        
        # Parse JSON message
        data = json.loads(msg_str)
        
        # Update node status
        for i, node_id in enumerate(node_ids):
            if f"wc/{node_id}/status" == topic_str:
                nodes_status[i] = data.get("status", "offline")
                print(f"📊 Updated {node_id}: {nodes_status[i]}")
                break
                
    except Exception as e:
        print(f"❌ Error processing MQTT message: {e}")

# === Button Handling ===
def check_buttons():
    """Check button presses and handle UI navigation"""
    global selected_node, last_button_time
    
    current_time = time.ticks_ms()
    if current_time - last_button_time < BUTTON_DEBOUNCE:
        return
    
    # Check each button
    if not btn_up.value():  # Button pressed (active low)
        selected_node = (selected_node - 1) % len(node_names)
        last_button_time = current_time
        print(f"⬆️ Selected: {node_names[selected_node]}")
        update_display()
        
    elif not btn_down.value():
        selected_node = (selected_node + 1) % len(node_names)
        last_button_time = current_time
        print(f"⬇️ Selected: {node_names[selected_node]}")
        update_display()
        
    elif not btn_select.value():
        send_flush_command()
        last_button_time = current_time

def send_flush_command():
    """Send flush command to selected node"""
    if not mqtt_connected:
        print("❌ MQTT not connected!")
        return
    
    node_id = node_ids[selected_node]
    node_name = node_names[selected_node]
    
    if nodes_status[selected_node] != "online":
        print(f"❌ {node_name} is offline!")
        # Flash LED to indicate error
        for _ in range(3):
            status_led.on()
            time.sleep(0.1)
            status_led.off()
            time.sleep(0.1)
        return
    
    # Send flush command
    command_data = {
        "action": "flush",
        "timestamp": time.time(),
        "source": "remote_control"
    }
    
    topic = f"wc/{node_id}/command"
    payload = json.dumps(command_data)
    
    try:
        mqtt_client.publish(topic, payload)
        print(f"🚽 Sent flush command to {node_name}")
        
        # Flash LED to indicate success
        for _ in range(2):
            status_led.on()
            time.sleep(0.2)
            status_led.off()
            time.sleep(0.2)
            
    except Exception as e:
        print(f"❌ Failed to send command: {e}")

# === Main Application ===
def main():
    """Main application loop"""
    global wifi_connected, mqtt_connected
    
    print("🚀 Starting WC Remote Control...")
    
    # Initialize display
    init_display()
    
    # Connect to WiFi
    if not connect_wifi():
        print("❌ Cannot start without WiFi connection")
        return
    
    # Connect to MQTT
    if not connect_mqtt():
        print("⚠️ Starting without MQTT connection")
    
    # Initial display update
    update_display()
    
    print("🎮 Remote control ready!")
    print("🔄 Use UP/DOWN buttons to select node, SELECT to flush")
    
    # Main loop
    last_status_time = 0
    loop_count = 0
    
    while True:
        try:
            # Check for MQTT messages
            if mqtt_client and mqtt_connected:
                mqtt_client.check_msg()
            
            # Check button presses
            check_buttons()
            
            # Periodic status updates (every 30 seconds)
            current_time = time.time()
            if current_time - last_status_time > 30:
                if mqtt_connected:
                    # Request status from all nodes
                    for node_id in node_ids:
                        status_request = {"action": "status", "timestamp": current_time}
                        mqtt_client.publish(f"wc/{node_id}/command", json.dumps(status_request))
                
                last_status_time = current_time
                print("📊 Requested status updates")
            
            # Refresh display every 5 seconds
            loop_count += 1
            if loop_count % 50 == 0:  # 100ms * 50 = 5 seconds
                update_display()
            
            # Connection status LED
            if wifi_connected and mqtt_connected:
                status_led.on()
            else:
                # Blink if not fully connected
                status_led.value(not status_led.value())
            
            time.sleep_ms(100)
            
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            time.sleep(1)
            
            # Try to reconnect
            if not wifi_connected:
                print("🔄 Attempting WiFi reconnect...")
                connect_wifi()
            elif wifi_connected and not mqtt_connected:
                print("🔄 Attempting MQTT reconnect...")
                connect_mqtt()

# === Entry Point ===
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Remote control stopped by user")
    except Exception as e:
        print(f"💥 Critical error: {e}")
    finally:
        # Cleanup
        if mqtt_client:
            try:
                mqtt_client.disconnect()
            except:
                pass
        print("🔌 Disconnected")
