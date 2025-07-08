#!/usr/bin/env python3
"""
Simple MQTT broker using Python - for development/testing
"""

import socket
import threading
import time
import json
from datetime import datetime

class SimpleMQTTBroker:
    def __init__(self, host='0.0.0.0', port=1883):
        self.host = host
        self.port = port
        self.clients = {}
        self.topics = {}
        self.running = False
        
    def start(self):
        """Start the MQTT broker"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            print(f"🦟 Simple MQTT Broker started on {self.host}:{self.port}")
            print(f"📡 Listening for ESP32/ESP8266 connections...")
            print("="*50)
            
            while self.running:
                try:
                    client_socket, address = self.socket.accept()
                    print(f"✅ New client connected from {address}")
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except Exception as e:
                    if self.running:
                        print(f"❌ Error accepting connection: {e}")
                        
        except Exception as e:
            print(f"❌ Error starting broker: {e}")
        finally:
            self.socket.close()
            
    def handle_client(self, client_socket, address):
        """Handle individual client connections"""
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                    
                # Basic MQTT packet handling
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"[{timestamp}] 📩 Received from {address}: {len(data)} bytes")
                
                # Send acknowledgment
                client_socket.send(b'\x20\x02\x00\x00')  # CONNACK
                
        except Exception as e:
            print(f"❌ Client {address} error: {e}")
        finally:
            client_socket.close()
            print(f"❌ Client {address} disconnected")
            
    def stop(self):
        """Stop the broker"""
        self.running = False
        if hasattr(self, 'socket'):
            self.socket.close()

if __name__ == "__main__":
    broker = SimpleMQTTBroker('192.168.100.121', 1883)
    
    try:
        broker.start()
    except KeyboardInterrupt:
        print("\n🛑 Stopping MQTT broker...")
        broker.stop()
        print("✅ MQTT broker stopped")
