import sqlite3
import json
import time
import os

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'wc_system.db')

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    """Initialize database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create nodes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS nodes (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        location TEXT,
        status TEXT DEFAULT 'offline',
        last_seen REAL DEFAULT 0,
        data TEXT
    )
    ''')
    
    # Create events table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        node_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        data TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on module import
init_db()

# Rest of your database functions...
def get_all_nodes():
    """Get all WC nodes from database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM nodes')
    nodes = [dict(row) for row in cursor.fetchall()]
    
    # Parse JSON data
    for node in nodes:
        if node.get('data'):
            try:
                node['data'] = json.loads(node['data'])
            except:
                node['data'] = {}
    
    conn.close()
    return nodes

def update_node_status(node_id, status, data=None):
    """Update node status and last seen timestamp"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if node exists
    cursor.execute('SELECT id FROM nodes WHERE id = ?', (node_id,))
    if cursor.fetchone() is None:
        # Create new node
        cursor.execute(
            'INSERT INTO nodes (id, name, location, status, last_seen, data) VALUES (?, ?, ?, ?, ?, ?)',
            (node_id, f'Node {node_id}', 'Unknown', status, time.time(), '{}')
        )
    
    # Update node status
    last_seen = time.time()
    
    if data:
        data_json = json.dumps(data)
        cursor.execute(
            'UPDATE nodes SET status = ?, last_seen = ?, data = ? WHERE id = ?',
            (status, last_seen, data_json, node_id)
        )
    else:
        cursor.execute(
            'UPDATE nodes SET status = ?, last_seen = ? WHERE id = ?',
            (status, last_seen, node_id)
        )
    
    conn.commit()
    conn.close()
    return True

def log_event(node_id, event_type, data=None):
    """Log an event in the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = time.time()
    data_json = json.dumps(data) if data else '{}'
    
    cursor.execute(
        'INSERT INTO events (timestamp, node_id, event_type, data) VALUES (?, ?, ?, ?)',
        (timestamp, node_id, event_type, data_json)
    )
    
    conn.commit()
    conn.close()
    return cursor.lastrowid

def get_recent_events(limit=50):
    """Get recent events from the database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM events ORDER BY timestamp DESC LIMIT ?', (limit,))
    events = [dict(row) for row in cursor.fetchall()]
    
    # Parse JSON data
    for event in events:
        if event.get('data'):
            try:
                event['data'] = json.loads(event['data'])
            except:
                event['data'] = {}
    
    conn.close()
    return events