import paho.mqtt.client as mqtt
import json
import time
from config import MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID
from database import update_node_status, log_event
import uuid

class MQTTHandler:
    def __init__(self, socketio=None):
        unique_id = f"{MQTT_CLIENT_ID}_{uuid.uuid4().hex[:8]}"
        self.client = mqtt.Client(client_id=unique_id)  # Sử dụng unique_id thay vì MQTT_CLIENT_ID
    
        # Set auth if provided
        if MQTT_USERNAME and MQTT_PASSWORD:
            self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        
        # Set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect  # ĐÃ THIẾT LẬP NHƯNG CHƯA ĐỊNH NGHĨA
    
        # For real-time updates
        self.socketio = socketio
    
        # Khởi tạo cờ reconnect
        self.is_connecting = False
        
    
    def connect(self):
        """Connect to MQTT broker"""
        if self.is_connecting:
            return False
    
        try:
            self.is_connecting = True
            # Thực hiện kết nối MQTT
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
            self.is_connecting = False
            return True
        except Exception as e:
            self.is_connecting = False
            print(f"Error connecting to MQTT: {e}")
            return False
            
    def on_connect(self, client, userdata, flags, rc):
        """Called when connected to MQTT broker"""
        print(f"Connected to MQTT broker with result code {rc}")
        
        # Subscribe to all WC topics
        client.subscribe("wc/#")
        print("Subscribed to wc/#")
        
        # Publish online status
        self.publish_status("pc_host", "online")
        print("🟢 MQTT Broker is running and listening for connections")
        print("Waiting for devices to connect...")
    
    # THÊM PHƯƠNG THỨC on_disconnect
    def on_disconnect(self, client, userdata, rc):
        """Called when disconnected from MQTT broker"""
        print(f"Disconnected from MQTT broker with result code {rc}")
        
        # Thông báo cho tất cả web clients
        if self.socketio:
            self.socketio.emit('mqtt_status', {'status': 'disconnected'})
        
    def on_message(self, client, userdata, message):
        """Called when a message is received on a subscribed topic"""
        topic = message.topic
        payload = message.payload.decode('utf-8')
        print(f"MQTT: {topic} = {payload}")
    
        # Broadcast to all connected web clients
        if self.socketio:
            self.socketio.emit('mqtt_message', {
                'topic': topic,
                'payload': payload
            })
    
        # Process messages from ESP32
        if topic == "wc/esp32/status":
            try:
                status_data = json.loads(payload)
                # Log event to database
                log_event('esp32', 'status_update', status_data)
            
                # Emit as new event for UI update
                if self.socketio:
                    self.socketio.emit('new_event', {
                        'timestamp': time.time(),
                        'node_id': 'esp32',
                        'event_type': 'status_update',
                        'data': status_data
                    })
            except Exception as e:
                print(f"Error processing ESP32 status: {e}")
    
    def publish_command(self, node_id, action, data=None):
        """Publish a command to a node"""
        if not self.client or not hasattr(self.client, 'is_connected') or not self.client.is_connected():
            print("MQTT client not connected")
            return False
    
        try:
            # Create command payload
            if data is None:
                data = {}
        
            payload = {
                "action": action,
                "timestamp": time.time()
            }
            payload.update(data)
        
            # Convert to JSON and publish
            json_payload = json.dumps(payload)
            topic = f"wc/{node_id}/command"
            result = self.client.publish(topic, json_payload)
        
            # Log command
            print(f"Published command to {topic}: {json_payload}")
        
            # Return success based on publish result
            return result.rc == 0
        except Exception as e:
            print(f"Error publishing command: {e}")
            return False
    
    def publish_status(self, node_id, status):
        """Publish status update"""
        topic = f"wc/{node_id}/status"
        payload = json.dumps({
            "status": status,
            "timestamp": time.time()
        })
        
        self.client.publish(topic, payload)
        print(f"Published status to {topic}: {payload}")
        
    def disconnect(self):
        """Disconnect from MQTT broker"""
        try:
            if hasattr(self, 'client') and self.client and hasattr(self.client, 'is_connected') and self.client.is_connected():
                self.publish_status("pc_host", "offline")
                self.client.loop_stop()
                self.client.disconnect()
        except Exception as e:
            print(f"Error during MQTT disconnect: {e}")