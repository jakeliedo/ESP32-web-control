#!/usr/bin/env python3
"""
Check database schema and add missing columns
"""

import sqlite3
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DB_PATH

def check_and_update_schema():
    """Check and update database schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check current schema
    cursor.execute("PRAGMA table_info(nodes)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    # Add node_type column if missing
    if 'node_type' not in columns:
        print("Adding node_type column...")
        cursor.execute("ALTER TABLE nodes ADD COLUMN node_type TEXT DEFAULT 'male'")
        print("✅ Added node_type column")
    
    # Update node names and types
    updates = [
        ('wc_male_01', 'Room1', 'male'),
        ('wc_male_02', 'Room2', 'male'), 
        ('wc_female_01', 'Room1', 'female')
    ]
    
    for node_id, name, node_type in updates:
        cursor.execute('''
            UPDATE nodes 
            SET name = ?, node_type = ?
            WHERE id = ?
        ''', (name, node_type, node_id))
        print(f"✅ Updated {node_id}: {name} ({node_type})")
    
    # Show final result
    cursor.execute("SELECT id, name, node_type, status FROM nodes")
    nodes = cursor.fetchall()
    print("\n📋 Current nodes:")
    for node in nodes:
        print(f"   - {node[0]}: {node[1]} ({node[2]}) - {node[3]}")
    
    conn.commit()
    conn.close()
    print("\n🎉 Database schema and names updated successfully!")

if __name__ == "__main__":
    check_and_update_schema()
