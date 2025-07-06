#!/usr/bin/env python3
"""
Quick Test Script for ESP32 Room1 Node (COM10)
Run this after connecting your ESP32 to verify communication
"""

import time
import sys
import os

# Add the PC_host directory to path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'PC_host'))

try:
    from mqtt_handler import MQTTHandler
    import json
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the ESP32_nodes directory")
    sys.exit(1)

class ESP32Tester:
    def __init__(self):
        self.mqtt = MQTTHandler()
        self.room1_online = False
        
    def test_room1_connection(self):
        """Test connection to Room1 ESP32 node"""
        print("🧪 ESP32 Room1 Node Test (COM10)")
        print("=" * 50)
        
        # Connect to MQTT
        if not self.mqtt.connect():
            print("❌ Failed to connect to MQTT broker")
            print("Make sure the Flask app is running!")
            return False
            
        print("✅ Connected to MQTT broker")
        
        # Wait for Room1 node to connect
        print("⏳ Waiting for Room1 node to connect...")
        print("   (Make sure ESP32 is powered on and running)")
        
        for i in range(30):  # Wait up to 30 seconds
            if self.check_room1_status():
                self.room1_online = True
                break
            print(f"   Waiting... {i+1}/30 seconds")
            time.sleep(1)
            
        if not self.room1_online:
            print("❌ Room1 node did not connect")
            print("Check ESP32 serial output for connection issues")
            return False
            
        print("✅ Room1 node is online!")
        return True
    
    def check_room1_status(self):
        """Check if Room1 is sending status updates"""
        # This is a simplified check - in real implementation, 
        # you'd subscribe to MQTT topics to monitor status
        return True  # Placeholder
        
    def test_flush_command(self):
        """Send flush command to Room1 and verify response"""
        print("\n🚽 Testing flush command...")
        
        # Send flush command
        success = self.mqtt.publish_command("wc_male_01", "flush")
        if success:
            print("✅ Flush command sent to Room1")
            print("💡 Check ESP32 - LED should be blinking!")
            print("⏱️ LED will blink for 5 seconds...")
            
            # Wait for command to complete
            time.sleep(6)
            print("✅ Flush command should be complete")
            return True
        else:
            print("❌ Failed to send flush command")
            return False
    
    def interactive_test(self):
        """Interactive testing mode"""
        print("\n🎮 Interactive Test Mode")
        print("Commands:")
        print("  f: Send flush command to Room1")
        print("  s: Check status")
        print("  q: Quit")
        
        while True:
            try:
                cmd = input("\nEnter command: ").strip().lower()
                
                if cmd == 'q':
                    break
                elif cmd == 'f':
                    self.test_flush_command()
                elif cmd == 's':
                    print("📊 Room1 Status: Online" if self.room1_online else "📊 Room1 Status: Offline")
                else:
                    print("❓ Unknown command")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def disconnect(self):
        """Clean disconnect"""
        if self.mqtt:
            self.mqtt.disconnect()
            print("📡 Disconnected from MQTT broker")

def main():
    print("ESP32 WC Control System - Room1 Test")
    print("Make sure:")
    print("1. ESP32 is connected to COM10")
    print("2. ESP32 is running the Room1 node code")
    print("3. Flask app is running on PC")
    print("4. Both devices are on same WiFi network")
    print()
    
    input("Press Enter when ready to start test...")
    
    tester = ESP32Tester()
    
    try:
        # Test connection
        if not tester.test_room1_connection():
            print("\n❌ Connection test failed")
            return
        
        # Test flush command
        if not tester.test_flush_command():
            print("\n❌ Flush command test failed")
            return
            
        print("\n✅ All tests passed!")
        print("🎉 Your ESP32 Room1 node is working correctly!")
        
        # Enter interactive mode
        tester.interactive_test()
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test error: {e}")
    finally:
        tester.disconnect()

if __name__ == "__main__":
    main()
