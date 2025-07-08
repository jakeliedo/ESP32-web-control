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
led = Pin(2, Pin.OUT)
relay = Pin(5, Pin.OUT)
led.value(1)  # OFF (inverted)
relay.value(0)  # OFF

# === Global vars ===
mqtt_client = None
timer = None
blink_count = 0

# === WiFi ===
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if "Michelle" in [n[0].decode() for n in wlan.scan()]:
        wlan.connect('Michelle', '0908800130')
    elif "Floor 9" in [n[0].decode() for n in wlan.scan()]:
        wlan.connect('Floor 9', 'Veg@s123')
    else:
        return False
    
    for _ in range(20):
        if wlan.isconnected():
            print('WiFi OK:', wlan.ifconfig()[0])
            return True
        time.sleep(0.5)
    return False

# === MQTT ===
def on_msg(topic, msg):
    global timer, blink_count
    try:
        cmd = msg.decode().strip()
        if cmd in ['flush', 'on']:
            print('FLUSH!')
            relay.value(1)
            blink_count = 25  # 5 seconds at 200ms interval
            start_blink()
            # Auto-off timer
            if timer:
                timer.deinit()
            timer = Timer(-1)
            timer.init(period=5000, mode=Timer.ONE_SHOT, callback=stop_relay)
    except:
        pass

def start_blink():
    global blink_count
    if blink_count > 0:
        led.value(not led.value())
        blink_count -= 1
        Timer(-1).init(period=200, mode=Timer.ONE_SHOT, callback=lambda t: start_blink())
    else:
        led.value(1)  # OFF

def stop_relay(t):
    relay.value(0)
    print('STOP')

def connect_mqtt():
    global mqtt_client
    try:
        mqtt_client = MQTTClient(f"{NODE_ID}_{time.ticks_ms()}", MQTT_BROKER)
        mqtt_client.set_callback(on_msg)
        mqtt_client.connect()
        mqtt_client.subscribe(f"wc/{NODE_ID}/command")
        print('MQTT OK')
        return True
    except:
        return False

# === Main ===
def main():
    print(f'Node {NODE_ID} starting...')
    
    if not connect_wifi():
        print('WiFi FAIL')
        return
    
    if not connect_mqtt():
        print('MQTT FAIL')
        return
    
    print('Ready!')
    
    while True:
        try:
            mqtt_client.check_msg()
            time.sleep_ms(100)
        except:
            time.sleep(1)

if __name__ == "__main__":
    main()
