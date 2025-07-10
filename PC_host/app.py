from flask import Flask, render_template, render_template_string, request, redirect, url_for, jsonify, flash
from flask_socketio import SocketIO
import threading
import time
import json
import os
import uuid
import requests
from collections import deque

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
        .hide-group { margin-right: 20px !important; gap: 2px !important; }
        .hide-group label { margin-left: 1px !important; font-size: 1rem; }
        .inline-row { flex-direction: row; align-items: center; gap: 12px; }
        /* Đảm bảo checkbox và label HIDE sát nhau, nhóm này sát lề phải nhưng không quá xa */
    }
    .hide-group input[type="checkbox"] {
        width: 18px;
        height: 18px;
        margin: 0;
    }
    .hide-group label {
        margin-left: 10px;
        font-size: 1.08rem;
    }
    /* Đảm bảo .hide-group luôn nằm sát lề phải, checkbox và label gần nhau, đẹp trên cả desktop và mobile */
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
        'node_id': 'wc1',
        'name': 'Room 1',
        'node_type': 'male',
        'status': 'offline',  # Mock data shows offline until real devices connect
        'location': 'Floor 1',
        'last_seen': time.time() - 600  # 10 minutes ago
    },
    {
        'node_id': 'wc2', 
        'name': 'Room 2',
        'node_type': 'male',
        'status': 'offline',  # Mock data shows offline until real devices connect
        'location': 'Floor 1', 
        'last_seen': time.time() - 600  # 10 minutes ago
    },
    {
        'node_id': 'wc3',
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
        'node_id': 'wc1',
        'event_type': 'web_command',
        'data': {'action': 'flush', 'success': True, 'ui': 'dashboard'}
    },
    {
        'id': 2, 
        'timestamp': time.time() - 180,
        'node_id': 'wc2',
        'event_type': 'sensor_trigger',
        'data': {'sensor': 'motion', 'value': True}
    },
    {
        'id': 3,
        'timestamp': time.time() - 300,
        'node_id': 'wc3',
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
        'node_id': 'wc1',
        'event_type': 'status_change',
        'data': {'old_status': 'offline', 'new_status': 'online'}
    }
]

def get_nodes_with_mock_data():
    """Get nodes from config/devices.json (admin UI), fallback to database or mock data if empty."""
    try:
        admin_nodes = load_admin_nodes()
        current_time = time.time()
        db_nodes_raw = get_all_nodes() or []
        db_nodes = {n.get('node_id') or n.get('id'): n for n in db_nodes_raw}
        result = []
        if admin_nodes and len(admin_nodes) > 0:
            for n in admin_nodes:
                if n.get('hide', False):
                    continue  # skip hidden nodes
                node_id = n.get('node_id')
                db_node = db_nodes.get(node_id, {})
                last_seen = db_node.get('last_seen', 0)
                # Nếu không có last_seen hoặc không có database, luôn offline
                if not db_nodes_raw or not last_seen or last_seen == 0:
                    status = 'offline'
                else:
                    time_since_seen = current_time - last_seen
                    status = 'online' if time_since_seen < 30 else 'offline'
                result.append({
                    'node_id': node_id,
                    'node_type': n.get('node_type', 'unknown'),
                    'name': n.get('name', 'Room'),
                    'status': status,
                    'last_seen': last_seen
                })
            return result
        # Nếu không có file config, fallback sang database
        if db_nodes_raw and len(db_nodes_raw) > 0:
            nodes = []
            for node in db_nodes_raw:
                node_id = node.get('node_id') or node.get('id')
                last_seen = node.get('last_seen', 0)
                if not last_seen or last_seen == 0:
                    status = 'offline'
                else:
                    time_since_seen = current_time - last_seen
                    status = 'online' if time_since_seen < 30 else 'offline'
                nodes.append({
                    'node_id': node_id,
                    'node_type': node.get('node_type', 'unknown'),
                    'name': node.get('name', 'Room'),
                    'status': status,
                    'last_seen': last_seen
                })
            return nodes
        # Fallback mock
        print("⚠️ No nodes found in config or database - Using MOCK data (all offline)")
        return MOCK_NODES
    except Exception as e:
        print(f"❌ Error getting nodes, using mock data: {e}")
        return MOCK_NODES

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

# --- Simple UI: Track recent commands for status lines ---
# Lưu 3 lệnh FLUSH gần nhất cho simple UI
recent_commands = deque(maxlen=3)

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
                
                # Nếu là lệnh FLUSH thì lưu lại
                if action.lower() == "flush" or action.endswith("_on"):
                    now_str = time.strftime('%H:%M:%S', time.localtime())
                    recent_commands.appendleft(f"FLUSH sent to {node_id} ({now_str})")
                
            except Exception as e:
                print(f"❌ Error in simple UI control: {e}")
        else:
            print(f"⚠️ Simple UI: No node_id received in form data")
        
        return redirect("/simple")
    
    # GET request - show the simple UI
    try:
        nodes = get_nodes_with_mock_data()
        print(f"🔍 Simple UI rendering: Found {len(nodes)} nodes")
        # Status lines: 3 lệnh FLUSH gần nhất + 1 dòng thời gian
        status_lines = list(recent_commands)
        status_lines.append(f"Time: {time.strftime('%H:%M:%S', time.localtime())}")
        return render_template('simple.html', nodes=nodes, status_lines=status_lines)
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

# --- Admin Node Management UI ---
ADMIN_NODES_JSON = os.path.join(os.path.dirname(__file__), 'config', 'devices.json')

def load_admin_nodes():
    if os.path.exists(ADMIN_NODES_JSON):
        with open(ADMIN_NODES_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_admin_nodes(nodes):
    os.makedirs(os.path.dirname(ADMIN_NODES_JSON), exist_ok=True)
    with open(ADMIN_NODES_JSON, 'w', encoding='utf-8') as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)

@app.route('/nodes', methods=['GET', 'POST'])
def manage_nodes():
    real_nodes = get_all_nodes() or []
    node_ids = []
    for n in real_nodes:
        nid = n.get('node_id') or n.get('id')
        if nid and nid not in node_ids:
            node_ids.append(nid)
    if not node_ids:
        for n in load_admin_nodes():
            nid = n.get('node_id')
            if nid and nid not in node_ids:
                node_ids.append(nid)
    nodes = load_admin_nodes()
    if request.method == 'POST':
        node_id = request.form.get('node_id', '').strip()
        node_type = request.form.get('node_type', 'male')
        name = request.form.get('name', 'Room').strip() or 'Room'
        hide = request.form.get('hide', 'off') == 'on'
        if not node_id:
            flash('Node ID is required!', 'danger')
        else:
            found = False
            for n in nodes:
                if n['node_id'] == node_id:
                    n['node_type'] = node_type
                    n['name'] = name
                    n['hide'] = hide
                    found = True
                    break
            if not found:
                nodes.append({'node_id': node_id, 'node_type': node_type, 'name': name, 'hide': hide})
            save_admin_nodes(nodes)
            flash(f'Node {node_id} saved.', 'success')
        return redirect(url_for('manage_nodes'))
    # GET
    html = '''
    <!DOCTYPE html>
    <html><head><title>Node Management</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    body { background: #222; color: #fff; font-family: Arial; }
    .container { max-width: 500px; margin: 32px auto; background: #333; border-radius: 12px; padding: 24px; }
    input, select { width: 100%; padding: 8px; margin: 8px 0 16px 0; border-radius: 6px; border: none; }
    button { padding: 10px 24px; border-radius: 6px; border: none; background: #4caf50; color: #fff; font-weight: bold; cursor: pointer; }
    table { width: 95%; margin: 24px auto 0 auto; border-collapse: collapse; background: #222; border-radius: 10px; box-shadow: 0 2px 12px #0004; font-size: 1.05rem; }
    th, td { padding: 10px 8px; border-bottom: 1px solid #444; text-align: left; }
    th { background: #2a2a2a; }
    tr:last-child td { border-bottom: none; }
    tr:hover { background: #444; }
    /* Đảm bảo bảng danh sách cân đối với card, cùng max-width, căn giữa và padding hợp lý */
    .success { color: #8f8; }
    .danger { color: #f88; }
    .inline-row { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
    .short-select { width: 90px; min-width: 60px; }
    .short-input { width: 90px; min-width: 60px; }
    .hide-group { margin-left: auto; display: flex; align-items: center; gap: 2px; margin-right: 20px; }
    @media (max-width: 600px) {
      .container { width: 95%; padding: 16px; }
      input, select { padding: 12px; }
      button { width: 100%; }
      .inline-row { flex-direction: row; align-items: center; gap: 12px; }
      .hide-group { margin-right: 20px !important; gap: 2px !important; }
      .hide-group label { margin-left: 1px !important; font-size: 1rem; }
      .short-select, .short-input { width: 100%; }
    }
    </style></head><body>
    <div class="container">
    <h2>Node Management</h2>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="{{ category }}">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}
    <form method="post">
      <div class="inline-row">
        <label for="node_id" style="margin:0;">Node ID:</label>
        <select name="node_id" id="node_id" class="short-select" required>
          <option value="">Select</option>
          {% for nid in node_ids %}
            <option value="{{nid}}">{{nid}}</option>
          {% endfor %}
        </select>
        <div class="hide-group" style="margin-left:8px;">
          <input type="checkbox" name="hide" id="hide">
          <label for="hide" style="margin:0 0 0 2px;">HIDE</label>
        </div>
      </div>
      <div class="inline-row">
        <label for="node_type" style="margin:0;">Type:</label>
        <select name="node_type" id="node_type" class="short-select">
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="other">Other</option>
        </select>
        <label for="name" style="margin:0 0 0 12px;">Room:</label>
        <input name="name" id="name" class="short-input" placeholder="e.g. 1">
      </div>
      <button type="submit">Add / Update</button>
    </form>
    <h3>Node List</h3>
    <table><tr><th>ID</th><th>Type</th><th>Room Name</th><th>Hide</th></tr>
    {% for n in nodes %}
      <tr><td>{{n.node_id}}</td><td>{{n.node_type}}</td><td>{{n.name}}</td><td>{{'Yes' if n.hide else ''}}</td></tr>
    {% endfor %}
    </table>
    </div></body></html>
    '''
    return render_template_string(html, nodes=nodes, node_ids=node_ids)

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
