#!/usr/bin/env python3
"""
Start Flask app with MQTT handler in background
"""

import subprocess
import sys
import os
import time

def start_flask_app():
    """Start Flask app in the background"""
    print("🚀 Starting Flask WC System...")
    
    # Change to PC_host directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Start Flask app 
        process = subprocess.Popen([
            sys.executable, "app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        print(f"📡 Flask app started with PID: {process.pid}")
        print("🔍 Monitoring output...")
        
        # Monitor output for a few seconds
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Flask app is running successfully!")
            print("🌐 You can access the dashboard at: http://localhost:5000")
            print("📊 Debug output will appear in the console")
            
            # Keep monitoring output
            try:
                while True:
                    line = process.stdout.readline()
                    if line:
                        print(line.strip())
                    if process.poll() is not None:
                        break
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping Flask app...")
                process.terminate()
                process.wait()
                print("✅ Flask app stopped")
        else:
            print("❌ Flask app failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_flask_app()
