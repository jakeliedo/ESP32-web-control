# 🚀 WC Control System - Setup Guide

Hướng dẫn cài đặt và chạy WC Control System trên máy tính mới.

## 📋 Yêu cầu hệ thống

### Bắt buộc:
- **Python 3.8+** (khuyến nghị Python 3.10 hoặc 3.11)
- **Git** để clone repository
- **MQTT Broker** (mosquitto hoặc built-in broker)

### Tùy chọn (cho phát triển ESP32):
- **Visual Studio Code** với extension Pymakr
- **ESP32 Development Board**
- **USB Cable** để connect ESP32

## 🛠️ Cài đặt

### 1. Clone Repository
```bash
git clone <repository-url>
cd ESP_WC_System
```

### 2. Tạo Virtual Environment (Khuyến nghị)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux  
python3 -m venv venv
source venv/bin/activate
```

### 3. Cài đặt Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Cài đặt MQTT Broker

#### Windows (Mosquitto):
```bash
# Download và cài đặt từ: https://mosquitto.org/download/
# Hoặc sử dụng built-in broker (tự động khởi động)
```

#### macOS:
```bash
brew install mosquitto
brew services start mosquitto
```

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```

### 5. Cấu hình môi trường

Tạo file `.env` trong thư mục `PC_host/`:
```env
# MQTT Configuration
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_CLIENT_ID=wc_control_pc

# Flask Configuration  
SECRET_KEY=your-secret-key-here
DEBUG=True
HOST=0.0.0.0
PORT=5000

# Database
DB_PATH=data/wc_system.db
```

## 🚀 Chạy ứng dụng

### Chạy nhanh (All-in-one):
```bash
cd PC_host
python quick_start.py
```

### Chạy thủ công:

#### 1. Khởi động MQTT Broker (nếu cần):
```bash
cd PC_host
python start_mqtt_broker.py
```

#### 2. Khởi động Flask Web Server:
```bash
cd PC_host
python app.py
```

#### 3. Truy cập ứng dụng:
- **Dashboard**: http://localhost:5000
- **Mobile UI**: http://localhost:5000/simple
- **Events**: http://localhost:5000/events
- **Analytics**: http://localhost:5000/analytics

## 📱 ESP32 Node Setup (Tùy chọn)

### 1. Cài đặt ESP32 Development Tools:
```bash
pip install esptool ampy pyserial
```

### 2. Chuẩn bị ESP32:
```bash
cd ESP32_host
python setup_dev_env.bat  # Windows
# hoặc ./setup_dev_env.sh  # macOS/Linux
```

### 3. Upload code lên ESP32:
```bash
cd ESP32_host  
python upload_project.py
```

### 4. Cấu hình WiFi trong ESP32:
Chỉnh sửa file `ESP32_nodes/room1/main.py`:
```python
# Thay đổi WiFi credentials
if "YourWiFiName" in networks:
    wlan.connect('YourWiFiName', 'YourPassword')
```

## 🔧 Cấu trúc Project

```
ESP_WC_System/
├── PC_host/                 # Flask Web Application
│   ├── app.py              # Main Flask app
│   ├── config.py           # Configuration
│   ├── database.py         # Database operations
│   ├── mqtt_handler.py     # MQTT communication
│   ├── templates/          # HTML templates
│   ├── static/            # CSS, JS, images
│   └── data/              # SQLite database
├── ESP32_host/             # ESP32 Remote Control
│   ├── main.py            # Main ESP32 code
│   ├── lib/               # MicroPython libraries
│   └── requirements.txt   # ESP32 dependencies
├── ESP32_nodes/            # Individual WC Nodes
│   └── room1/             # Node 1 (Male WC)
├── config/                 # Global configuration
└── requirements.txt        # Python dependencies
```

## 🧪 Testing

### Test hệ thống:
```bash
cd PC_host
python test_system_full.py
```

### Test MQTT:
```bash
cd PC_host
python debug_mqtt_monitor.py
```

### Test UI:
```bash
cd PC_host  
python test_ui.py
```

## 🔍 Troubleshooting

### Lỗi thường gặp:

#### 1. ModuleNotFoundError:
```bash
pip install -r requirements.txt
```

#### 2. MQTT Connection Failed:
```bash
# Kiểm tra MQTT broker
cd PC_host
python start_mqtt_broker.py
```

#### 3. Database Error:
```bash
# Reset database
cd PC_host
python reset_nodes.py
```

#### 4. Port 5000 đã sử dụng:
Thay đổi PORT trong `.env` hoặc:
```bash
# Kill process on port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:5000 | xargs kill -9
```

## 🌐 Network Configuration

### Cho phép truy cập từ mạng nội bộ:
1. Mở `.env` file
2. Đặt `HOST=0.0.0.0`
3. Kiểm tra firewall settings

### Tìm IP address:
```bash
cd PC_host
python show_urls.py
```

## 📊 Features

✅ **Web Dashboard** - Giao diện điều khiển chính  
✅ **Mobile UI** - Giao diện tối ưu cho mobile  
✅ **Real-time Events** - Theo dõi events thời gian thực  
✅ **MQTT Communication** - Giao tiếp với ESP32 nodes  
✅ **SQLite Database** - Lưu trữ logs và cấu hình  
✅ **Responsive Design** - Tương thích mọi thiết bị  
✅ **Dark/Light Theme** - Chế độ giao diện  
✅ **Auto-refresh** - Cập nhật tự động  

## 🔧 Development

### Code formatting:
```bash
black PC_host/*.py
```

### Linting:
```bash
pylint PC_host/*.py
```

### Testing:
```bash
pytest PC_host/tests/
```

## 📝 Notes

- Database tự động được tạo khi chạy lần đầu
- MQTT broker có thể sử dụng built-in hoặc external
- ESP32 nodes hoạt động độc lập với PC host
- Web interface hoạt động với hoặc không có ESP32

## 📞 Support

Nếu gặp vấn đề, check:
1. Python version (python --version)
2. Dependencies installed (pip list)
3. MQTT broker running
4. Network connectivity
5. Firewall settings

---
*WC Control System v2.0 - Updated July 2025*
