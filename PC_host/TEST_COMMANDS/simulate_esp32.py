#!/usr/bin/env python3
"""
Simulate ESP32 nodes sending MQTT messages to test the system
"""

import paho.mqtt.client as mqtt
import json
import time
import random

def simulate_esp32_node(node_id, node_type="male", room_name="Room 1"):
    """Simulate an ESP32 node"""
    
    def on_connect(client, userdata, flags, rc):
        print(f"✅ {node_id} connected to MQTT broker (rc={rc})")
        if rc == 0:
            # Subscribe to commands for this node
            client.subscribe(f"wc/{node_id}/cmd")
            print(f"📡 {node_id} subscribed to wc/{node_id}/cmd")
            
            # Send initial status
            status_data = {
                "status": "online",
                "node_id": node_id,
                "room_name": room_name,
                "node_type": node_type,
                "timestamp": time.time(),
                "ip": "192.168.100.59",
                "free_memory": random.randint(20000, 30000)
            }
            client.publish(f"wc/{node_id}/status", json.dumps(status_data))
            print(f"📤 {node_id} sent status: online")

    def on_message(client, userdata, msg):
        print(f"📥 {node_id} received command: {msg.topic} = {msg.payload.decode()}")
        
        # Simulate processing command
        try:
            cmd_data = json.loads(msg.payload.decode())
            action = cmd_data.get('action', 'unknown')
            
            # Send response
            response_data = {
                "node_id": node_id,
                "action": action,
                "success": True,
                "timestamp": time.time(),
                "message": f"Action {action} completed successfully"
            }
            client.publish(f"wc/{node_id}/response", json.dumps(response_data))
            print(f"📤 {node_id} sent response for action: {action}")
            
        except Exception as e:
            print(f"❌ {node_id} error processing command: {e}")

    # Create MQTT client
    client = mqtt.Client(f"esp32_sim_{node_id}")
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        print(f"🔌 {node_id} connecting to MQTT broker...")
        client.connect("127.0.0.1", 1883, 60)
        client.loop_start()
        
        # Send periodic heartbeat
        for i in range(30):  # Run for 30 seconds
            time.sleep(2)
            
            # Send heartbeat every 6 seconds
            if i % 3 == 0:
                heartbeat_data = {
                    "node_id": node_id,
                    "timestamp": time.time(),
                    "uptime": i * 2,
                    "free_memory": random.randint(20000, 30000)
                }
                client.publish(f"wc/{node_id}/heartbeat", json.dumps(heartbeat_data))
                print(f"💓 {node_id} heartbeat sent")
        
        print(f"🛑 {node_id} stopping simulation...")
        client.loop_stop()
        client.disconnect()
        
    except Exception as e:
        print(f"❌ {node_id} simulation error: {e}")

def main():
    print("🎭 Starting ESP32 Node Simulation")
    print("🦟 This will simulate ESP32 nodes connecting to MQTT broker")
    print("="*60)
    
    # Simulate different nodes
    nodes = [
        ("wc_male_01", "male", "Male Room 1"),
        ("wc_male_02", "male", "Male Room 2"), 
        ("wc_female_01", "female", "Female Room 1"),
        ("wc_female_02", "female", "Female Room 2")
    ]
    
    import threading
    
    threads = []
    for node_id, node_type, room_name in nodes:
        thread = threading.Thread(target=simulate_esp32_node, args=(node_id, node_type, room_name))
        threads.append(thread)
        thread.start()
        time.sleep(1)  # Stagger connections
    
    # Wait for all threads
    for thread in threads:
        thread.join()
    
    print("✅ All ESP32 simulations completed!")

if __name__ == "__main__":
    main()
