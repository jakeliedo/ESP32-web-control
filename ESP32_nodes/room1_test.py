import network
import time
from machine import Pin, Timer
from umqtt.simple import MQTTClient
import json
import ubinascii
import machine

# === Room1 ESP32 Node Configuration ===
NODE_ID = 'wc_male_01'  # This matches the mock data in PC_host/app.py
NODE_TYPE = 'male'
ROOM_NAME = 'Room1'

# Network Configuration
MQTT_BROKER = '192.168.100.72'  # Your PC's IP address
MQTT_PORT = 1883
WIFI_SSID = 'Michelle'  # Your WiFi network
WIFI_PASS = '0908800130'  # Your WiFi password

# Alternative WiFi networks
WIFI_NETWORKS = [
    {'ssid': 'Michelle', 'password': '0908800130'},
    {'ssid': 'Vinternal', 'password': 'Veg@s123'}
]

# === GPIO Setup ===
# Built-in LED on ESP32 (GPIO 2) - will blink when flush command received
led = Pin(2, Pin.OUT)
led.value(1)  # Turn OFF (LED is inverted on ESP32)

# Optional: External LED or relay for actual control
# relay = Pin(5, Pin.OUT)
# relay.value(0)  # OFF

# === Global Variables ===
mqtt_client = None
blink_timer = None
blink_count = 0
wifi_connected = False
mqtt_connected = False

print(f"[{NODE_ID}] Starting Room1 ESP32 Node...")
print(f"[{NODE_ID}] Device ID: {ubinascii.hexlify(machine.unique_id()).decode()}")

# === WiFi Connection ===
def connect_wifi():
    global wifi_connected
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    print(f"[{NODE_ID}] Scanning for WiFi networks...")
    available_networks = [n[0].decode() for n in wlan.scan()]
    print(f"[{NODE_ID}] Found networks: {available_networks}")
    
    # Try each configured network
    for network_config in WIFI_NETWORKS:
        ssid = network_config['ssid']
        password = network_config['password']
        
        if ssid in available_networks:
            print(f"[{NODE_ID}] Connecting to {ssid}...")
            wlan.connect(ssid, password)
            
            # Wait for connection
            for i in range(20):
                if wlan.isconnected():
                    wifi_connected = True
                    ip = wlan.ifconfig()[0]
                    print(f"[{NODE_ID}] ✅ WiFi connected to {ssid}!")
                    print(f"[{NODE_ID}] IP address: {ip}")
                    return True
                    
                print(f"[{NODE_ID}] Connecting... ({i+1}/20)")
                time.sleep(0.5)
            
            print(f"[{NODE_ID}] Failed to connect to {ssid}")
            
    wifi_connected = False
    print(f"[{NODE_ID}] ❌ WiFi connection failed - no available networks")
    return False

# === MQTT Message Handler ===
def on_mqtt_message(topic, message):
    global blink_count
    
    try:
        topic_str = topic.decode()
        
        if isinstance(message, bytes):
            msg_str = message.decode().strip()
        else:
            msg_str = str(message).strip()
            
        print(f"[{NODE_ID}] 📨 Received: {topic_str} -> {msg_str}")
        
        # Parse command
        try:
            # Try JSON first
            cmd_data = json.loads(msg_str)
            action = cmd_data.get('action', msg_str)
        except:
            # Fallback to plain text
            action = msg_str.lower()
        
        # Handle flush command
        if action in ['flush', 'on', 'activate']:
            print(f"[{NODE_ID}] 🚽 FLUSH command received for Room1!")
            execute_flush()
            
        # Handle other commands
        elif action in ['status', 'ping']:
            publish_status()
            
        elif action in ['off', 'stop']:
            stop_all()
            
        else:
            print(f"[{NODE_ID}] Unknown command: {action}")
            
    except Exception as e:
        print(f"[{NODE_ID}] ❌ Error processing message: {e}")
        print(f"[{NODE_ID}] Topic: {topic}")
        print(f"[{NODE_ID}] Message: {message}")

# === Execute Flush Action ===
def execute_flush():
    global blink_count
    
    print(f"[{NODE_ID}] 🔄 Executing flush for Room1...")
    
    # Start LED blinking (25 blinks = 5 seconds at 200ms intervals)
    blink_count = 25
    start_led_blink()
    
    # Optional: Activate relay for real hardware control
    # relay.value(1)
    
    # Send response back to PC
    publish_response("flush", True, "Room1 flush activated - LED blinking!")
    
    # Auto-stop after 5 seconds
    Timer(-1).init(period=5000, mode=Timer.ONE_SHOT, callback=stop_all)

# === LED Blinking Function ===
def start_led_blink():
    global blink_count, blink_timer
    
    if blink_count > 0:
        # Toggle LED (remember it's inverted)
        led.value(not led.value())
        blink_count -= 1
        
        # Schedule next blink
        if blink_timer:
            blink_timer.deinit()
        blink_timer = Timer(-1)
        blink_timer.init(period=200, mode=Timer.ONE_SHOT, callback=lambda t: start_led_blink())
        
        # Show progress
        if blink_count % 5 == 0:
            print(f"[{NODE_ID}] 💡 LED blinking... {blink_count} blinks remaining")
    else:
        # Stop blinking
        led.value(1)  # Turn OFF (inverted)
        print(f"[{NODE_ID}] ✅ LED blinking completed")

# === Stop All Operations ===
def stop_all(timer_obj=None):
    global blink_count
    
    print(f"[{NODE_ID}] ⏹️ Stopping all operations...")
    
    # Stop LED blinking
    blink_count = 0
    led.value(1)  # Turn OFF (inverted)
    
    # Stop relay (if used)
    # relay.value(0)
    
    # Clean up timers
    if blink_timer:
        blink_timer.deinit()
    
    # Send status update
    publish_response("stop", True, "Room1 operations stopped")

# === MQTT Connection ===
def connect_mqtt():
    global mqtt_client, mqtt_connected
    
    try:
        # Create unique client ID
        client_id = f"{NODE_ID}_{ubinascii.hexlify(machine.unique_id()).decode()[:8]}"
        print(f"[{NODE_ID}] MQTT Client ID: {client_id}")
        
        # Create MQTT client
        mqtt_client = MQTTClient(client_id, MQTT_BROKER, port=MQTT_PORT)
        mqtt_client.set_callback(on_mqtt_message)
        
        # Connect to broker
        print(f"[{NODE_ID}] Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
        mqtt_client.connect()
        
        # Subscribe to command topic
        command_topic = f"wc/{NODE_ID}/command"
        mqtt_client.subscribe(command_topic)
        
        mqtt_connected = True
        print(f"[{NODE_ID}] ✅ MQTT connected!")
        print(f"[{NODE_ID}] 📡 Subscribed to: {command_topic}")
        
        # Announce that we're online
        publish_status()
        
        return True
        
    except Exception as e:
        mqtt_connected = False
        print(f"[{NODE_ID}] ❌ MQTT connection failed: {e}")
        return False

# === Publish Status ===
def publish_status():
    if mqtt_client and mqtt_connected:
        try:
            status_data = {
                "node_id": NODE_ID,
                "node_type": NODE_TYPE,
                "name": ROOM_NAME,
                "status": "online",
                "wifi_connected": wifi_connected,
                "timestamp": time.time(),
                "device_id": ubinascii.hexlify(machine.unique_id()).decode(),
                "location": "Floor 1"
            }
            
            topic = f"wc/{NODE_ID}/status"
            message = json.dumps(status_data)
            mqtt_client.publish(topic, message)
            print(f"[{NODE_ID}] 📤 Status published")
            
        except Exception as e:
            print(f"[{NODE_ID}] ❌ Failed to publish status: {e}")

# === Publish Response ===
def publish_response(action, success, message=""):
    if mqtt_client and mqtt_connected:
        try:
            response_data = {
                "node_id": NODE_ID,
                "room_name": ROOM_NAME,
                "action": action,
                "success": success,
                "message": message,
                "timestamp": time.time()
            }
            
            topic = f"wc/{NODE_ID}/response"
            response_msg = json.dumps(response_data)
            mqtt_client.publish(topic, response_msg)
            print(f"[{NODE_ID}] 📤 Response sent: {action} - {'SUCCESS' if success else 'FAILED'}")
            
        except Exception as e:
            print(f"[{NODE_ID}] ❌ Failed to publish response: {e}")

# === Main Function ===
def main():
    global mqtt_client
    
    print(f"[{NODE_ID}] 🚀 Initializing Room1 ESP32 Node...")
    
    # Test LED
    print(f"[{NODE_ID}] Testing LED...")
    for i in range(3):
        led.value(0)  # ON
        time.sleep(0.2)
        led.value(1)  # OFF
        time.sleep(0.2)
    print(f"[{NODE_ID}] LED test complete")
    
    # Connect to WiFi
    if not connect_wifi():
        print(f"[{NODE_ID}] ⚠️ WiFi connection failed. Retrying in 10 seconds...")
        time.sleep(10)
        return
    
    # Connect to MQTT
    if not connect_mqtt():
        print(f"[{NODE_ID}] ⚠️ MQTT connection failed. Retrying in 10 seconds...")
        time.sleep(10)
        return
    
    print(f"[{NODE_ID}] 🎉 Room1 ESP32 Node is ready!")
    print(f"[{NODE_ID}] 💡 LED will blink when flush command is received")
    print(f"[{NODE_ID}] 🌐 Send commands to: wc/{NODE_ID}/command")
    
    # Main loop
    last_heartbeat = 0
    loop_count = 0
    
    while True:
        try:
            # Check for MQTT messages
            if mqtt_client and mqtt_connected:
                mqtt_client.check_msg()
            
            # Send periodic heartbeat (every 30 seconds)
            current_time = time.time()
            if current_time - last_heartbeat > 30:
                publish_status()
                last_heartbeat = current_time
                print(f"[{NODE_ID}] 💓 Heartbeat sent (loop: {loop_count})")
            
            # Short delay
            time.sleep_ms(100)
            loop_count += 1
            
        except Exception as e:
            print(f"[{NODE_ID}] ❌ Error in main loop: {e}")
            time.sleep(1)
            
            # Try to reconnect if needed
            if not wifi_connected:
                print(f"[{NODE_ID}] Attempting WiFi reconnection...")
                connect_wifi()
                
            if wifi_connected and not mqtt_connected:
                print(f"[{NODE_ID}] Attempting MQTT reconnection...")
                connect_mqtt()

# === Startup ===
if __name__ == "__main__":
    print("=" * 50)
    print("ESP32 WC Control System - Room1 Node")
    print("COM10 - ESP32 Development Board")
    print("=" * 50)
    
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print(f"\n[{NODE_ID}] 🛑 Stopped by user")
            break
        except Exception as e:
            print(f"[{NODE_ID}] 💥 Critical error: {e}")
            print(f"[{NODE_ID}] Restarting in 5 seconds...")
            time.sleep(5)
