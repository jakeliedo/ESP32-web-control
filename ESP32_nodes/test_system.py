#!/usr/bin/env python3
"""
ESP32 WC Control System - Testing Script
This script helps test the communication between PC and ESP32 nodes
"""

import paho.mqtt.client as mqtt
import json
import time
import threading

class WCSystemTester:
    def __init__(self, broker_host="localhost", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client("wc_system_tester")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.nodes_status = {}
        
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT broker with result code {rc}")
        # Subscribe to all WC topics
        client.subscribe("wc/+/status")
        client.subscribe("wc/+/response")
        print("Subscribed to status and response topics")
        
    def on_message(self, client, userdata, message):
        topic = message.topic
        payload = message.payload.decode('utf-8')
        
        try:
            # Parse topic
            topic_parts = topic.split('/')
            node_id = topic_parts[1]
            message_type = topic_parts[2]
            
            # Parse payload
            data = json.loads(payload)
            
            # Update node status
            if message_type == "status":
                self.nodes_status[node_id] = data
                print(f"📡 Status from {node_id}: {data.get('status', 'unknown')}")
                
            elif message_type == "response":
                action = data.get('action', 'unknown')
                success = data.get('success', False)
                print(f"✅ Response from {node_id}: {action} - {'SUCCESS' if success else 'FAILED'}")
                
        except Exception as e:
            print(f"Error parsing message: {e}")
            print(f"Topic: {topic}")
            print(f"Payload: {payload}")
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def send_command(self, node_id, action="flush"):
        """Send command to a specific node"""
        try:
            topic = f"wc/{node_id}/command"
            payload = {
                "action": action,
                "timestamp": time.time(),
                "source": "test_script"
            }
            
            message = json.dumps(payload)
            result = self.client.publish(topic, message)
            
            if result.rc == 0:
                print(f"🚀 Sent {action} command to {node_id}")
                return True
            else:
                print(f"❌ Failed to send command to {node_id}")
                return False
                
        except Exception as e:
            print(f"Error sending command: {e}")
            return False
    
    def test_all_nodes(self):
        """Test all 4 nodes"""
        nodes = [
            "wc_male_01",    # Room1
            "wc_male_02",    # Room2  
            "wc_female_01",  # Room3
            "wc_female_02"   # Room4
        ]
        
        print("\n🧪 Testing all nodes...")
        print("=" * 40)
        
        for node_id in nodes:
            print(f"\nTesting {node_id}...")
            if self.send_command(node_id, "flush"):
                time.sleep(1)  # Wait for response
            time.sleep(2)  # Wait between nodes
    
    def show_status(self):
        """Show current status of all nodes"""
        print("\n📊 Current Node Status:")
        print("=" * 40)
        
        if not self.nodes_status:
            print("No nodes reporting status yet...")
            return
            
        for node_id, status in self.nodes_status.items():
            room_name = status.get('room_name', 'Unknown')
            node_type = status.get('node_type', 'unknown')
            online_status = status.get('status', 'unknown')
            wifi_status = status.get('wifi_connected', False)
            relay_active = status.get('relay_active', False)
            
            print(f"🏠 {room_name} ({node_id})")
            print(f"   Type: {node_type}")
            print(f"   Status: {online_status}")
            print(f"   WiFi: {'✅' if wifi_status else '❌'}")
            print(f"   Relay: {'🔴 ACTIVE' if relay_active else '⚫ INACTIVE'}")
            print()
    
    def interactive_mode(self):
        """Interactive testing mode"""
        print("\n🎮 Interactive Mode")
        print("Commands:")
        print("  1-4: Test Room 1-4")
        print("  a: Test all nodes")
        print("  s: Show status")
        print("  q: Quit")
        print()
        
        while True:
            try:
                cmd = input("Enter command: ").strip().lower()
                
                if cmd == 'q':
                    break
                elif cmd == 'a':
                    self.test_all_nodes()
                elif cmd == 's':
                    self.show_status()
                elif cmd in ['1', '2', '3', '4']:
                    nodes = ["wc_male_01", "wc_male_02", "wc_female_01", "wc_female_02"]
                    node_id = nodes[int(cmd) - 1]
                    self.send_command(node_id, "flush")
                else:
                    print("Invalid command!")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()

def main():
    print("ESP32 WC Control System - Test Script")
    print("=" * 50)
    
    # Create tester instance
    tester = WCSystemTester()
    
    # Connect to MQTT broker
    if not tester.connect():
        print("Failed to connect to MQTT broker. Make sure it's running!")
        return
    
    print("Connected to MQTT broker!")
    print("Waiting for node status updates...")
    
    # Wait a moment for initial status messages
    time.sleep(3)
    
    try:
        # Show initial status
        tester.show_status()
        
        # Start interactive mode
        tester.interactive_mode()
        
    except KeyboardInterrupt:
        print("\nStopping test script...")
    
    finally:
        tester.disconnect()
        print("Disconnected from MQTT broker.")

if __name__ == "__main__":
    main()
