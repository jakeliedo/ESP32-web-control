#!/usr/bin/env python3
"""
Update node names in database
"""

import sqlite3
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DB_PATH

def update_node_names():
    """Update node names to match requirements"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Update node names
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
    
    conn.commit()
    conn.close()
    print("\n🎉 Node names updated successfully!")

if __name__ == "__main__":
    update_node_names()
