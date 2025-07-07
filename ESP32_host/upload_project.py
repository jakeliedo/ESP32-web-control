#!/usr/bin/env python3
"""
ESP32 Remote Control - Project Upload Script
Automatically uploads all project files to ESP32 via serial connection
"""

import os
import sys
import time
import serial.tools.list_ports
from pathlib import Path

# Configuration
DEFAULT_BAUDRATE = 115200
UPLOAD_DELAY = 0.5  # Delay between file uploads

# Files to upload (in order)
FILES_TO_UPLOAD = [
    # Libraries first
    ("lib/umqtt/simple.py", "lib/umqtt/simple.py"),
    ("lib/st7789p3.py", "lib/st7789p3.py"), 
    ("lib/simple_ui.py", "lib/simple_ui.py"),
    ("lib/remote_control.py", "lib/remote_control.py"),
    
    # Configuration
    ("config.py", "config.py"),
    
    # Boot files
    ("boot.py", "boot.py"),
    
    # Main application (last)
    ("main.py", "main.py"),
    
    # Optional files
    ("test_system.py", "test_system.py"),
]

def find_esp32_port():
    """Find ESP32 serial port automatically"""
    print("🔍 Scanning for ESP32...")
    
    ports = serial.tools.list_ports.comports()
    esp32_ports = []
    
    for port in ports:
        # Common ESP32 identifiers
        if any(keyword in port.description.upper() for keyword in 
               ['USB', 'SERIAL', 'CP210', 'CH340', 'FTDI']):
            esp32_ports.append(port.device)
            print(f"   Found potential ESP32: {port.device} - {port.description}")
    
    if not esp32_ports:
        print("❌ No ESP32 found. Please check connection.")
        return None
    
    # Return first found port
    selected_port = esp32_ports[0]
    print(f"✅ Selected port: {selected_port}")
    return selected_port

def check_ampy():
    """Check if ampy is installed and working"""
    try:
        import subprocess
        result = subprocess.run(['ampy', '--help'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def upload_file_ampy(port, local_path, remote_path):
    """Upload file using ampy"""
    import subprocess
    
    # Create remote directory if needed
    remote_dir = os.path.dirname(remote_path)
    if remote_dir and remote_dir != '.':
        try:
            subprocess.run(['ampy', '--port', port, 'mkdir', remote_dir], 
                         capture_output=True, check=False)
        except:
            pass  # Directory might already exist
    
    # Upload file
    cmd = ['ampy', '--port', port, 'put', local_path, remote_path]
    
    print(f"📤 Uploading {local_path} -> {remote_path}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"   ✅ Success")
            return True
        else:
            print(f"   ❌ Failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def upload_file_manual_instructions(local_path, remote_path):
    """Show manual upload instructions"""
    print(f"📋 Manual upload needed:")
    print(f"   Local:  {local_path}")
    print(f"   Remote: {remote_path}")
    print(f"   Use Thonny or VS Code to upload this file")

def verify_files_exist():
    """Verify all files exist before upload"""
    print("🔍 Verifying project files...")
    
    missing_files = []
    for local_path, remote_path in FILES_TO_UPLOAD:
        if not os.path.exists(local_path):
            missing_files.append(local_path)
            print(f"   ❌ Missing: {local_path}")
        else:
            print(f"   ✅ Found: {local_path}")
    
    if missing_files:
        print(f"\n❌ {len(missing_files)} files missing. Please create them first.")
        return False
    
    print(f"✅ All {len(FILES_TO_UPLOAD)} files found")
    return True

def main():
    """Main upload process"""
    print("=" * 60)
    print("ESP32 Remote Control - Project Upload")
    print("=" * 60)
    
    # Check project files
    if not verify_files_exist():
        return False
    
    # Find ESP32 port
    port = find_esp32_port()
    if not port:
        print("\n❌ Cannot find ESP32. Please:")
        print("   1. Connect ESP32 via USB")
        print("   2. Install ESP32 drivers")
        print("   3. Check Device Manager (Windows)")
        return False
    
    # Check ampy tool
    if not check_ampy():
        print("\n❌ ampy not installed or not working")
        print("Install with: pip install adafruit-ampy")
        print("\nAlternative: Upload files manually with Thonny or VS Code")
        
        # Show manual instructions
        print("\n📋 Manual Upload Instructions:")
        for local_path, remote_path in FILES_TO_UPLOAD:
            upload_file_manual_instructions(local_path, remote_path)
        return False
    
    print(f"\n🚀 Starting upload to {port}...")
    
    # Upload files
    success_count = 0
    failed_files = []
    
    for i, (local_path, remote_path) in enumerate(FILES_TO_UPLOAD, 1):
        print(f"\n[{i}/{len(FILES_TO_UPLOAD)}]", end=" ")
        
        if upload_file_ampy(port, local_path, remote_path):
            success_count += 1
        else:
            failed_files.append((local_path, remote_path))
        
        # Small delay between uploads
        time.sleep(UPLOAD_DELAY)
    
    # Results
    print("\n" + "=" * 60)
    print("📊 Upload Results:")
    print(f"   ✅ Successful: {success_count}/{len(FILES_TO_UPLOAD)}")
    print(f"   ❌ Failed: {len(failed_files)}")
    
    if failed_files:
        print("\n❌ Failed files:")
        for local_path, remote_path in failed_files:
            print(f"   - {local_path}")
        print("\nTry uploading failed files manually with Thonny")
        return False
    
    print("\n🎉 All files uploaded successfully!")
    print("\nNext steps:")
    print("1. Configure WiFi and MQTT in config.py")
    print("2. Reset ESP32 to start the application")
    print("3. Monitor serial output for debug info")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Upload cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
