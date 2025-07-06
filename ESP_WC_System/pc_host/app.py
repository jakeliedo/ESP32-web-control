from flask import Flask, render_template, render_template_string, request, redirect, url_for, jsonify
from flask_socketio import SocketIO
import threading
import time
import json
import os
import requests
import uuid

# Import modules
from config import DEBUG, SECRET_KEY, HOST, PORT
from mqtt_handler import MQTTHandler
from database import get_all_nodes, get_recent_events, log_event, update_node_status

# Khởi tạo Flask app
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app)

# Địa chỉ IP của ESP32 (thay bằng IP thực tế của bạn)
ESP32_IP = "http://192.168.100.72"

# Khởi tạo MQTT Handler với socketio cho real-time updates
mqtt_handler = MQTTHandler(socketio)

# Kết nối đến MQTT broker
if mqtt_handler.connect():
    print("✅ Connected to MQTT broker successfully")
else:
    print("⚠️ Could not connect to MQTT broker. Running in limited mode.")

# HTML Template cũ - giữ lại để tương thích với code cũ
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Web Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    html, body {
        height: 100%;
        margin: 0;
        padding: 0;
    }
    body {
        background: #111;
        color: #fff;
        font-family: Arial, sans-serif;
        min-height: 100vh;
        min-width: 100vw;
        box-sizing: border-box;
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
    }
    .container {
        width: 100vw;
        max-width: 500px;
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: 1fr 1fr;
        gap: 18px;
        padding: 12px 0 32px 0;
        box-sizing: border-box;
    }
    .card {
    background: transparent;
    border: 2.5px solid #444;
    border-radius: 22px;
    padding: 18px 8px 18px 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    box-shadow: 0 2px 16px #000a;
    min-width: 0;
    min-height: 280px;
    width: 95%;
    justify-content: space-between;
    }
    .icon img {
        width: 72px;
        height: 108px;
        margin-bottom: 8px;
        margin-top: 12px;
    }
    .room {
        font-size: 1.4rem;
        margin-bottom: 18px;
        font-weight: bold;
    }
    .flush-btn {
        background: none;
        border: none;
        padding: 0;
        cursor: pointer;
        outline: none;
        margin-top: 8px;
        margin-bottom: 12px;
    }
    .flush-btn img {
        width: 72px;
        height: 72px;
        display: block;
    }
    .flush-btn:active img {
        filter: brightness(0.8);
    }
    .logo {
        position: fixed;
        right: 16px;
        bottom: 16px;
        width: 48px;
        opacity: 0.85;
        z-index: 10;
    }
    @media (max-width: 600px) {
        .container {
            max-width: 98vw;
            gap: 10px;
            padding: 4px 0 24px 0;
        }
        .card {
            padding: 10px 2px 10px 2px;
            min-height: 240px;
        }
        .icon img {
            width: 48px;
            height: 72px;
            margin-bottom: 8px;
        }
        .flush-btn img {
            width: 60px;
            height: 60px;
        }
        .logo {
            width: 32px;
            right: 8px;
            bottom: 8px;
        }
        .room {
            font-size: 1.1rem;
            margin-bottom: 40px;
        }
    }
    </style>
</head>
<body>
    <form method="post" style="width:100%;">
        <div class="container">
            <div class="card">
                <div class="icon"><img src="/static/male.png" alt="Male"></div>
                <div class="room">Room 1</div>
                <button class="flush-btn" name="action" value="1_on">
                    <img src="/static/button.png" alt="FLUSH">
                </button>
            </div>
            <div class="card">
                <div class="icon"><img src="/static/male.png" alt="Male"></div>
                <div class="room">Room 2</div>
                <button class="flush-btn" name="action" value="2_on">
                    <img src="/static/button.png" alt="FLUSH">
                </button>
            </div>
            <div class="card">
                <div class="icon"><img src="/static/female.png" alt="Female"></div>
                <div class="room">Room 1</div>
                <button class="flush-btn" name="action" value="3_on">
                    <img src="/static/button.png" alt="FLUSH">
                </button>
            </div>
            <div></div>
        </div>
    </form>
    <img src="/static/logo.png" class="logo" alt="Logo">
</body>
</html>
"""

# Routes
@app.route('/')
def dashboard():
    """Main dashboard page with Node and Events data"""
    try:
        nodes = get_all_nodes()
        print(f"DEBUG: Found {len(nodes)} nodes in database")
        events = get_recent_events(10)  # Get 10 most recent events
        return render_template('index.html', nodes=nodes, events=events)
    except Exception as e:
        print(f"Error rendering dashboard: {e}")
        # Fall back to simple template if templates not found
        return render_template_string(HTML)

@app.route("/simple", methods=["GET", "POST"])
def simple_index():
    """Simple UI for backward compatibility"""
    if request.method == "POST":
        action = request.form.get("action")
        # Gửi lệnh tới ESP32
        try:
            resp = requests.post(f"{ESP32_IP}/control", data={"ch": action}, timeout=2)
            print(f"Sent command {action} to ESP32, response: {resp.text}")
            
            # Log the command in database
            log_event('esp32', 'web_command', {'action': action})
            
            # Also publish to MQTT
            node_id = action.split('_')[0] if '_' in action else 'esp32'
            mqtt_handler.publish_command(node_id, action)
            
        except Exception as e:
            print(f"Error sending command to ESP32: {e}")
        return redirect("/simple")
    return render_template_string(HTML)

@app.route('/control/<node_id>', methods=['POST'])
def control(node_id):
    """Handle control actions for specific nodes"""
    try:
        action = request.form.get('action', 'flush')
        print(f"DEBUG: Control request for node_id: {node_id}, action: {action}")
        
        # Publish command to MQTT
        success = mqtt_handler.publish_command(node_id, action)
        
        # Log the action in our database
        log_event(node_id, "web_command", {"action": action, "success": success})
        
        return redirect(url_for('dashboard'))
    except Exception as e:
        print(f"Error in control: {e}")
        return f"Error: {str(e)}", 500

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
    """Handle new client connections"""
    client_ip = request.remote_addr
    print(f'Client connected from {client_ip}')

    # Log client connection event
    log_event('system', 'client_connect', {'client_ip': client_ip})
    
    # Broadcast client connection to all clients
    socketio.emit('new_event', {
        'timestamp': time.time(),
        'node_id': 'system',
        'event_type': 'client_connect',
        'data': {'client_ip': client_ip}
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnections"""
    print('Client disconnected')

# Application shutdown handler
def shutdown_handler():
    """Clean up resources when shutting down"""
    print("Application shutting down...")
    mqtt_handler.disconnect()

# Register shutdown handler
import atexit
atexit.register(shutdown_handler)

# Run the application
if __name__ == "__main__":
    try:
        print(f"🚀 PC Host running at http://{HOST}:{PORT}")
        print(f"Simple UI available at http://{HOST}:{PORT}/simple")
        socketio.run(app, host=HOST, port=PORT, debug=DEBUG)
    except KeyboardInterrupt:
        print("Shutting down by keyboard interrupt...")
        shutdown_handler()
    except Exception as e:
        print(f"Error starting server: {e}")