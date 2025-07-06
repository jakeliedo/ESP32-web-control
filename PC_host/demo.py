#!/usr/bin/env python3
"""
Demo script to showcase the new WC Control System UI
This will start the Flask app and display the URLs for testing
"""

import sys
import os
import time
import webbrowser
from threading import Timer

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def open_browser():
    """Open browser after a delay to allow Flask to start"""
    time.sleep(2)
    print("\n🌐 Opening browser windows...")
    webbrowser.open('http://localhost:5000')
    print("✅ Dashboard opened in browser")
    
    time.sleep(1)
    webbrowser.open('http://localhost:5000/events')
    print("✅ Events page opened in browser")
    
    time.sleep(1)
    webbrowser.open('http://localhost:5000/analytics')
    print("✅ Analytics page opened in browser")

def main():
    print("🚀 WC Control System v2.0 Demo")
    print("=" * 50)
    print("📱 Modern UI Features:")
    print("  • Dark/Light theme toggle")
    print("  • Real-time WebSocket updates")
    print("  • Interactive charts and analytics")
    print("  • Enhanced mobile-responsive design")
    print("  • Advanced event filtering and export")
    print("  • System health monitoring")
    print()
    
    print("🔗 Available URLs:")
    print("  • Dashboard:  http://localhost:5000/")
    print("  • Events:     http://localhost:5000/events")
    print("  • Analytics:  http://localhost:5000/analytics")
    print("  • Simple UI:  http://localhost:5000/simple")
    print("  • API Status: http://localhost:5000/api/status")
    print()
    
    print("💡 UI Enhancements:")
    print("  • Statistics cards with real-time updates")
    print("  • Interactive Chart.js visualizations")
    print("  • Advanced event timeline and filtering")
    print("  • Node performance metrics")
    print("  • System health indicators")
    print("  • Enhanced notifications system")
    print()
    
    # Start browser opening timer
    Timer(2.0, open_browser).start()
    
    print("⚡ Starting Flask application...")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Import and run the app
    try:
        from app import app, socketio, HOST, PORT
        socketio.run(app, host=HOST, port=PORT, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install flask flask-socketio requests")

if __name__ == "__main__":
    main()
