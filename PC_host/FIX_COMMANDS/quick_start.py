#!/usr/bin/env python3
"""
Quick start Flask app for testing
"""

print("🚀 Starting Flask app...")

# Start the app
import subprocess
import sys
import os

# Change to the correct directory
os.chdir(r"b:\Python\MicroPython\ESP_WC_System\PC_host")

# Start Flask app
try:
    result = subprocess.run([sys.executable, "app.py"], 
                          capture_output=False, 
                          text=True, 
                          timeout=None)
except KeyboardInterrupt:
    print("\n⏹️ Flask app stopped")
except Exception as e:
    print(f"❌ Error starting Flask app: {e}")
