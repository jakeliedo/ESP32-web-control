#!/usr/bin/env python3
"""
Setup Mosquitto as Windows Service for ESP32 connectivity
"""

import subprocess
import os
import time

def setup_mosquitto_windows_service():
    """Setup Mosquitto as Windows Service với cấu hình ESP32"""
    print("🔧 Cài đặt Mosquitto như Windows Service...")
    
    # Kiểm tra quyền Administrator
    try:
        # Test admin privileges
        result = subprocess.run(['net', 'session'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Cần chạy với quyền Administrator!")
            print("💡 Hãy mở PowerShell/Terminal với 'Run as Administrator'")
            return False
    except:
        print("⚠️ Không thể kiểm tra quyền Administrator")
    
    # Tìm đường dẫn Mosquitto
    mosquitto_paths = [
        "C:\\Program Files\\mosquitto\\mosquitto.exe",
        "C:\\Program Files (x86)\\mosquitto\\mosquitto.exe",
        "C:\\mosquitto\\mosquitto.exe"
    ]
    
    mosquitto_exe = None
    mosquitto_dir = None
    
    for path in mosquitto_paths:
        if os.path.exists(path):
            mosquitto_exe = path
            mosquitto_dir = os.path.dirname(path)
            break
    
    if not mosquitto_exe:
        print("❌ Không tìm thấy mosquitto.exe")
        print("💡 Hãy cài đặt Mosquitto trước: choco install mosquitto")
        return False
    
    print(f"✅ Tìm thấy Mosquitto: {mosquitto_exe}")
    print(f"📁 Thư mục: {mosquitto_dir}")
    
    # Tạo cấu hình ESP32
    config_content = """# ESP32 WC System - Mosquitto Service Configuration
# Cấu hình cho phép ESP32 kết nối

# Lắng nghe trên tất cả interfaces, port 1883
listener 1883 0.0.0.0

# Cho phép kết nối ẩn danh (không cần xác thực)
allow_anonymous true

# Log cho Windows Service
log_dest file C:\\ProgramData\\mosquitto\\mosquitto.log
log_type error
log_type warning  
log_type notice
log_type information

# Persistence cho service
persistence true
persistence_location C:\\ProgramData\\mosquitto\\

# Allow retained messages
retain_available true

# ESP32 compatibility settings
message_size_limit 8192
keepalive_interval 60
retry_interval 20

# Connection limits
max_connections 100
max_queued_messages 1000

# End of ESP32 configuration
"""
    
    # Tạo thư mục ProgramData nếu chưa có
    try:
        os.makedirs("C:\\ProgramData\\mosquitto", exist_ok=True)
        print("✅ Đã tạo thư mục ProgramData")
    except Exception as e:
        print(f"⚠️ Không thể tạo thư mục ProgramData: {e}")
    
    # Tạo file cấu hình
    config_path = os.path.join(mosquitto_dir, "mosquitto_service.conf")
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print(f"✅ Đã tạo cấu hình service: {config_path}")
    except PermissionError:
        print("❌ Không có quyền ghi file cấu hình")
        print("💡 Hãy chạy với quyền Administrator")
        return False
    except Exception as e:
        print(f"❌ Lỗi tạo cấu hình: {e}")
        return False
    
    # Dừng service cũ nếu có
    print("🛑 Dừng service cũ...")
    subprocess.run(['net', 'stop', 'mosquitto'], capture_output=True)
    subprocess.run(['sc', 'delete', 'mosquitto'], capture_output=True)
    
    # Cài đặt Windows Service
    print("🔧 Cài đặt Mosquitto Windows Service...")
    
    service_cmd = [
        'sc', 'create', 'mosquitto',
        'binPath=', f'"{mosquitto_exe}" -c "{config_path}"',
        'DisplayName=', 'Mosquitto MQTT Broker (ESP32)',
        'start=', 'auto'
    ]
    
    try:
        result = subprocess.run(service_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Service đã được cài đặt thành công")
        else:
            print(f"⚠️ Lỗi cài đặt service: {result.stderr}")
            # Thử cách khác với mosquitto install
            print("🔄 Thử cách khác...")
            
            install_cmd = [mosquitto_exe, 'install', '-c', config_path]
            result2 = subprocess.run(install_cmd, capture_output=True, text=True)
            
            if result2.returncode == 0:
                print("✅ Service đã được cài đặt qua mosquitto install")
            else:
                print(f"❌ Cả hai cách đều thất bại: {result2.stderr}")
                return False
    
    except Exception as e:
        print(f"❌ Lỗi cài đặt service: {e}")
        return False
    
    # Khởi động service
    print("🚀 Khởi động Mosquitto Service...")
    
    try:
        result = subprocess.run(['net', 'start', 'mosquitto'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Mosquitto Service đã khởi động thành công!")
        else:
            print(f"⚠️ Lỗi khởi động service: {result.stderr}")
            print("💡 Thử khởi động thủ công: net start mosquitto")
            return False
    except Exception as e:
        print(f"❌ Lỗi khởi động service: {e}")
        return False
    
    # Cấu hình Windows Firewall
    print("🔥 Cấu hình Windows Firewall...")
    
    firewall_cmd = [
        'netsh', 'advfirewall', 'firewall', 'add', 'rule',
        'name=Mosquitto MQTT ESP32', 'dir=in', 'action=allow', 
        'protocol=TCP', 'localport=1883'
    ]
    
    try:
        result = subprocess.run(firewall_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Windows Firewall rule đã được thêm")
        else:
            print(f"⚠️ Lỗi firewall: {result.stderr}")
    except Exception as e:
        print(f"⚠️ Không thể cấu hình firewall: {e}")
    
    return True

def verify_service():
    """Kiểm tra service có chạy không"""
    print("🧪 Kiểm tra Mosquitto Service...")
    
    # Kiểm tra service status
    try:
        result = subprocess.run(['sc', 'query', 'mosquitto'], capture_output=True, text=True)
        if 'RUNNING' in result.stdout:
            print("✅ Mosquitto Service đang chạy")
        else:
            print("❌ Mosquitto Service không chạy")
            print(f"Status: {result.stdout}")
            return False
    except Exception as e:
        print(f"❌ Lỗi kiểm tra service: {e}")
        return False
    
    # Kiểm tra port 1883
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        listening = False
        for line in result.stdout.split('\n'):
            if '1883' in line and 'LISTENING' in line:
                print(f"✅ Port 1883 đang lắng nghe: {line.strip()}")
                listening = True
                break
        
        if not listening:
            print("❌ Port 1883 không lắng nghe")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi kiểm tra port: {e}")
        return False
    
    # Test kết nối
    print("🔌 Test kết nối MQTT...")
    
    import socket
    
    # Test localhost
    try:
        sock = socket.socket()
        sock.settimeout(3)
        sock.connect(('127.0.0.1', 1883))
        sock.close()
        print("✅ localhost:1883 - OK")
    except Exception as e:
        print(f"❌ localhost:1883 - FAILED: {e}")
        return False
    
    # Test external IP
    try:
        sock = socket.socket()
        sock.settimeout(3)
        sock.connect(('192.168.100.121', 1883))
        sock.close()
        print("✅ 192.168.100.121:1883 - OK")
        print("🎉 ESP32 có thể kết nối được!")
        return True
    except Exception as e:
        print(f"❌ 192.168.100.121:1883 - FAILED: {e}")
        return False

def show_service_info():
    """Hiển thị thông tin service"""
    print("\n📊 Thông tin Mosquitto Service:")
    print("=" * 40)
    
    # Service status
    try:
        result = subprocess.run(['sc', 'query', 'mosquitto'], capture_output=True, text=True)
        print("Service Status:")
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line and ('STATE' in line or 'SERVICE_NAME' in line):
                print(f"  {line}")
    except:
        print("  Không thể lấy thông tin service")
    
    # Port status
    print("\nPort Status:")
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if '1883' in line:
                print(f"  {line.strip()}")
    except:
        print("  Không thể kiểm tra port")
    
    print("\n🔧 Các lệnh hữu ích:")
    print("  net start mosquitto    - Khởi động service")
    print("  net stop mosquitto     - Dừng service")
    print("  sc delete mosquitto    - Xóa service")
    print("  services.msc           - Mở Service Manager")

if __name__ == "__main__":
    print("🚀 Mosquitto Windows Service Setup for ESP32")
    print("=" * 50)
    
    success = setup_mosquitto_windows_service()
    
    if success:
        print("\n" + "=" * 50)
        time.sleep(3)  # Đợi service khởi động hoàn toàn
        
        if verify_service():
            print("\n✅ HOÀN THÀNH! Mosquitto Service đã sẵn sàng cho ESP32")
            show_service_info()
        else:
            print("\n❌ Service có vấn đề, cần kiểm tra lại")
    else:
        print("\n❌ Cài đặt service thất bại")
        print("💡 Đảm bảo chạy với quyền Administrator")
