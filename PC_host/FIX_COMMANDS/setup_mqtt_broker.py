#!/usr/bin/env python3
"""
ESP32 WC System - Complete Mosquitto MQTT Broker Setup
Supports uninstall, reinstall, and proper configuration for ESP32 connectivity
"""

import subprocess
import sys
import os
import time
import shutil

def uninstall_mosquitto():
    """Uninstall existing Mosquitto installation"""
    print("🗑️ Uninstalling existing Mosquitto installation...")
    
    try:
        # Stop mosquitto service first
        print("🛑 Stopping Mosquitto service...")
        subprocess.run(['net', 'stop', 'mosquitto'], capture_output=True)
        subprocess.run(['sc', 'delete', 'mosquitto'], capture_output=True)
        
        # Try chocolatey uninstall
        try:
            result = subprocess.run(['choco', 'uninstall', 'mosquitto', '-y'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Mosquitto uninstalled via Chocolatey")
                return True
        except FileNotFoundError:
            pass
        
        # Try winget uninstall
        try:
            result = subprocess.run(['winget', 'uninstall', 'Eclipse.Mosquitto'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Mosquitto uninstalled via winget")
                return True
        except FileNotFoundError:
            pass
        
        # Manual cleanup
        mosquitto_paths = [
            "C:\\Program Files\\mosquitto",
            "C:\\Program Files (x86)\\mosquitto",
            "C:\\mosquitto"
        ]
        
        for path in mosquitto_paths:
            if os.path.exists(path):
                try:
                    shutil.rmtree(path)
                    print(f"🗑️ Removed directory: {path}")
                except Exception as e:
                    print(f"⚠️ Could not remove {path}: {e}")
        
        print("✅ Mosquitto cleanup completed")
        return True
        
    except Exception as e:
        print(f"⚠️ Error during uninstall: {e}")
        return False

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

def create_esp32_config():
    """Create ESP32-compatible Mosquitto configuration"""
    config_content = """# ESP32 WC System - Mosquitto Configuration
# Allow connections from ESP32 devices

# Listen on all interfaces (0.0.0.0) on port 1883
listener 1883 0.0.0.0

# Allow anonymous connections (no authentication required)
allow_anonymous true

# Log to console with debug info
log_dest stdout
log_type all

# Disable persistence for simplicity
persistence false

# Allow retained messages
retain_available true

# Set maximum message size (for ESP32 compatibility)
message_size_limit 8192
"""
    return config_content

def setup_mosquitto_service():
    """Setup Mosquitto as Windows service with ESP32 config"""
    print("🔧 Setting up Mosquitto service with ESP32 configuration...")
    
    try:
        # Check if mosquitto is installed
        result = subprocess.run(['mosquitto', '-h'], capture_output=True, text=True)
        if result.returncode != 0:
            raise FileNotFoundError()
        
        # Create configuration file
        config_path = "C:\\Program Files\\mosquitto\\mosquitto_esp32.conf"
        config_content = create_esp32_config()
        
        try:
            with open(config_path, 'w') as f:
                f.write(config_content)
            print(f"✅ Created ESP32 config: {config_path}")
        except PermissionError:
            # Try alternative location
            config_path = "mosquitto_esp32.conf"
            with open(config_path, 'w') as f:
                f.write(config_content)
            print(f"✅ Created ESP32 config: {os.path.abspath(config_path)}")
        
        # Install as Windows service
        print("🔧 Installing Mosquitto as Windows service...")
        service_cmd = [
            'mosquitto', 
            'install',
            '-c', config_path
        ]
        
        result = subprocess.run(service_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Mosquitto service installed successfully")
        else:
            print(f"⚠️ Service install result: {result.stderr}")
        
        # Start the service
        print("🚀 Starting Mosquitto service...")
        result = subprocess.run(['net', 'start', 'mosquitto'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Mosquitto service started successfully")
            return True
        else:
            print(f"⚠️ Service start result: {result.stderr}")
            # Try starting manually
            return start_mosquitto_manual(config_path)
            
    except FileNotFoundError:
        print("❌ Mosquitto not found - need to install first")
        return False
    except Exception as e:
        print(f"❌ Error setting up service: {e}")
        return False

def start_mosquitto_manual(config_path=None):
    """Start mosquitto manually with ESP32 configuration"""
    try:
        print("🦟 Starting Mosquitto MQTT broker manually...")
        print("📡 MQTT broker will listen on 0.0.0.0:1883 (all interfaces)")
        
        if config_path and os.path.exists(config_path):
            cmd = ['mosquitto', '-c', config_path, '-v']
            print(f"📋 Using config: {config_path}")
        else:
            # Use inline configuration for ESP32 compatibility
            cmd = [
                'mosquitto',
                '-p', '1883',           # Port 1883
                '-v',                   # Verbose
                '--bind-address', '0.0.0.0'  # Listen on all interfaces
            ]
            print("📋 Using inline ESP32-compatible configuration")
        
        process = subprocess.Popen(cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True)
        
        print("🔄 Mosquitto is starting...")
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Mosquitto MQTT broker started successfully!")
            print("📡 ESP32 can now connect to 192.168.100.121:1883")
            print("🔄 Press Ctrl+C to stop")
            
            # Monitor output
            for line in process.stdout:
                print(f"🦟 {line.strip()}")
        else:
            print("❌ Mosquitto failed to start")
            return False
            
    except KeyboardInterrupt:
        print("🛑 Stopping MQTT broker...")
        if process:
            process.terminate()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting mosquitto: {e}")
        return False

def test_mqtt_connectivity():
    """Test MQTT broker connectivity for ESP32"""
    print("🧪 Testing MQTT connectivity for ESP32...")
    
    try:
        import socket
        
        # Test socket connection to 0.0.0.0:1883
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        # Test localhost
        try:
            sock.connect(('127.0.0.1', 1883))
            sock.close()
            print("✅ MQTT broker reachable on localhost:1883")
        except:
            print("❌ MQTT broker NOT reachable on localhost:1883")
            return False
        
        # Test external IP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            sock.connect(('192.168.100.121', 1883))
            sock.close()
            print("✅ MQTT broker reachable on 192.168.100.121:1883")
            print("🎉 ESP32 should be able to connect!")
            return True
        except:
            print("❌ MQTT broker NOT reachable on 192.168.100.121:1883")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connectivity: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 ESP32 WC System - Complete MQTT Broker Setup")
    print("="*60)
    
    # Check if mosquitto is already installed
    try:
        result = subprocess.run(['mosquitto', '-h'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Mosquitto is already installed")
        else:
            raise FileNotFoundError()
    except FileNotFoundError:
        print("🔧 Mosquitto not found - installing now...")
        if not install_mosquitto():
            print("❌ Failed to install Mosquitto")
            return False
    
    print("\n" + "="*60)
    
    # Setup and start mosquitto
    print("🔧 Setting up Mosquitto for ESP32 connectivity...")
    
    # Try service setup first
    if setup_mosquitto_service():
        print("✅ Mosquitto service setup completed")
    else:
        print("🔄 Service setup failed, trying manual start...")
        start_mosquitto_manual()
    
    print("\n" + "="*60)
    
    # Test connectivity
    time.sleep(3)  # Wait for mosquitto to fully start
    test_mqtt_connectivity()

if __name__ == "__main__":
    main()
