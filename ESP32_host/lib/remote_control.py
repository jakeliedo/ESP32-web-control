"""
WC Remote Control Logic
Handles remote control operations and MQTT communication
"""

import time
import json
from umqtt.simple import MQTTClient

class RemoteControl:
    """WC Remote Control Manager"""
    
    def __init__(self, client_id, broker_ip, broker_port=1883):
        self.client_id = client_id
        self.broker_ip = broker_ip
        self.broker_port = broker_port
        self.client = None
        self.connected = False
        self.callback = None
        self.node_status = {}
        self.last_heartbeat = 0
        
    def set_callback(self, callback):
        """Set MQTT message callback"""
        self.callback = callback
        
    def mqtt_callback(self, topic, msg):
        """Internal MQTT callback"""
        if self.callback:
            self.callback(topic, msg)
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            print(f"🔗 Connecting to MQTT broker at {self.broker_ip}:{self.broker_port}")
            
            self.client = MQTTClient(self.client_id, self.broker_ip, self.broker_port, keepalive=60)
            self.client.set_callback(self.mqtt_callback)
            self.client.connect()
            
            self.connected = True
            print("✅ Connected to MQTT broker!")
            
            # Publish status
            self.publish_status("online")
            
            return True
            
        except Exception as e:
            print(f"❌ MQTT connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client and self.connected:
            try:
                self.publish_status("offline")
                self.client.disconnect()
                self.connected = False
                print("📴 Disconnected from MQTT broker")
            except:
                pass
    
    def subscribe_to_nodes(self, nodes):
        """Subscribe to status updates from WC nodes"""
        if not self.connected:
            return False
            
        try:
            for node in nodes:
                status_topic = node["topic"].replace("/command", "/status")
                self.client.subscribe(status_topic.encode())
                print(f"📡 Subscribed to {status_topic}")
                
                # Initialize node status
                self.node_status[node["id"]] = {"status": "offline", "last_seen": 0}
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to subscribe: {e}")
            return False
    
    def send_flush_command(self, node):
        """Send flush command to specified node"""
        if not self.connected:
            print("❌ MQTT not connected")
            return False
        
        try:
            command = {
                "action": "flush",
                "timestamp": time.time(),
                "source": "remote_control",
                "client_id": self.client_id
            }
            
            command_json = json.dumps(command)
            topic = node["topic"].encode()
            
            self.client.publish(topic, command_json.encode())
            print(f"🚽 Sent flush command to {node['name']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send flush command: {e}")
            return False
    
    def publish_status(self, status):
        """Publish remote control status"""
        if not self.client:
            return False
            
        try:
            status_data = {
                "status": status,
                "device": "remote_control",
                "client_id": self.client_id,
                "timestamp": time.time()
            }
            
            status_json = json.dumps(status_data)
            self.client.publish(b"wc/remote/status", status_json.encode())
            print(f"📤 Published status: {status}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to publish status: {e}")
            return False
    
    def send_heartbeat(self, selected_node_id=None):
        """Send heartbeat message"""
        if not self.connected:
            return False
            
        try:
            current_time = time.time()
            
            heartbeat_data = {
                "heartbeat": True,
                "uptime": current_time,
                "selected_node": selected_node_id,
                "node_count": len(self.node_status),
                "client_id": self.client_id
            }
            
            heartbeat_json = json.dumps(heartbeat_data)
            self.client.publish(b"wc/remote/heartbeat", heartbeat_json.encode())
            
            self.last_heartbeat = current_time
            print("💓 Heartbeat sent")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send heartbeat: {e}")
            return False
    
    def check_messages(self):
        """Check for incoming MQTT messages"""
        if self.client and self.connected:
            try:
                self.client.check_msg()
                return True
            except Exception as e:
                print(f"❌ MQTT check_msg error: {e}")
                self.connected = False
                return False
        return False
    
    def update_node_status(self, node_id, status, last_seen=None):
        """Update status of a WC node"""
        if last_seen is None:
            last_seen = time.time()
            
        self.node_status[node_id] = {
            "status": status,
            "last_seen": last_seen
        }
        
        print(f"📊 Updated {node_id} status: {status}")
    
    def get_node_status(self, node_id):
        """Get status of a specific node"""
        return self.node_status.get(node_id, {"status": "offline", "last_seen": 0})
    
    def get_all_status(self):
        """Get status of all nodes"""
        current_time = time.time()
        status_summary = {}
        
        for node_id, data in self.node_status.items():
            # Consider node offline if not seen in last 60 seconds
            if current_time - data["last_seen"] > 60:
                status_summary[node_id] = {"status": "offline", "last_seen": data["last_seen"]}
            else:
                status_summary[node_id] = data
                
        return status_summary
    
    def should_send_heartbeat(self, interval=30):
        """Check if it's time to send heartbeat"""
        return (time.time() - self.last_heartbeat) > interval
    
    def reconnect(self):
        """Attempt to reconnect to MQTT broker"""
        self.disconnect()
        time.sleep(2)
        return self.connect()
    
    def is_connected(self):
        """Check if connected to MQTT broker"""
        return self.connected
