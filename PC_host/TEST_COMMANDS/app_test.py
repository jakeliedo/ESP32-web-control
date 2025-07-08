#!/usr/bin/env python3
"""
Simplified version of app.py that works without MQTT broker
For initial testing and development
"""

from flask import Flask, render_template, render_template_string, request, redirect, url_for, jsonify
from flask_socketio import SocketIO
import time
import json

# Import modules
try:
    from config import DEBUG, SECRET_KEY, HOST, PORT
    print(f"✅ Config loaded: {HOST}:{PORT}")
except Exception as e:
    print(f"⚠️ Config error: {e}")
    # Fallback values
    DEBUG = True
    SECRET_KEY = "dev_key_change_in_production"
    HOST = "0.0.0.0"
    PORT = 5000

# Initialize Flask app
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app)

print("✅ Flask app initialized")

# Mock data for testing without MQTT
MOCK_NODES = [
    {
        'node_id': 'wc_male_01',
        'name': 'Room 1',
        'node_type': 'male',
        'status': 'offline',
        'location': 'Floor 1',
        'last_seen': time.time() - 600
    },
    {
        'node_id': 'wc_male_02', 
        'name': 'Room 2',
        'node_type': 'male',
        'status': 'offline',
        'location': 'Floor 1', 
        'last_seen': time.time() - 600
    },
    {
        'node_id': 'wc_female_01',
        'name': 'Room 1', 
        'node_type': 'female',
        'status': 'offline',
        'location': 'Floor 1',
        'last_seen': time.time() - 600
    },
    {
        'node_id': 'wc_female_02',
        'name': 'Room 2',
        'node_type': 'female', 
        'status': 'offline',
        'location': 'Floor 1',
        'last_seen': time.time() - 600
    }
]

# Simple HTML template for testing
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ESP32 WC Control - Test Mode</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; background: #f0f0f0; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { background: white; border-radius: 8px; padding: 20px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .node { display: flex; justify-content: space-between; align-items: center; }
        .btn { background: #007cba; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #005a87; }
        .status { padding: 5px 10px; border-radius: 4px; color: white; }
        .offline { background: #dc3545; }
        .online { background: #28a745; }
        .header { text-align: center; color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="header">🚽 ESP32 WC Control System</h1>
        <p class="header">Test Mode - MQTT Broker Not Connected</p>
        
        {% for node in nodes %}
        <div class="card">
            <div class="node">
                <div>
                    <h3>{{ node.name }} ({{ node.node_type.title() }})</h3>
                    <p>Node ID: {{ node.node_id }}</p>
                    <span class="status {{ node.status }}">{{ node.status.upper() }}</span>
                </div>
                <form method="post" style="display: inline;">
                    <input type="hidden" name="node_id" value="{{ node.node_id }}">
                    <button type="submit" name="action" value="flush" class="btn">FLUSH</button>
                </form>
            </div>
        </div>
        {% endfor %}
        
        <div class="card">
            <h3>🔧 System Info</h3>
            <p>Server: {{ host }}:{{ port }}</p>
            <p>Debug Mode: {{ debug }}</p>
            <p>Time: {{ current_time }}</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    """Main dashboard - test version"""
    if request.method == 'POST':
        node_id = request.form.get('node_id')
        action = request.form.get('action', 'flush')
        
        print(f"🔍 TEST MODE: Received command {action} for node {node_id}")
        print("⚠️ MQTT not connected - command not sent to device")
        
        return redirect(url_for('dashboard'))
    
    # GET request
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    return render_template_string(HTML_TEMPLATE, 
                                nodes=MOCK_NODES,
                                host=HOST,
                                port=PORT, 
                                debug=DEBUG,
                                current_time=current_time)

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "status": "test_mode",
        "mqtt_connected": False,
        "nodes": MOCK_NODES,
        "timestamp": time.time()
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connections"""
    print(f'✅ Client connected from {request.remote_addr}')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnections"""
    print('❌ Client disconnected')

if __name__ == "__main__":
    try:
        print(f"🚀 Starting ESP32 WC Control System (Test Mode)")
        print(f"🌐 Server: http://{HOST}:{PORT}")
        print(f"🔧 Debug: {DEBUG}")
        print("⚠️ MQTT broker not required in test mode")
        print("="*50)
        
        socketio.run(app, host=HOST, port=PORT, debug=DEBUG)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
