import network
import time
from machine import Pin, Timer
from umqtt.simple import MQTTClient
import json

# === Cấu hình Node ===
NODE_ID = 'wc2'
NODE_TYPE = 'wc'
ROOM_NAME = 'WC 2'
MQTT_BROKER = '192.168.100.121'
MQTT_PORT = 1883

# === GPIO Setup ===
status_led = Pin(2, Pin.OUT)
relay = Pin(5, Pin.OUT)
status_led.value(1)  # OFF (inverted)
relay.value(0)       # OFF

# === Global variables ===
mqtt_client = None
relay_timer = None
blink_timer = None
blink_count = 0
wifi_connected = False
mqtt_connected = False

# === WiFi ===
def connect_wifi():
    global wifi_connected
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    networks = [n[0].decode() for n in wlan.scan()]
    if "Michelle" in networks:
        wlan.connect('Michelle', '0908800130')
    elif "Floor 9" in networks:
        wlan.connect('Floor 9', 'Veg@s123')
    elif "Vinternal" in networks:
        wlan.connect('Floor 9', 'abcd1234')  # Example for internal network  
    else:
        print(f"[{NODE_ID}] No known WiFi networks found")
        wifi_connected = False
        return False
    for _ in range(20):
        if wlan.isconnected():
            print('WiFi OK:', wlan.ifconfig()[0])
            wifi_connected = True
            return True
        time.sleep(0.5)
    wifi_connected = False
    print(f"[{NODE_ID}] WiFi connection failed")
    return False

# === MQTT ===
def on_mqtt_message(topic, message):
    global relay_timer, blink_count
    try:
        if isinstance(message, bytes):
            msg_str = message.decode().strip()
        else:
            msg_str = str(message).strip()
        print(f"[{NODE_ID}] 📨 MQTT Message Received!")
        print(f"[{NODE_ID}]    Topic: {topic.decode()}")
        print(f"[{NODE_ID}]    Message: {msg_str}")
        try:
            cmd_data = json.loads(msg_str)
            action = cmd_data.get('action', msg_str)
            print(f"[{NODE_ID}]    Parsed Action: {action}")
        except:
            action = msg_str
            print(f"[{NODE_ID}]    Using plain string action: {action}")
        if action in ['flush', 'on', 'activate']:
            print(f"[{NODE_ID}] 🚽 FLUSH COMMAND RECEIVED!")
            execute_flush()
        elif action in ['status', 'ping']:
            print(f"[{NODE_ID}] 📊 STATUS REQUEST RECEIVED!")
            publish_status()
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
    relay.value(1)
    print(f"[{NODE_ID}] ✅ Relay activated: {relay.value()}")
    print(f"[{NODE_ID}] 💡 Starting LED blink sequence for 4 seconds...")
    blink_led_4_seconds()

def blink_led_4_seconds():
    print(f"[{NODE_ID}] 💡 Starting 4-second LED blink sequence...")
    for i in range(20):
        status_led.value(0)
        print(f"[{NODE_ID}] 💡 LED ON - blink {i+1}/20")
        time.sleep_ms(100)
        status_led.value(1)
        print(f"[{NODE_ID}] 💡 LED OFF - blink {i+1}/20")
        time.sleep_ms(100)
    status_led.value(1)
    print(f"[{NODE_ID}] ✅ LED blinking completed - 4 seconds finished")
    global relay_timer
    if relay_timer:
        relay_timer.deinit()
    relay_timer = Timer(0)
    relay_timer.init(period=5000, mode=Timer.ONE_SHOT, callback=stop_relay)
    print(f"[{NODE_ID}] ⏰ 5-second auto-off timer started")
    publish_response("flush", True, "Flush executed successfully - LED blinking for 4 seconds")
    print(f"[{NODE_ID}] 🎉 FLUSH COMMAND COMPLETED!")

def stop_relay(timer_obj=None):
    global relay_timer
    relay.value(0)
    if relay_timer:
        relay_timer.deinit()
        relay_timer = None
    print(f"[{NODE_ID}] Relay stopped")
    publish_response("stop", True, "Relay deactivated")

def connect_mqtt():
    global mqtt_client, mqtt_connected
    try:
        client_id = f"{NODE_ID}_{time.ticks_ms()}"
        mqtt_client = MQTTClient(client_id, MQTT_BROKER, port=MQTT_PORT)
        mqtt_client.set_callback(on_mqtt_message)
        mqtt_client.connect()
        command_topic = f"wc/{NODE_ID}/command"
        mqtt_client.subscribe(command_topic)
        mqtt_connected = True
        print(f"[{NODE_ID}] MQTT connected and subscribed to {command_topic}")
        publish_status()
        return True
    except Exception as e:
        mqtt_connected = False
        print(f"[{NODE_ID}] MQTT connection failed: {e}")
        return False

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
                "free_memory": str(time.ticks_ms())
            }
            topic = f"wc/{NODE_ID}/status"
            message = json.dumps(status_data)
            mqtt_client.publish(topic, message)
            print(f"[{NODE_ID}] Status published")
        except Exception as e:
            print(f"[{NODE_ID}] Failed to publish status: {e}")

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

def main():
    global mqtt_client
    print(f"[{NODE_ID}] Starting {ROOM_NAME} ({NODE_TYPE}) node...")
    print(f"[{NODE_ID}] Testing LED...")
    for i in range(3):
        status_led.value(0)
        time.sleep_ms(300)
        status_led.value(1)
        time.sleep_ms(300)
    print(f"[{NODE_ID}] LED test complete")
    if not connect_wifi():
        print(f"[{NODE_ID}] Failed to connect to WiFi. Retrying in 10 seconds...")
        time.sleep(10)
        return
    if not connect_mqtt():
        print(f"[{NODE_ID}] Failed to connect to MQTT. Retrying in 10 seconds...")
        time.sleep(10)
        return
    print(f"[{NODE_ID}] 🎉 {ROOM_NAME} ESP32 Node is ready!")
    print(f"[{NODE_ID}] 💡 LED will blink for 4 seconds when flush command is received")
    print(f"[{NODE_ID}] 📡 Status will be published every 10 seconds")
    last_status_time = 0
    loop_count = 0
    while True:
        try:
            if mqtt_client:
                mqtt_client.check_msg()
            current_time = time.time()
            if current_time - last_status_time > 10:
                print(f"[{NODE_ID}] 📊 Publishing status update #{int(current_time/10)}")
                publish_status()
                last_status_time = current_time
            time.sleep_ms(100)
            loop_count += 1
            if loop_count % 50 == 0:
                wifi_status = "connected" if wifi_connected else "disconnected"
                mqtt_status = "connected" if mqtt_connected else "disconnected"
                print(f"[{NODE_ID}] 🔄 Status: WiFi={wifi_status}, MQTT={mqtt_status}, Relay={relay.value()}")
        except Exception as e:
            print(f"[{NODE_ID}] ❌ Error in main loop: {e}")
            time.sleep(1)
            if not wifi_connected:
                print(f"[{NODE_ID}] 🔄 Attempting WiFi reconnect...")
                connect_wifi()
            if wifi_connected and not mqtt_connected:
                print(f"[{NODE_ID}] 🔄 Attempting MQTT reconnect...")
                connect_mqtt()

if __name__ == "__main__":
    main()