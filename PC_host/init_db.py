#!/usr/bin/env python3
"""
Initialize database for WC Control System
"""

from database import init_db

if __name__ == "__main__":
    print("🗄️ Initializing WC Control System database...")
    try:
        init_db()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
