import network
import time
from machine import Pin, Timer
from umqtt.simple import MQTTClient
import json

# === Cấu hình Node ===
NODE_ID = 'wc1'
MQTT_BROKER = '192.168.100.121'
MQTT_PORT = 1883

# === GPIO Setup ===
# Status LED (built-in on most ESP32 boards)
status_led = Pin(2, Pin.OUT)
# Relay for controlling actuator (water valve, pump, etc.)
relay = Pin(5, Pin.OUT)
# Optional: Status indicator LED
indicator_led = Pin(18, Pin.OUT)
# Initialize pins
status_led.value(1)  # OFF (inverted on ESP32)
relay.value(0)       # OFF
indicator_led.value(0)  # OFF

# === Global variables ===
mqtt_client = None
relay_timer = None
blink_timer = None
blink_count = 0
wifi_connected = False
mqtt_connected = False

# === WiFi ===
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # Scan for available networks and connect
    networks = [n[0].decode() for n in wlan.scan()]   
    if "Michelle" in [n[0].decode() for n in wlan.scan()]:
        wlan.connect('Michelle', '0908800130')
    elif "Floor 9" in [n[0].decode() for n in wlan.scan()]:
        wlan.connect('Floor 9', 'Veg@s123')
    else:
        print(f"[{NODE_ID}] No known WiFi networks found")
        return False
    
    for _ in range(20):
        if wlan.isconnected():
            print('WiFi OK:', wlan.ifconfig()[0])
            return True
        time.sleep(0.5)
    wifi_connected = False
    print(f"[{NODE_ID}] WiFi connection failed")
    return False

# === MQTT ===
def on_mqtt_message(topic, message):
    global relay_timer, blink_count
    try:
        # Parse command
        if isinstance(message, bytes):
            msg_str = message.decode().strip()
        else:
            msg_str = str(message).strip()
            
        print(f"[{NODE_ID}] 📨 MQTT Message Received!")
        print(f"[{NODE_ID}]    Topic: {topic.decode()}")
        print(f"[{NODE_ID}]    Message: {msg_str}")
        
        # Try to parse as JSON first
        try:
            cmd_data = json.loads(msg_str)
            action = cmd_data.get('action', msg_str)
            print(f"[{NODE_ID}]    Parsed Action: {action}")
        except:
            # Fallback to plain string
            action = msg_str
            print(f"[{NODE_ID}]    Using plain string action: {action}")
        
        # Handle flush command
        if action in ['flush', 'on', 'activate']:
            print(f"[{NODE_ID}] 🚽 FLUSH COMMAND RECEIVED!")
            execute_flush()
            
        # Handle status request
        elif action in ['status', 'ping']:
            print(f"[{NODE_ID}] 📊 STATUS REQUEST RECEIVED!")
            publish_status()
            
        # Handle off command
        elif action in ['off', 'stop']:
            print(f"[{NODE_ID}] 🛑 STOP COMMAND RECEIVED!")
            stop_relay()
        else:
            print(f"[{NODE_ID}] ❓ Unknown action: {action}")
            
    except Exception as e:
        print(f"[{NODE_ID}] ❌ Error processing message: {e}")

# === Execute Flush Action ===
def execute_flush():
    global relay_timer, blink_count
    
    print(f"[{NODE_ID}] 🚽 FLUSH COMMAND PROCESSING STARTED!")
    print(f"[{NODE_ID}] 🔧 Activating hardware...")
    
    # Activate relay (water valve, pump, etc.)
    relay.value(1)
    indicator_led.value(1)
    print(f"[{NODE_ID}] ✅ Relay activated: {relay.value()}")
    print(f"[{NODE_ID}] ✅ Indicator LED activated: {indicator_led.value()}")
    
    # Blink LED for exactly 4 seconds using direct timing
    print(f"[{NODE_ID}] 💡 Starting LED blink sequence for 4 seconds...")
    blink_led_4_seconds()

# === LED Blinking for 4 seconds ===
def blink_led_4_seconds():
    """Blink LED for exactly 4 seconds (20 blinks at 200ms each)"""
    print(f"[{NODE_ID}] 💡 Starting 4-second LED blink sequence...")
    
    # Blink 20 times with 200ms on/off = 4 seconds total
    for i in range(20):
        # Turn LED ON (0 = ON for ESP32 built-in LED)
        status_led.value(0)
        print(f"[{NODE_ID}] 💡 LED ON - blink {i+1}/20")
        time.sleep_ms(100)  # ON for 100ms
        
        # Turn LED OFF (1 = OFF for ESP32 built-in LED) 
        status_led.value(1)
        print(f"[{NODE_ID}] 💡 LED OFF - blink {i+1}/20")
        time.sleep_ms(100)  # OFF for 100ms
        
        # Total: 100ms ON + 100ms OFF = 200ms per blink
        # 20 blinks × 200ms = 4000ms = 4 seconds
    
    # Ensure LED is OFF at the end
    status_led.value(1)
    print(f"[{NODE_ID}] ✅ LED blinking completed - 4 seconds finished")
    
    # Set auto-off timer (5 seconds)
    if relay_timer:
        relay_timer.deinit()
    relay_timer = Timer(0)  # Use timer 0 instead of -1
    relay_timer.init(period=5000, mode=Timer.ONE_SHOT, callback=stop_relay)
    print(f"[{NODE_ID}] ⏰ 5-second auto-off timer started")
    
    # Send confirmation back to server
    publish_response("flush", True, "Flush executed successfully - LED blinking for 4 seconds")
    
    print(f"[{NODE_ID}] 🎉 FLUSH COMMAND COMPLETED!")

# === Stop Relay ===
def stop_relay(timer_obj=None):
    relay.value(0)
    indicator_led.value(0)
    if relay_timer:
        relay_timer.deinit()
        relay_timer = None
    print(f"[{NODE_ID}] Relay stopped")
    
    # Send status update
    publish_response("stop", True, "Relay deactivated")

# === MQTT Connection ===
def connect_mqtt():
    global mqtt_client, mqtt_connected
    try:
        # Create unique client ID
        client_id = f"{NODE_ID}_{time.ticks_ms()}"
        mqtt_client = MQTTClient(client_id, MQTT_BROKER, port=MQTT_PORT)
        mqtt_client.set_callback(on_mqtt_message)
        
        # Connect to broker
        mqtt_client.connect()
        
        # Subscribe to command topic
        command_topic = f"wc/{NODE_ID}/command"
        mqtt_client.subscribe(command_topic)
        
        mqtt_connected = True
        print(f"[{NODE_ID}] MQTT connected and subscribed to {command_topic}")
        
        # Announce online status
        publish_status()
        
        return True
        
    except Exception as e:
        mqtt_connected = False
        print(f"[{NODE_ID}] MQTT connection failed: {e}")
        return False
    
# === Publish Status ===
def publish_status():
    if mqtt_client and mqtt_connected:
        try:
            status_data = {
                "node_id": NODE_ID,
                "node_type": NODE_TYPE,
                "room_name": ROOM_NAME,
                "status": "online",
                "wifi_connected": wifi_connected,
                "relay_active": relay.value(),
                "timestamp": time.time(),
                "free_memory": str(time.ticks_ms())  # Simple way to show activity
            }
            
            topic = f"wc/{NODE_ID}/status"
            message = json.dumps(status_data)
            mqtt_client.publish(topic, message)
            print(f"[{NODE_ID}] Status published")
            
        except Exception as e:
            print(f"[{NODE_ID}] Failed to publish status: {e}")
            
# === Publish Response ===

def publish_response(action, success, message=""):
    if mqtt_client and mqtt_connected:
        try:
            response_data = {
                "node_id": NODE_ID,
                "action": action,
                "success": success,
                "message": message,
                "timestamp": time.time()
            }
            
            topic = f"wc/{NODE_ID}/response"
            response_msg = json.dumps(response_data)
            mqtt_client.publish(topic, response_msg)
            
        except Exception as e:
            print(f"[{NODE_ID}] Failed to publish response: {e}")

# === Main Loop ===
def main():
    global mqtt_client
    
    print(f"[{NODE_ID}] Starting {ROOM_NAME} ({NODE_TYPE}) node...")
    
    # Test LED on startup
    print(f"[{NODE_ID}] Testing LED...")
    for i in range(3):
        status_led.value(0)  # ON (inverted)
        time.sleep_ms(300)
        status_led.value(1)  # OFF (inverted)
        time.sleep_ms(300)
    print(f"[{NODE_ID}] LED test complete")
    
    # Connect to WiFi
    if not connect_wifi():
        print(f"[{NODE_ID}] Failed to connect to WiFi. Retrying in 10 seconds...")
        time.sleep(10)
        return
    
    # Connect to MQTT
    if not connect_mqtt():
        print(f"[{NODE_ID}] Failed to connect to MQTT. Retrying in 10 seconds...")
        time.sleep(10)
        return
    
    print(f"[{NODE_ID}] 🎉 {ROOM_NAME} ESP32 Node is ready!")
    print(f"[{NODE_ID}] 💡 LED will blink for 4 seconds when flush command is received")
    print(f"[{NODE_ID}] 📡 Status will be published every 10 seconds")
    
    # Main loop
    last_status_time = 0
    loop_count = 0
    while True:
        try:
            # Check for MQTT messages every 100ms for responsiveness
            if mqtt_client:
                mqtt_client.check_msg()
            
            # Send periodic status updates (every 10 seconds instead of 30)
            current_time = time.time()
            if current_time - last_status_time > 10:
                print(f"[{NODE_ID}] 📊 Publishing status update #{int(current_time/10)}")
                publish_status()
                last_status_time = current_time
            
            # Short sleep for responsiveness
            time.sleep_ms(100)
            
            # Debug info every 50 loops (5 seconds)
            loop_count += 1
            if loop_count % 50 == 0:
                wifi_status = "connected" if wifi_connected else "disconnected"
                mqtt_status = "connected" if mqtt_connected else "disconnected"
                print(f"[{NODE_ID}] 🔄 Status: WiFi={wifi_status}, MQTT={mqtt_status}, Relay={relay.value()}")
            
        except Exception as e:
            print(f"[{NODE_ID}] ❌ Error in main loop: {e}")
            time.sleep(1)
            
            # Try to reconnect if connection lost
            if not wifi_connected:
                print(f"[{NODE_ID}] 🔄 Attempting WiFi reconnect...")
                connect_wifi()
            if wifi_connected and not mqtt_connected:
                print(f"[{NODE_ID}] 🔄 Attempting MQTT reconnect...")
                connect_mqtt()
if __name__ == "__main__":
    main()