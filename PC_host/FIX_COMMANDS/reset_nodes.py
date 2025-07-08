#!/usr/bin/env python3
"""
Reset database with proper WC nodes
"""

import sqlite3
import os
import time

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'wc_system.db')

def reset_nodes():
    """Reset nodes table with actual WC nodes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clear existing nodes
    cursor.execute('DELETE FROM nodes')
    
    # Add real WC nodes based on ESP32 configuration
    real_nodes = [
        {
            'id': 'wc_male_01',
            'name': 'Room 1 (Male WC)',
            'location': 'Floor 1',
            'status': 'offline',
            'last_seen': 0,
            'data': '{"node_type": "male", "room_name": "Room 1"}'
        },
        {
            'id': 'wc_male_02', 
            'name': 'Room 2 (Male WC)',
            'location': 'Floor 1',
            'status': 'offline',
            'last_seen': 0,
            'data': '{"node_type": "male", "room_name": "Room 2"}'
        },
        {
            'id': 'wc_female_01',
            'name': 'Room 3 (Female WC)', 
            'location': 'Floor 1',
            'status': 'offline',
            'last_seen': 0,
            'data': '{"node_type": "female", "room_name": "Room 3"}'
        }
    ]
    
    # Insert real nodes
    for node in real_nodes:
        cursor.execute('''
            INSERT INTO nodes (id, name, location, status, last_seen, data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (node['id'], node['name'], node['location'], node['status'], node['last_seen'], node['data']))
    
    conn.commit()
    print(f"✅ Reset database with {len(real_nodes)} real WC nodes:")
    for node in real_nodes:
        print(f"   - {node['id']}: {node['name']}")
    
    # Clear old events from test nodes
    cursor.execute("DELETE FROM events WHERE node_id NOT IN ('wc_male_01', 'wc_male_02', 'wc_female_01')")
    deleted_events = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"✅ Cleaned up {deleted_events} old test events")

if __name__ == "__main__":
    print("🔄 Resetting database with real WC nodes...")
    reset_nodes()
    print("✅ Database reset completed!")
