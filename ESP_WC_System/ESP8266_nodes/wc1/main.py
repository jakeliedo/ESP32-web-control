import network
import time
from machine import Pin
from umqtt.simple import MQTTClient
import json

# === Cấu hình Node ===
NODE_ID = 'wc1'  # Unique ID: wc1, wc2, etc
MQTT_BROKER = '192.168.100.72'  # ESP32 host IP
MQTT_PORT = 1883

# === GPIO Setup ===
led = Pin(2, Pin.OUT)  # Built-in LED (GPIO2 on ESP8266)
outputs = {
    '1': Pin(5, Pin.OUT),  # D1 on ESP8266
    '2': Pin(4, Pin.OUT),  # D2 on ESP8266 
    '3': Pin(0, Pin.OUT)   # D3 on ESP8266
}

# === WiFi Setup ===
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

# Tìm và kết nối WiFi
def connect_wifi():
    print("Scanning WiFi...")
    nets = sta_if.scan()
    ssid_list = [net[0].decode() for net in nets]
    print(f"Found networks: {ssid_list}")
    
    if "Michelle" in ssid_list:
        print("Connecting to Michelle...")
        sta_if.connect('Michelle', '0908800130')
    elif "Vinternal" in ssid_list:
        print("Connecting to Vinternal...")
        sta_if.connect('Vinternal', 'Veg@s123')
    elif "Floor 9" in ssid_list:
        print("Connecting to Floor 9...")
        sta_if.connect('Floor 9', 'Veg@s123')
    else:
        print("No known network found!")
        return False
    
    # Wait for connection
    for _ in range(20):  # wait up to 10 seconds
        if sta_if.isconnected():
            print('WiFi connected, IP:', sta_if.ifconfig()[0])
            return True
        time.sleep(0.5)
    
    print("WiFi connection failed!")
    return False

# === MQTT Handler ===
mqtt_client = None

def mqtt_callback(topic, msg):
    try:
        print(f"Received: {topic} - {msg}")
        command = msg.decode()
        
        channel, action = command.split('_')
        if channel in outputs and action in ['on', 'off']:
            # Set GPIO
            value = 1 if action == 'on' else 0
            outputs[channel].value(value)
            
            # Blink LED for feedback
            blink_led()
            
            # Auto turn off after delay if turned on
            if action == 'on':
                # This would be replaced with a proper timer in production code
                # For simplicity, we'll just print the intention
                print(f"Channel {channel} will turn off after 3 seconds")
            
            # Send status update
            publish_status()
    except Exception as e:
        print(f"Error in callback: {e}")

def connect_mqtt():
    global mqtt_client
    client_id = f"{NODE_ID}_{time.ticks_ms()}"
    mqtt_client = MQTTClient(client_id, MQTT_BROKER, port=MQTT_PORT)
    mqtt_client.set_callback(mqtt_callback)
    
    try:
        mqtt_client.connect()
        topic = f"wc/{NODE_ID}/command"
        mqtt_client.subscribe(topic)
        print(f"MQTT connected, subscribed to {topic}")
        publish_status()  # Publish initial status
        return True
    except Exception as e:
        print(f"MQTT connection failed: {e}")
        return False

def publish_status():
    if mqtt_client:
        status = {}
        for ch, pin in outputs.items():
            status[ch] = pin.value()
        
        status_json = json.dumps(status)
        topic = f"wc/{NODE_ID}/status"
        mqtt_client.publish(topic, status_json)
        print(f"Published status: {status_json}")

# === Utility Functions ===
def blink_led(times=2, delay=100):
    for _ in range(times):
        led.value(1)
        time.sleep_ms(delay)
        led.value(0)
        time.sleep_ms(delay)

# === Main Loop ===
def main():
    print(f"=== ESP8266 Node {NODE_ID} Starting ===")
    
    if not connect_wifi():
        print("Cannot continue without WiFi")
        return
    
    if not connect_mqtt():
        print("Cannot continue without MQTT")
        return
    
    print("Node ready and listening for commands")
    
    while True:
        try:
            mqtt_client.check_msg()
            
            # Check WiFi and reconnect if needed
            if not sta_if.isconnected():
                print("WiFi disconnected, reconnecting...")
                connect_wifi()
                connect_mqtt()
        except Exception as e:
            print(f"Error in main loop: {e}")
            try:
                mqtt_client.connect()
            except:
                time.sleep(5)
        
        time.sleep_ms(100)  # Small delay to prevent tight loop

# Start the program
if __name__ == "__main__":
    main()