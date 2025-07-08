#!/usr/bin/env python3
"""
Fix Mosquitto ESP32 connectivity - Simple solution
"""

import subprocess
import os
import time

def fix_mosquitto_esp32():
    """Fix Mosquitto to allow ESP32 connections"""
    print("🔧 Fixing Mosquitto for ESP32 connectivity...")
    
    # Step 1: Stop any running mosquitto
    print("🛑 Stopping any running Mosquitto processes...")
    try:
        subprocess.run(['taskkill', '/f', '/im', 'mosquitto.exe'], capture_output=True)
        subprocess.run(['net', 'stop', 'mosquitto'], capture_output=True)
        time.sleep(2)
    except:
        pass
    
    # Step 2: Create simple ESP32 config
    config_content = """# ESP32 WC System - Mosquitto Configuration
# Simple configuration for ESP32 connectivity

# Listen on all interfaces, port 1883
listener 1883 0.0.0.0

# Allow anonymous connections
allow_anonymous true

# Basic logging
log_dest console
log_type error
log_type warning
log_type notice
log_type information

# No persistence
persistence false

# Allow retained messages
retain_available true

# ESP32 compatibility settings
message_size_limit 8192
keepalive_interval 60
"""
    
    # Try to write config to Program Files first
    config_locations = [
        "C:\\Program Files\\mosquitto\\mosquitto.conf",
        "mosquitto_esp32.conf"
    ]
    
    config_path = None
    for location in config_locations:
        try:
            with open(location, 'w', encoding='utf-8') as f:
                f.write(config_content)
            config_path = location
            print(f"✅ Created config: {location}")
            break
        except PermissionError:
            continue
        except Exception as e:
            print(f"⚠️ Failed to create {location}: {e}")
            continue
    
    if not config_path:
        print("❌ Could not create configuration file")
        return False
    
    # Step 3: Add Windows Firewall rule
    print("🔥 Adding Windows Firewall rule for port 1883...")
    firewall_cmd = [
        'netsh', 'advfirewall', 'firewall', 'add', 'rule',
        'name=MQTT ESP32', 'dir=in', 'action=allow', 'protocol=TCP', 'localport=1883'
    ]
    
    try:
        result = subprocess.run(firewall_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Windows Firewall rule added")
        else:
            print(f"⚠️ Firewall rule failed: {result.stderr}")
    except Exception as e:
        print(f"⚠️ Could not add firewall rule: {e}")
    
    # Step 4: Start Mosquitto manually
    print("🦟 Starting Mosquitto manually...")
    
    try:
        # Try to start mosquitto
        cmd = ['mosquitto', '-c', config_path, '-v']
        print(f"🔧 Command: {' '.join(cmd)}")
        
        # Start in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        print("⏱️ Waiting for Mosquitto to start...")
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Mosquitto started successfully!")
            return True
        else:
            print("❌ Mosquitto failed to start")
            # Try to read output
            try:
                output, _ = process.communicate(timeout=1)
                print(f"Error output: {output}")
            except:
                pass
            return False
            
    except FileNotFoundError:
        print("❌ mosquitto.exe not found")
        print("💡 Please install Mosquitto first:")
        print("   - Download from https://mosquitto.org/download/")
        print("   - Or run: choco install mosquitto")
        return False
    except Exception as e:
        print(f"❌ Error starting Mosquitto: {e}")
        return False

def test_connection():
    """Test if MQTT is working"""
    print("🧪 Testing MQTT connectivity...")
    
    import socket
    
    # Test local connection
    try:
        sock = socket.socket()
        sock.settimeout(3)
        sock.connect(('127.0.0.1', 1883))
        sock.close()
        print("✅ localhost:1883 - OK")
    except Exception as e:
        print(f"❌ localhost:1883 - FAILED: {e}")
        return False
    
    # Test external connection
    try:
        sock = socket.socket()
        sock.settimeout(3)
        sock.connect(('192.168.100.121', 1883))
        sock.close()
        print("✅ 192.168.100.121:1883 - OK")
        print("🎉 ESP32 can now connect!")
        return True
    except Exception as e:
        print(f"❌ 192.168.100.121:1883 - FAILED: {e}")
        return False

def check_ports():
    """Check what's listening on port 1883"""
    print("📊 Checking ports...")
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if '1883' in line and 'LISTENING' in line:
                print(f"  {line.strip()}")
                return True
        print("  No process listening on port 1883")
        return False
    except:
        print("  Could not check ports")
        return False

if __name__ == "__main__":
    print("🚀 ESP32 MQTT Connectivity Fix")
    print("=" * 40)
    
    success = fix_mosquitto_esp32()
    
    print("\n" + "=" * 40)
    
    if success:
        time.sleep(2)
        check_ports()
        print("\n" + "=" * 40)
        test_connection()
    else:
        print("❌ Failed to start Mosquitto")
        print("\n💡 Manual steps:")
        print("1. Open PowerShell as Administrator")
        print("2. Run: mosquitto -c mosquitto_esp32.conf -v")
        print("3. Check Windows Firewall settings")
