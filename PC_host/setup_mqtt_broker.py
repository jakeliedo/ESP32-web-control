#!/usr/bin/env python3
"""
Install and run Mosquitto MQTT broker using Python
"""

import subprocess
import sys
import os
import time

def install_mosquitto():
    """Install mosquitto using package manager"""
    print("🔧 Installing Mosquitto MQTT broker...")
    
    try:
        # Try chocolatey first (Windows)
        result = subprocess.run(['choco', 'install', 'mosquitto', '-y'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Mosquitto installed via Chocolatey")
            return True
    except FileNotFoundError:
        pass
    
    try:
        # Try winget (Windows)
        result = subprocess.run(['winget', 'install', 'Eclipse.Mosquitto'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Mosquitto installed via winget")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Could not install Mosquitto automatically")
    print("📋 Please install manually from: https://mosquitto.org/download/")
    print("   Or run: choco install mosquitto")
    return False

def start_mosquitto():
    """Start mosquitto MQTT broker"""
    try:
        # Check if mosquitto is available
        result = subprocess.run(['mosquitto', '-h'], capture_output=True, text=True)
        if result.returncode != 0:
            raise FileNotFoundError()
            
        print("🦟 Starting Mosquitto MQTT broker on port 1883...")
        print("📡 MQTT broker will listen on 192.168.1.181:1883")
        
        # Start mosquitto with verbose output
        process = subprocess.Popen(['mosquitto', '-p', '1883', '-v'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True)
        
        # Monitor output
        for line in process.stdout:
            print(f"🦟 {line.strip()}")
            if "mosquitto version" in line.lower():
                print("✅ Mosquitto MQTT broker started successfully!")
            
    except FileNotFoundError:
        print("❌ Mosquitto not found")
        return install_mosquitto()
    except KeyboardInterrupt:
        print("🛑 Stopping MQTT broker...")
        if process:
            process.terminate()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting mosquitto: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ESP32 WC System - MQTT Broker Setup")
    print("="*50)
    start_mosquitto()
