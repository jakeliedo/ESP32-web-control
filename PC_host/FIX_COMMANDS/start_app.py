#!/usr/bin/env python3
"""
Start Flask app with debug monitoring
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Flask app
from app import app, socketio

if __name__ == "__main__":
    print("🚀 Starting WC Control System...")
    print("📡 MQTT Handler will be initialized...")
    print("🌐 Web interface will be available at: http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000")
    print("⚡ Simple UI: http://localhost:5000/simple")
    print("📋 Events: http://localhost:5000/events")
    print("\n" + "="*60)
    
    # Start the Flask app with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
