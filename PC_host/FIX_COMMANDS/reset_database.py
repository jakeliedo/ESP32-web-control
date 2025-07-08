#!/usr/bin/env python3
"""
Reset the database - remove old node entries so they can be recreated with correct names
"""

import sqlite3
import os

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'wc_system.db')

def reset_database():
    """Remove all existing nodes from database"""
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Delete all nodes
        cursor.execute('DELETE FROM nodes')
        
        # Keep events but show what we're doing
        cursor.execute('SELECT COUNT(*) FROM events')
        event_count = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        print(f"✅ Database reset complete!")
        print(f"   - Deleted all node entries")
        print(f"   - Kept {event_count} event records")
        print(f"   - ESP32 nodes will recreate themselves with correct names")
    else:
        print('❌ Database file not found')

if __name__ == "__main__":
    reset_database()
