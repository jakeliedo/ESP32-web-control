from flask import Flask, render_template, render_template_string, request, redirect, url_for, jsonify
from flask_socketio import SocketIO
import threading
import time
import json
import os
import uuid
import requests

# Import modules
from config import DEBUG, SECRET_KEY, HOST, PORT, MQTT_BROKER, MQTT_PORT
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

# Mock data for demo purposes - Limited to 4 nodes (offline when not connected)
MOCK_NODES = [
    {
        'node_id': 'wc_male_01',
        'name': 'Room 1',
        'node_type': 'male',
        'status': 'offline',  # Mock data shows offline until real devices connect
        'location': 'Floor 1',
        'last_seen': time.time() - 600  # 10 minutes ago
    },
    {
        'node_id': 'wc_male_02', 
        'name': 'Room 2',
        'node_type': 'male',
        'status': 'offline',  # Mock data shows offline until real devices connect
        'location': 'Floor 1', 
        'last_seen': time.time() - 600  # 10 minutes ago
    },
    {
        'node_id': 'wc_female_01',
        'name': 'Room 1', 
        'node_type': 'female',
        'status': 'offline',  # Mock data shows offline until real devices connect
        'location': 'Floor 1',
        'last_seen': time.time() - 600  # 10 minutes ago
    },
    {
        'node_id': 'wc_female_02',
        'name': 'Room 2',
        'node_type': 'female', 
        'status': 'offline',  # Mock data shows offline until real devices connect
        'location': 'Floor 1',
        'last_seen': time.time() - 600  # 10 minutes ago
    }
]

# Mock events data
MOCK_EVENTS = [
    {
        'id': 1,
        'timestamp': time.time() - 60,
        'node_id': 'wc_male_01',
        'event_type': 'web_command',
        'data': {'action': 'flush', 'success': True, 'ui': 'dashboard'}
    },
    {
        'id': 2, 
        'timestamp': time.time() - 180,
        'node_id': 'wc_female_01',
        'event_type': 'sensor_trigger',
        'data': {'sensor': 'motion', 'value': True}
    },
    {
        'id': 3,
        'timestamp': time.time() - 300,
        'node_id': 'wc_male_02',
        'event_type': 'status_change',
        'data': {'old_status': 'offline', 'new_status': 'online'}
    },
    {
        'id': 4,
        'timestamp': time.time() - 420,
        'node_id': 'wc_female_02',
        'event_type': 'web_command',
        'data': {'action': 'flush', 'success': False, 'ui': 'simple'}
    },
    {
        'id': 5,
        'timestamp': time.time() - 540,
        'node_id': 'wc_male_03',
        'event_type': 'web_command',
        'data': {'action': 'flush', 'success': True, 'ui': 'dashboard'}
    },
    {
        'id': 6,
        'timestamp': time.time() - 660,
        'node_id': 'wc_female_03',
        'event_type': 'sensor_trigger',
        'data': {'sensor': 'door', 'value': False}
    },
    {
        'id': 7,
        'timestamp': time.time() - 780,
        'node_id': 'system',
        'event_type': 'client_connect',
        'data': {'client_ip': '192.168.1.100'}
    },
    {
        'id': 8,
        'timestamp': time.time() - 900,
        'node_id': 'wc_male_01',
        'event_type': 'status_change',
        'data': {'old_status': 'offline', 'new_status': 'online'}
    }
]

def get_nodes_with_mock_data():
    """Get nodes from database, fallback to mock data if empty. Limit to 4 nodes maximum."""
    try:
        real_nodes = get_all_nodes()
        current_time = time.time()
        
        if real_nodes and len(real_nodes) > 0:
            # Check which nodes are actually online (seen within last 30 seconds)
            online_nodes = []
            for node in real_nodes:
                last_seen = node.get('last_seen', 0)
                time_since_seen = current_time - last_seen
                
                # Node is considered online only if seen within last 30 seconds
                if time_since_seen < 30:
                    node['status'] = 'online'
                    online_nodes.append(node)
                    print(f"📡 Node {node.get('id', 'unknown')} is ONLINE (last seen {time_since_seen:.1f}s ago)")
                else:
                    node['status'] = 'offline'  # Force offline if not seen recently
                    print(f"⚠️ Node {node.get('id', 'unknown')} is OFFLINE (last seen {time_since_seen:.1f}s ago)")
            
            # Add required fields for templates
            for node in real_nodes[:4]:
                if 'node_type' not in node:
                    if 'male' in node.get('id', ''):
                        node['node_type'] = 'male'
                    elif 'female' in node.get('id', ''):
                        node['node_type'] = 'female'
                    else:
                        node['node_type'] = 'unknown'
                
                # Ensure node_id field exists for templates
                if 'node_id' not in node and 'id' in node:
                    node['node_id'] = node['id']
            
            print(f"📊 Real nodes status: {len(online_nodes)} online, {len(real_nodes) - len(online_nodes)} offline")
            return real_nodes[:4]
        else:
            print("⚠️ No ESP32 devices found in database - Using MOCK data (all offline)")
            return MOCK_NODES[:4]
    except Exception as e:
        print(f"❌ Error getting nodes from database, using mock data: {e}")
        return MOCK_NODES[:4]

def get_events_with_mock_data(limit=10):
    """Get events from database, fallback to mock data if empty"""
    try:
        real_events = get_recent_events(limit)
        if real_events and len(real_events) > 0:
            return real_events
        else:
            print("No real events found, using mock data for demo")
            return MOCK_EVENTS[:limit]
    except Exception as e:
        print(f"Error getting events from database, using mock data: {e}")
        return MOCK_EVENTS[:limit]

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    """Main dashboard page with Node and Events data"""
    if request.method == 'POST':
        print(f"\n🔍 DASHBOARD POST REQUEST RECEIVED!")
        print(f"🔍 Form data: {dict(request.form)}")
        print(f"🔍 Request headers: {dict(request.headers)}")
        
        # Handle control actions from dashboard
        node_id = request.form.get('node_id')
        action = request.form.get('action', 'flush')
        
        print(f"🔍 Extracted values:")
        print(f"   - node_id: '{node_id}'")
        print(f"   - action: '{action}'")
        
        if node_id:
            try:
                # Publish command to MQTT
                print(f"🚀 Publishing MQTT command: {action} to node {node_id}")
                success = mqtt_handler.publish_command(node_id, action)
                
                # Log the action in our database
                log_event(node_id, "web_command", {"action": action, "success": success, "ui": "dashboard"})
                
                print(f"✅ Dashboard: Sent {action} to node {node_id}, success: {success}")
                
                # Return JSON response for AJAX requests
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': success,
                        'message': f'{action.upper()} command sent to {node_id}',
                        'node_id': node_id,
                        'action': action,
                        'timestamp': time.time()
                    })
                
            except Exception as e:
                print(f"❌ Error in dashboard control: {e}")
                
                # Return error JSON for AJAX requests
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': f'Error sending command: {str(e)}',
                        'node_id': node_id,
                        'action': action
                    }), 500
        else:
            print(f"⚠️ Dashboard: No node_id received in form data")
            
            # Return error JSON for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'message': 'No node selected',
                    'error': 'missing_node_id'
                }), 400
        
        # Regular form submission - redirect to dashboard
        return redirect(url_for('dashboard'))
    
    # GET request - show the dashboard
    try:
        nodes = get_nodes_with_mock_data()
        print(f"🔍 Dashboard rendering: Found {len(nodes)} nodes")
        events = get_events_with_mock_data(20)  # Get 20 most recent events for dashboard
        current_time = time.time()
        return render_template('index.html', nodes=nodes, events=events, current_time=current_time)
    except Exception as e:
        print(f"❌ Error rendering dashboard: {e}")
        # Fall back to simple template if templates not found
        return render_template_string(HTML)

@app.route("/simple", methods=["GET", "POST"])
def simple_index():
    """Mobile-optimized simple UI with 2x2 grid layout"""
    if request.method == "POST":
        print(f"\n🔍 SIMPLE UI POST REQUEST RECEIVED!")
        print(f"🔍 Form data: {dict(request.form)}")
        
        node_id = request.form.get("node_id")
        action = request.form.get("action", "flush")
        
        print(f"🔍 Extracted values:")
        print(f"   - node_id: '{node_id}'")
        print(f"   - action: '{action}'")
        
        if node_id:
            try:
                # Publish command to MQTT
                print(f"🚀 Publishing MQTT command: {action} to node {node_id}")
                success = mqtt_handler.publish_command(node_id, action)
                
                # Log the action in our database
                log_event(node_id, "web_command", {"action": action, "success": success, "ui": "simple"})
                
                print(f"✅ Simple UI: Sent {action} to node {node_id}, success: {success}")
                
            except Exception as e:
                print(f"❌ Error in simple UI control: {e}")
        else:
            print(f"⚠️ Simple UI: No node_id received in form data")
        
        return redirect("/simple")
    
    # GET request - show the simple UI
    try:
        nodes = get_nodes_with_mock_data()
        print(f"🔍 Simple UI rendering: Found {len(nodes)} nodes")
        return render_template('simple.html', nodes=nodes)
    except Exception as e:
        print(f"❌ Error rendering simple UI: {e}")
        # Fall back to old HTML template if simple.html not found
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
    """API endpoint to check system status"""
    try:
        nodes = get_nodes_with_mock_data()
        
        # Check MQTT connection status
        mqtt_status = {
            'connected': mqtt_handler.client.is_connected() if mqtt_handler else False,
            'broker': MQTT_BROKER,
            'port': MQTT_PORT
        }
        
        # Check nodes status
        nodes_status = []
        for node in nodes:
            nodes_status.append({
                'node_id': node.get('node_id'),
                'name': node.get('name', 'Unknown'),
                'status': node.get('status', 'offline'),
                'last_seen': node.get('last_seen'),
                'node_type': node.get('node_type', 'unknown')
            })
        
        return jsonify({
            'success': True,
            'timestamp': time.time(),
            'mqtt': mqtt_status,
            'nodes': nodes_status,
            'total_nodes': len(nodes),
            'online_nodes': len([n for n in nodes if n.get('status') == 'online'])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': time.time()
        }), 500

@app.route('/api/send_command', methods=['POST'])
def api_send_command():
    """API endpoint to send commands to nodes"""
    try:
        data = request.get_json()
        node_id = data.get('node_id')
        action = data.get('action', 'flush')
        
        if not node_id:
            return jsonify({
                'success': False,
                'error': 'node_id is required'
            }), 400
        
        # Send MQTT command
        success = mqtt_handler.publish_command(node_id, action)
        
        # Log the action
        log_event(node_id, "api_command", {"action": action, "success": success})
        
        return jsonify({
            'success': success,
            'message': f'{action.upper()} command sent to {node_id}',
            'node_id': node_id,
            'action': action,
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': time.time()
        }), 500

@app.route('/events')
def events_page():
    """Page to view system events"""
    limit = int(request.args.get('limit', 50))
    events = get_events_with_mock_data(limit)
    return render_template('events.html', events=events)

@app.route('/analytics')
def analytics_page():
    """Analytics and insights page"""
    try:
        # Get system analytics data
        nodes = get_nodes_with_mock_data()
        events = get_events_with_mock_data(100)  # Get more events for analytics
        
        # Calculate basic analytics
        total_commands = len([e for e in events if e.get('event_type') == 'web_command'])
        total_connections = len([e for e in events if e.get('event_type') == 'client_connect'])
        
        analytics_data = {
            'total_commands': total_commands,
            'total_connections': total_connections,
            'nodes': nodes,
            'events': events
        }
        
        return render_template('analytics.html', **analytics_data)
    except Exception as e:
        print(f"Error rendering analytics page: {e}")
        return f"Error loading analytics: {str(e)}", 500

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
