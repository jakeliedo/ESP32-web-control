#!/usr/bin/env python3
"""
Test MQTT connection to local Mosquitto broker
"""

import paho.mqtt.client as mqtt
import time
import json

def on_connect(client, userdata, flags, rc):
    print(f"✅ Connected to MQTT broker with result code {rc}")
    if rc == 0:
        print("🦟 Successfully connected to Mosquitto!")
        client.subscribe("test/#")
        client.subscribe("wc/#")
        print("📡 Subscribed to test/# and wc/# topics")
        
        # Send test message
        test_message = {
            "message": "Hello from PC Host",
            "timestamp": time.time(),
            "source": "mqtt_test.py"
        }
        client.publish("test/pc_host", json.dumps(test_message))
        print("📤 Sent test message to test/pc_host")
    else:
        print(f"❌ Failed to connect to MQTT broker, return code {rc}")

def on_message(client, userdata, msg):
    print(f"📥 Received: {msg.topic} = {msg.payload.decode()}")

def on_disconnect(client, userdata, rc):
    print(f"❌ Disconnected from MQTT broker with result code {rc}")

def test_mqtt():
    print("🔍 Testing MQTT connection to Mosquitto...")
    print("🦟 Broker: 127.0.0.1:1883")
    
    client = mqtt.Client(client_id="mqtt_test_client", callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    try:
        print("🔌 Connecting to MQTT broker...")
        client.connect("127.0.0.1", 1883, 60)
        
        print("🔄 Starting MQTT loop...")
        client.loop_start()
        
        # Keep alive for 10 seconds
        for i in range(10):
            print(f"⏱️ Testing... {i+1}/10")
            time.sleep(1)
            
            # Send periodic test messages
            if i % 3 == 0:
                client.publish("test/heartbeat", f"heartbeat_{i}")
        
        print("🛑 Stopping MQTT loop...")
        client.loop_stop()
        client.disconnect()
        print("✅ MQTT test completed successfully!")
        
    except Exception as e:
        print(f"❌ MQTT test failed: {e}")

if __name__ == "__main__":
    test_mqtt()
