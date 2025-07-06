import json
import network
import time
from machine import Pin
from umqtt.simple import MQTTClient
import ubinascii
import machine

# Config
led = Pin(2, Pin.OUT)
PC_HOST = "192.168.1.182"  # IP của PC host
MQTT_PORT = 1883
CLIENT_ID = f"esp32_test_{ubinascii.hexlify(machine.unique_id()).decode()}"
WIFI_SSID = "Michelle"
WIFI_PASS = "0908800130"

def connect_wifi():
    """Connect to WiFi"""
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    
    print(f"Connecting to {WIFI_SSID}...")
    sta_if.connect(WIFI_SSID, WIFI_PASS)
    
    for i in range(20):
        if sta_if.isconnected():
            ip = sta_if.ifconfig()[0]
            print(f"Connected to WiFi. IP: {ip}")
            return True, ip
        print(".", end="")
        time.sleep(0.5)
    
    print("WiFi connection failed")
    return False, None

def mqtt_callback(topic, msg):
    """Handle incoming MQTT messages"""
    topic_str = topic.decode()
    try:
        msg_str = msg.decode()
        print(f"Received: {topic_str} = {msg_str}")
        
        # Cố gắng parse JSON message
        data = json.loads(msg_str)
        
        # Xử lý các lệnh
        if topic_str == "wc/esp32/command":
            if data.get("action") == "flush":
                print("Executing flush command")
                # Mô phỏng xả nước với LED
                for _ in range(5):
                    led.value(1)
                    time.sleep(0.1)
                    led.value(0)
                    time.sleep(0.1)
            else:
                # Chỉ nhấp nháy LED một lần cho các lệnh khác
                led.value(1)
                time.sleep(0.1)
                led.value(0)
    except:
        # Nếu không phải JSON hoặc có lỗi, chỉ nhấp nháy LED
        led.value(1)
        time.sleep(0.1)
        led.value(0)

def main():
    # Connect to WiFi
    connected, ip = connect_wifi()
    if not connected:
        print("WiFi connection failed")
        return
    
    # Connect to MQTT
    print(f"Connecting to MQTT broker at {PC_HOST}...")
    
    try:
        client = MQTTClient(CLIENT_ID, PC_HOST, MQTT_PORT, keepalive=30)
        client.set_callback(mqtt_callback)
        client.connect()
        print("✓ Connected to MQTT broker!")
        
        # Subscribe thành công
        client.subscribe(b"wc/esp32/command")
        
        # Gửi status message dùng JSON
        status_data = {
            "status": "online",
            "ip": ip,
            "uptime": 0,
            "device_id": CLIENT_ID
        }
        
        # Sử dụng json.dumps để chuyển đổi Python dict thành JSON string
        status_json = json.dumps(status_data)
        client.publish(b"wc/esp32/status", status_json.encode())
        
        # In thông báo thành công
        print(f"✓ Subscribed to wc/esp32/command")
        print(f"✓ Published status: {status_json}")
        
        # Blink LED to indicate success
        for _ in range(3):
            led.value(1)
            time.sleep(0.1)
            led.value(0)
            time.sleep(0.1)
        
        # Simple message check loop
        count = 0
        while True:
            # Check for messages
            client.check_msg()
            
            # Publish heartbeat every 5 seconds
            if count % 50 == 0:
                # Cập nhật trạng thái
                status_data["uptime"] = count // 10
                status_data["heartbeat"] = count // 50
                
                # Chuyển đổi thành JSON và gửi
                status_json = json.dumps(status_data)
                client.publish(b"wc/esp32/status", status_json.encode())
                
                print(f"♥ Heartbeat sent (uptime: {status_data['uptime']}s)")
                
                # Nhấp nháy LED
                led.value(1)
                time.sleep(0.05)
                led.value(0)
            
            count += 1
            time.sleep(0.1)
            
    except Exception as e:
        print(f"Error: {e}")
        led.value(1)  # LED stays on to indicate error

if __name__ == "__main__":
    main()