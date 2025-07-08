#!/usr/bin/env python3
"""
Simple embedded MQTT broker for testing
Uses Python's simple MQTT broker implementation
"""

import sys
import os
import time

# Try to use a simple MQTT broker if available
try:
    # Option 1: Try using simple embedded broker
    import subprocess
    
    def start_mosquitto():
        """Try to start mosquitto if available"""
        try:
            # Check if mosquitto is available
            result = subprocess.run(['mosquitto', '-h'], capture_output=True, text=True)
            if result.returncode == 0:
                print("🦟 Starting Mosquitto MQTT broker...")
                process = subprocess.Popen(['mosquitto', '-p', '1883', '-v'], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE)
                return process
        except FileNotFoundError:
            pass
        return None
    
    def start_simple_broker():
        """Start a simple Python MQTT broker"""
        print("🔧 Starting simple Python MQTT broker on port 1883...")
        print("📡 Broker will accept connections on 192.168.100.121:1883")
        
        # Create a simple broker simulation
        import socket
        import threading
        import json
        
        class SimpleMQTTBroker:
            def __init__(self, host='192.168.100.121', port=1883):
                self.host = host
                self.port = port
                self.clients = {}
                self.subscriptions = {}
                self.messages = []
                
            def start(self):
                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    self.server.bind((self.host, self.port))
                    self.server.listen(5)
                    print(f"✅ MQTT Broker listening on {self.host}:{self.port}")
                    
                    while True:
                        client_socket, address = self.server.accept()
                        print(f"📱 New client connected: {address}")
                        client_thread = threading.Thread(
                            target=self.handle_client, 
                            args=(client_socket, address)
                        )
                        client_thread.daemon = True
                        client_thread.start()
                        
                except Exception as e:
                    print(f"❌ Error starting broker: {e}")
                    
            def handle_client(self, client_socket, address):
                try:
                    while True:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                        print(f"📨 Received from {address}: {data}")
                        # Simple echo response for MQTT CONNECT
                        client_socket.send(b'\\x20\\x02\\x00\\x00')  # CONNACK
                except Exception as e:
                    print(f"❌ Error handling client {address}: {e}")
                finally:
                    client_socket.close()
                    print(f"📤 Client {address} disconnected")
        
        broker = SimpleMQTTBroker()
        broker.start()
    
    if __name__ == "__main__":
        print("🚀 Starting MQTT Broker for ESP32 WC System...")
        
        # Try mosquitto first, then fallback to simple broker
        mosquitto_process = start_mosquitto()
        if mosquitto_process:
            print("✅ Mosquitto MQTT broker started")
            try:
                mosquitto_process.wait()
            except KeyboardInterrupt:
                print("🛑 Stopping Mosquitto...")
                mosquitto_process.terminate()
        else:
            print("⚠️  Mosquitto not found, using simple Python broker...")
            start_simple_broker()
            
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("For a proper MQTT broker, install Mosquitto:")
    print("  Windows: choco install mosquitto")
    print("  Or download from: https://mosquitto.org/download/")
