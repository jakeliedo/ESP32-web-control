#!/usr/bin/env python3
"""
Test script to debug MQTT and status issues
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import get_nodes_with_mock_data
from mqtt_handler import MQTTHandler
import time

def test_status():
    """Test the current node status"""
    print("🔍 Testing Node Status:")
    print("=" * 50)
    
    nodes = get_nodes_with_mock_data()
    for i, node in enumerate(nodes, 1):
        status_icon = "🟢" if node['status'] == 'online' else "🔴"
        print(f"   {i}. {node['name']} ({node['node_type']}) - {status_icon} {node['status']}")
    
    online_count = len([n for n in nodes if n['status'] == 'online'])
    offline_count = len([n for n in nodes if n['status'] == 'offline'])
    
    print(f"\n📊 Summary: {online_count} online, {offline_count} offline")
    
    if online_count == 0:
        print("✅ CORRECT: All nodes show offline when no ESP32 connected")
    else:
        print("❌ ISSUE: Some nodes show online when they shouldn't")
    
    return nodes

def test_mqtt_command():
    """Test MQTT command publishing"""
    print("\n🔍 Testing MQTT Command:")
    print("=" * 50)
    
    mqtt_handler = MQTTHandler()
    if mqtt_handler.connect():
        print("✅ MQTT connected successfully")
        
        # Test publishing flush command to Room1
        node_id = 'wc_male_01'
        success = mqtt_handler.publish_command(node_id, 'flush')
        
        if success:
            print(f"✅ FLUSH command sent to {node_id}")
            print("   Check ESP32 serial output for LED blinking...")
        else:
            print(f"❌ Failed to send FLUSH command to {node_id}")
        
        time.sleep(2)  # Wait for response
        mqtt_handler.disconnect()
    else:
        print("❌ Failed to connect to MQTT broker")

if __name__ == "__main__":
    print("🧪 ESP32 WC System Debug Test")
    print("=" * 50)
    
    # Test 1: Node Status
    nodes = test_status()
    
    # Test 2: MQTT Command (only if we have online nodes)
    online_nodes = [n for n in nodes if n['status'] == 'online']
    if online_nodes:
        test_mqtt_command()
    else:
        print("\n⏭️  Skipping MQTT test - no online nodes detected")
    
    print("\n🏁 Test Complete!")
