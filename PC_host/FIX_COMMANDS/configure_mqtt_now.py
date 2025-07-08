#!/usr/bin/env python3
"""
Cấu hình Mosquitto cho ESP32 ngay lập tức
"""

import subprocess
import os
import time
import shutil

def configure_mosquitto_now():
    """Cấu hình Mosquitto ngay lập tức"""
    print("🔧 Đang cấu hình Mosquitto cho ESP32...")
    
    # Nội dung cấu hình ESP32
    esp32_config = """# ESP32 WC System - Mosquitto Configuration
# Cấu hình cho phép ESP32 kết nối

# Lắng nghe trên tất cả interfaces, port 1883
listener 1883 0.0.0.0

# Cho phép kết nối ẩn danh (không cần xác thực)
allow_anonymous true

# Log chi tiết để debug
log_dest stdout
log_type all

# Không lưu persistence để đơn giản
persistence false

# Cho phép retained messages
retain_available true

# Giới hạn kích thước message (tương thích ESP32)
message_size_limit 8192

# Timeout settings cho ESP32
keepalive_interval 60
retry_interval 20

# End of ESP32 configuration
"""
    
    try:
        # 1. Dừng service hiện tại
        print("🛑 Dừng Mosquitto service...")
        subprocess.run(['net', 'stop', 'mosquitto'], capture_output=True)
        
        # 2. Backup cấu hình cũ
        config_path = "C:\\Program Files\\mosquitto\\mosquitto.conf"
        backup_path = "C:\\Program Files\\mosquitto\\mosquitto.conf.backup"
        
        if os.path.exists(config_path):
            try:
                shutil.copy2(config_path, backup_path)
                print("💾 Đã backup cấu hình cũ")
            except:
                print("⚠️ Không thể backup (không có quyền)")
        
        # 3. Tạo cấu hình mới
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(esp32_config)
            print(f"✅ Đã tạo cấu hình ESP32: {config_path}")
            config_file = config_path
        except PermissionError:
            # Nếu không có quyền, tạo ở thư mục hiện tại
            config_file = "mosquitto_esp32.conf"
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(esp32_config)
            print(f"✅ Đã tạo cấu hình ESP32: {os.path.abspath(config_file)}")
        
        # 4. Khởi động lại service
        print("🚀 Khởi động Mosquitto service...")
        result = subprocess.run(['net', 'start', 'mosquitto'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Mosquitto service đã khởi động")
        else:
            print("⚠️ Service không khởi động được, thử chạy thủ công...")
            print(f"🔧 Lệnh: mosquitto -c \"{config_file}\" -v")
            
            # Thử chạy thủ công
            try:
                print("🦟 Đang chạy Mosquitto thủ công...")
                process = subprocess.Popen([
                    'mosquitto', '-c', config_file, '-v'
                ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
                
                # Đợi một chút để broker khởi động
                time.sleep(3)
                
                if process.poll() is None:
                    print("✅ Mosquitto đang chạy!")
                else:
                    print("❌ Mosquitto không khởi động được")
                    
            except FileNotFoundError:
                print("❌ Không tìm thấy mosquitto.exe")
                print("💡 Kiểm tra lại cài đặt Mosquitto")
        
        # 5. Kiểm tra kết nối
        print("🧪 Kiểm tra kết nối...")
        time.sleep(2)
        
        import socket
        
        # Test localhost
        try:
            sock = socket.socket()
            sock.settimeout(5)
            sock.connect(('127.0.0.1', 1883))
            sock.close()
            print("✅ MQTT broker hoạt động trên localhost:1883")
        except:
            print("❌ Không kết nối được localhost:1883")
            return False
        
        # Test external IP
        try:
            sock = socket.socket()
            sock.settimeout(5)
            sock.connect(('192.168.100.121', 1883))
            sock.close()
            print("✅ MQTT broker hoạt động trên 192.168.100.121:1883")
            print("🎉 ESP32 có thể kết nối được!")
            return True
        except:
            print("❌ Không kết nối được 192.168.100.121:1883")
            print("💡 Kiểm tra Windows Firewall")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def check_ports():
    """Kiểm tra port đang lắng nghe"""
    print("📊 Kiểm tra port 1883:")
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if '1883' in line:
                print(f"  {line.strip()}")
    except:
        print("  Không thể kiểm tra ports")

if __name__ == "__main__":
    print("🚀 ESP32 MQTT Broker Configuration Tool")
    print("="*50)
    
    success = configure_mosquitto_now()
    
    print("\n" + "="*50)
    check_ports()
    
    if success:
        print("\n✅ HOÀN THÀNH! ESP32 có thể kết nối MQTT broker")
        print("📡 Địa chỉ kết nối: 192.168.100.121:1883")
    else:
        print("\n❌ CÓ VẤN ĐỀ! Kiểm tra lại cài đặt Mosquitto")
        print("💡 Thử chạy: mosquitto -c mosquitto_esp32.conf -v")
