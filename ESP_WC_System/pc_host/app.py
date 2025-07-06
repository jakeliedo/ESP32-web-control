from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect
import threading
import time
import json
import os
import subprocess

# Import our modules
from config import DEBUG, SECRET_KEY, HOST, PORT, WC_NODES
from mqtt_handler import MQTTHandler
from database import get_all_nodes, get_recent_events, log_event

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app)
csrf = CSRFProtect(app)
# Initialize MQTT Handler with socketio for real-time updates
mqtt_handler = MQTTHandler(socketio)

def check_and_start_mosquitto():
    """Check if Mosquitto service is running and try to start it if not"""
    try:
        # Check status
        result = subprocess.run(['sc', 'query', 'mosquitto'], 
                            capture_output=True, text=True)
        
        if "RUNNING" not in result.stdout:
            print("⚠️ Mosquitto service is not running. Attempting to start it...")
            try:
                # Try to start the service
                subprocess.run(['net', 'start', 'mosquitto'], 
                            capture_output=True, text=True)
                
                # Wait for service to start
                time.sleep(2)
                
                # Check if started successfully
                result = subprocess.run(['sc', 'query', 'mosquitto'], 
                                    capture_output=True, text=True)
                
                if "RUNNING" in result.stdout:
                    print("✅ Successfully started Mosquitto service")
                    return True
                else:
                    print("❌ Failed to start Mosquitto service")
                    print("Please make sure Mosquitto is installed correctly as a service")
                    return False
            except Exception as e:
                print(f"❌ Error starting Mosquitto service: {e}")
                return False
        else:
            print("✅ Mosquitto service is already running")
            return True
    except Exception as e:
        print(f"❌ Error checking Mosquitto service: {e}")
        return False

def check_mqtt_broker():
    """Check if MQTT broker is accessible"""
    import socket
    try:
        from config import MQTT_BROKER, MQTT_PORT
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((MQTT_BROKER, MQTT_PORT))
        s.close()
        if result == 0:
            print(f"✅ MQTT broker at {MQTT_BROKER}:{MQTT_PORT} is available")
            return True
        else:
            print(f"❌ MQTT broker at {MQTT_BROKER}:{MQTT_PORT} is not accessible")
            print("Please check if Mosquitto service is running")
            return False
    except Exception as e:
        print(f"❌ Error checking MQTT connection: {e}")
        return False

# Check Mosquitto service status and start if needed
check_and_start_mosquitto()

# Connect to MQTT broker
if check_mqtt_broker():
    if mqtt_handler.connect():
        print("✅ Successfully connected to MQTT broker")
    else:
        print("⚠️ Could not connect to MQTT broker. Running in limited mode.")
else:
    print("⚠️ MQTT broker is not accessible. Running in limited mode.")

# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    nodes = get_all_nodes()
    events = get_recent_events(10)  # Get 10 most recent events
    return render_template('index.html', nodes=nodes, events=events)

@app.route('/control/<node_id>', methods=['POST'])
def control(node_id):
    """Handle control actions"""
    action = request.form.get('action', 'flush')
    
    # Publish command to MQTT
    mqtt_handler.publish_command(node_id, action)
    
    # Log the action in our database
    log_event(node_id, "web_command", {"action": action})
    
    return redirect(url_for('index'))

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    nodes = get_all_nodes()
    return jsonify({
        "status": "online",
        "nodes": nodes,
        "timestamp": time.time()
    })

@app.route('/api/control/<node_id>', methods=['POST'])
def api_control(node_id):
    """API endpoint for control actions"""
    data = request.json or {}
    action = data.get('action', 'flush')
    
    # Publish command to MQTT
    success = mqtt_handler.publish_command(node_id, action, data)
    
    # Log the API action
    log_event(node_id, "api_command", {"action": action, "data": data})
    
    return jsonify({
        "success": success,
        "node_id": node_id,
        "action": action,
        "timestamp": time.time()
    })

@app.route('/events')
def events_page():
    """Page to view system events"""
    limit = int(request.args.get('limit', 50))
    events = get_recent_events(limit)
    return render_template('events.html', events=events)

# SocketIO events for real-time updates
@socketio.on('connect')
def handle_connect():
    # Lấy IP của client kết nối
    client_ip = request.remote_addr
    print(f'Client connected from {client_ip}')

    # Log sự kiện kết nối vào database
    log_event('system', 'client_connect', {'client_ip': client_ip})
    
    # Emit sự kiện này đến tất cả các clients để cập nhật UI
    socketio.emit('new_event', {
        'timestamp': time.time(),
        'node_id': 'system',
        'event_type': 'client_connect',
        'data': {'client_ip': client_ip}
    })
    
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Application shutdown handler
def shutdown_handler():
    print("Application shutting down...")
    mqtt_handler.disconnect()

# Register shutdown handler
import atexit
atexit.register(shutdown_handler)

# Run the application
if __name__ == '__main__':
    try:
        print(f"🚀 PC Host running at http://{HOST}:{PORT}")
        socketio.run(app, host=HOST, port=PORT, debug=DEBUG)
    except KeyboardInterrupt:
        print("Shutting down by keyboard interrupt...")
        shutdown_handler()