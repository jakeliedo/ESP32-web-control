# 🚽 WC Control System v2.0

Hệ thống điều khiển WC thông minh sử dụng ESP32, MQTT và Flask Web Interface với giao diện hiện đại.

## ✨ Features

🎛️ **Web Dashboard** - Giao diện điều khiển đầy đủ tính năng  
📱 **Mobile UI** - Tối ưu cho điện thoại di động  
🔄 **Real-time Updates** - Cập nhật trạng thái thời gian thực  
🌐 **MQTT Communication** - Giao tiếp đáng tin cậy với ESP32  
🗄️ **Event Logging** - Lưu trữ và theo dõi hoạt động  
🎨 **Modern UI** - Giao diện đẹp với Dark/Light theme  
📊 **Analytics** - Thống kê và phân tích sử dụng  
⚡ **Quick Setup** - Cài đặt tự động với script  

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────┐    MQTT     ┌─────────────────┐    HTTP    ┌─────────────────┐
│   ESP32 Nodes   │◄──────────► │    PC Host      │◄─────────► │   Web Browser   │
│   (Room 1,2..)  │   Commands  │  (Flask App)    │  Control   │   Dashboard     │
│                 │   Status    │   MQTT Broker   │            │                 │
└─────────────────┘             └─────────────────┘            └─────────────────┘
        │                               │                              │
        │                               │                              │
        └─ WiFi ─┐           ┌─ Database ─┘                              │
                 │           │ (SQLite)                                │
                 └─ Network ─┘                                         │
                                                             ┌─────────┘
                                                             │
                                                     ┌───────▼────────┐
                                                     │  Mobile Devices │
                                                     │   Responsive    │
                                                     └─────────────────┘
```

## 📁 Cấu trúc dự án

```
ESP_WC_System/
├── 📦 PC_host/                    # Flask Web Server
│   ├── 🐍 app.py                 # Main Flask application  
│   ├── ⚙️ config.py              # Configuration settings
│   ├── 🗄️ database.py            # SQLite database handler
│   ├── 📡 mqtt_handler.py        # MQTT client handler
│   ├── 🎨 templates/             # HTML templates
│   │   ├── index.html           # Modern Dashboard UI
│   │   ├── events.html          # Event history
│   │   ├── analytics.html       # Analytics dashboard
│   │   └── layout.html          # Base template with theme
│   ├── 🎨 static/                # Frontend assets
│   │   ├── css/style.css        # Enhanced styles
│   │   ├── js/main.js           # Interactive features
│   │   └── images/              # UI icons and images
│   └── 🗄️ data/                  # Database storage
├── 📱 ESP32_host/                # ESP32 Remote Control
│   ├── main.py                  # Remote control firmware
│   ├── lib/                     # MicroPython libraries
│   └── 📋 requirements.txt       # ESP32 dependencies
├── 🏠 ESP32_nodes/               # Individual WC Nodes
│   ├── room1/                   # Node 1 (Male WC)
│   │   └── main.py             # Node firmware
│   └── room2/                   # Node 2 (Female WC)
├── ⚙️ config/                    # Global configuration
│   ├── devices.json            # Device definitions
│   └── network_config.json     # Network settings
├── 📚 requirements.txt           # Python dependencies
├── 📖 INSTALLATION_GUIDE.md     # Detailed setup guide
├── 🛠️ setup.bat                 # Windows auto-setup
└── 🛠️ setup.sh                  # Linux/Mac auto-setup
```

## 🚀 Quick Setup

### 🏃‍♂️ Option 1: Automatic Setup (Recommended)

#### Windows:
```cmd
git clone <repository-url>
cd ESP_WC_System
setup.bat
```

#### macOS/Linux:
```bash
git clone <repository-url>
cd ESP_WC_System
chmod +x setup.sh
./setup.sh
```

### 🛠️ Option 2: Manual Setup

#### 1. Clone Repository:
```bash
git clone <repository-url>
cd ESP_WC_System
```

#### 2. Install Python Dependencies:
```bash
# Create virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux  
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Run Application:
```bash
cd PC_host
python quick_start.py
```

## 🖥️ Access URLs

- **🎛️ Main Dashboard**: http://localhost:5000
- **📱 Mobile Interface**: http://localhost:5000/simple  
- **📋 Event History**: http://localhost:5000/events
- **📊 Analytics**: http://localhost:5000/analytics
- **🔧 API Status**: http://localhost:5000/api/status

### Option 2: Manual Setup

### 1. Clone Repository
```bash
git clone <repo-url>
cd ESP_WC_System
```

### 2. Setup PC Host (Flask Server)
```bash
cd PC_host

# Install Python dependencies
pip install flask flask-socketio paho-mqtt

# Configure network settings
cp config.py.example config.py  # Edit IP addresses
```

### 3. Setup ESP32 Nodes
```bash
cd ../ESP32_nodes

# Install MicroPython on ESP32
# Deploy code to ESP32
python deploy.py --device room1 --port COM3
```

## ⚙️ Configuration

### PC Host Configuration (`PC_host/config.py`)
```python
# Network Configuration
HOST = "0.0.0.0"           # Flask server host
PORT = 5000                # Flask server port

# MQTT Broker Settings
MQTT_BROKER = "localhost"   # Change to your MQTT broker IP
MQTT_PORT = 1883
MQTT_USERNAME = None        # Set if authentication required
MQTT_PASSWORD = None

# Database
DATABASE_PATH = "wc_system.db"

# Debug
DEBUG = True
```

### Device Configuration (`config/devices.json`)
```json
{
  "nodes": [
    {
      "node_id": "room1",
      "name": "Room 1",
      "type": "male",
      "location": "Floor 1",
      "ip": "192.168.1.100"
    }
  ]
}
```

### Network Configuration (`config/network_config.json`)
```json
{
  "wifi": {
    "ssid": "YOUR_WIFI_SSID",
    "password": "YOUR_WIFI_PASSWORD"
  },
  "mqtt": {
    "broker": "192.168.1.10",
    "port": 1883,
    "topics": {
      "commands": "wc/commands/{node_id}",
      "status": "wc/status/{node_id}"
    }
  }
}
```

## 🔧 Setup cho IP khác nhau

### Khi chuyển sang network mới:

1. **Cập nhật PC Host IP:**
```bash
cd PC_host
# Sửa file config.py
nano config.py
# Thay đổi MQTT_BROKER = "IP_MỚI_CỦA_MQTT_BROKER"
```

2. **Cập nhật ESP32 Network:**
```bash
cd ESP32_nodes
# Sửa file network_config.json hoặc config trong main.py
# Cập nhật WiFi SSID, password và MQTT broker IP
```

3. **Auto-detect Network Script:**
```bash
# Chạy script tự động detect IP
python detect_network.py
```

## 🖥️ Chạy hệ thống

### 1. Start MQTT Broker (nếu chưa có)
```bash
# Ubuntu/Debian
sudo apt install mosquitto mosquitto-clients
sudo systemctl start mosquitto

# Windows (download từ mosquitto.org)
# Hoặc dùng Docker
docker run -it -p 1883:1883 eclipse-mosquitto
```

### 2. Start PC Host
```bash
cd PC_host
python app.py

# Hoặc dùng development mode
python -m flask run --host=0.0.0.0 --port=5000 --debug
```

### 3. Deploy ESP32 Code
```bash
cd ESP32_nodes
python deploy.py --device room1 --port COM3  # Windows
python deploy.py --device room1 --port /dev/ttyUSB0  # Linux
```

## 🌐 Web Interface

Sau khi start PC Host:

- **Dashboard UI:** `http://localhost:5000/`
- **Simple Mobile UI:** `http://localhost:5000/simple`
- **Events Log:** `http://localhost:5000/events`
- **API Status:** `http://localhost:5000/api/status`

### Remote Access:
- Thay `localhost` bằng IP của PC Host
- VD: `http://192.168.1.10:5000/`

## 🐛 Troubleshooting

### Common Issues:

1. **ESP32 không kết nối WiFi:**
```python
# Kiểm tra SSID/password trong main.py
# Kiểm tra signal strength
# Reset ESP32 và thử lại
```

2. **MQTT connection failed:**
```bash
# Test MQTT broker
mosquitto_pub -h BROKER_IP -t test -m "hello"
mosquitto_sub -h BROKER_IP -t test
```

3. **Web UI không hiển thị nodes:**
```bash
# Kiểm tra database
cd PC_host
python -c "from database import get_all_nodes; print(get_all_nodes())"
```

4. **Port conflicts:**
```bash
# Kiểm tra port đang sử dụng
netstat -tulnp | grep :5000  # Linux
netstat -ano | findstr :5000  # Windows
```

## 📱 Features

### Dashboard UI:
- ✅ Real-time node status
- ✅ FLUSH button controls
- ✅ Event logging
- ✅ Auto-refresh
- ✅ Responsive design

### Simple UI:
- ✅ Mobile-optimized
- ✅ 2x2 grid layout
- ✅ Touch-friendly buttons
- ✅ Minimal interface

### ESP32 Features:
- ✅ WiFi auto-reconnect
- ✅ MQTT communication
- ✅ LED status indicator
- ✅ 4-second flush sequence
- ✅ Heartbeat status

## 🔄 Development Workflow

### 1. Testing Changes:
```bash
# Test Flask app
cd PC_host
python -m pytest tests/

# Test ESP32 code
cd ESP32_nodes
python test_mqtt.py
```

### 2. Adding New Nodes:
```bash
# 1. Add to config/devices.json
# 2. Copy ESP32_nodes/room1/ to ESP32_nodes/roomX/
# 3. Update node_id in main.py
# 4. Deploy to new ESP32
python deploy.py --device roomX --port COMX
```

### 3. Backup Database:
```bash
cd PC_host
cp wc_system.db wc_system_backup_$(date +%Y%m%d).db
```

## 🚀 Production Deployment

### Using Docker:
```dockerfile
# Dockerfile for PC Host
FROM python:3.9-slim
WORKDIR /app
COPY PC_host/ .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
```

### Using systemd (Linux):
```bash
# Create service file
sudo nano /etc/systemd/system/wc-system.service

# Enable and start
sudo systemctl enable wc-system
sudo systemctl start wc-system
```

## 📞 Support

### Logs Location:
- **Flask logs:** Console output hoặc `/var/log/wc-system.log`
- **ESP32 logs:** Serial monitor (115200 baud)
- **MQTT logs:** `/var/log/mosquitto/mosquitto.log`

### Debug Commands:
```bash
# Check system status
curl http://localhost:5000/api/status

# Test MQTT
mosquitto_pub -h localhost -t "wc/commands/room1" -m '{"action":"flush"}'

# Check database
sqlite3 PC_host/wc_system.db "SELECT * FROM nodes;"
```

---

## 🎯 Complete Setup Checklist

### ✅ For New Installation:
1. **Clone repo:** `git clone <repo-url>`
2. **Quick setup:** Run `quick_setup.bat` (Windows) or `./quick_setup.sh` (Linux)
3. **Configure WiFi:** Edit `config/network_config.json`
4. **Start system:** Run `start_system.bat` or `./start_system.sh`
5. **Deploy ESP32:** Use `ESP32_nodes/deploy.py`

### ✅ For Different IP/Network:
1. **Run detector:** `python detect_network.py`
2. **Update configs:** Script will auto-update most settings
3. **Manual WiFi:** Edit `config/network_config.json` for ESP32
4. **Restart:** Use startup scripts

### ✅ Files Created by Auto-Setup:
- `PC_host/config.py` - Flask app configuration
- `config/network_config.json` - Network settings
- `config/devices.json` - Device definitions
- `start_system.bat/.sh` - Startup scripts

## 📝 Notes

- ESP32 cần MicroPython firmware
- PC Host cần Python 3.7+
- MQTT broker có thể chạy trên cùng PC hoặc riêng biệt
- Web interface tương thích với mobile browsers
- System hỗ trợ multiple ESP32 nodes
- Auto-detection script giúp setup nhanh cho network mới

**🎉 Happy Building! Clone và chạy `quick_setup.bat` để bắt đầu!**
├── config/                         # Shared configuration
│   ├── network_config.json         # WiFi, MQTT settings
│   └── devices.json                # Node information
├── esp32_host/                     # ESP32 Host/Remote
│   ├── main.py                     # Main file
│   ├── boot.py                     # Boot initialization
│   ├── mqtt_client.py              # MQTT client
│   ├── lib/                        # Libraries
│   │   ├── microWebSrv.py          # Web server
│   │   └── umqtt/                  # MQTT library
│   └── static/                     # Web assets
│       ├── male.png
│       ├── female.png
│       └── button.png
├── esp8266_nodes/                  # ESP8266 Nodes
│   ├── wc1/                        # Node 1 (Male Room 1)
│   │   ├── main.py
│   │   └── boot.py
│   ├── wc2/                        # Node 2 (Male Room 2)
│   │   ├── main.py
│   │   └── boot.py
│   ├── wc3/                        # Node 3 (Female Room 1)
│   │   ├── main.py
│   │   └── boot.py
│   └── lib/                        # Shared libraries
│       └── mqtt_handler.py
├── pc_host/                        # PC Backup Host
│   ├── app.py                      # Flask app
│   ├── mqtt_bridge.py              # MQTT client
│   └── static/                     # Web assets
└── ESP_WC_System.code-workspace    # VS Code workspace
```

## Development Status

### ✅ Completed
- [x] Created project directory structure
- [x] Configured VS Code workspace
- [x] Defined system architecture
- [x] Created basic boot.py file

### 🔄 In Progress
- [ ] ESP32 Host main.py (copy from MicroWebSrv + add MQTT)
- [ ] ESP32 Host mqtt_client.py
- [ ] ESP8266 Node template code
- [ ] Config files (network, devices)

### ⏳ Not Started
- [ ] TFT display integration (ESP32)
- [ ] PC Flask app with MQTT
- [ ] OTA update system
- [ ] Security implementation
- [ ] Internet access via port forwarding

## Network Configuration

### WiFi Networks
- **Michelle**: Static IP 192.168.1.43
- **Vinternal**: Dynamic IP
- **Floor 9**: Dynamic IP

### MQTT Configuration
- **Broker**: ESP32 host or PC backup
- **Topics**:
  - `wc/{node_id}/command` - Send commands to nodes
  - `wc/{node_id}/status` - Receive status from nodes
  - `host/status` - Host status

## Hardware Configuration

### ESP32 Host
- **Board**: ESP32S module
- **Display**: TFT 3.5" touchscreen (future)
- **WiFi**: Built-in
- **Role**: Web server + MQTT client/broker

### ESP8266 Nodes (D1 Mini Pro)
- **Board**: ESP8266 D1 Mini Pro
- **GPIO**:
  - GPIO2: Built-in LED (feedback)
  - GPIO5 (D1): Relay/Output 1
  - GPIO4 (D2): Relay/Output 2  
  - GPIO0 (D3): Relay/Output 3
- **WiFi**: Built-in
- **Role**: MQTT client + GPIO control

## API/Protocol Specification

### MQTT Messages
```json
// Command to node
{
  "topic": "wc/wc1/command",
  "payload": "1_on"  // format: {channel}_{action}
}

// Status from node  
{
  "topic": "wc/wc1/status",
  "payload": "{\"1\": 1, \"2\": 0, \"3\": 0}"
}
```

### Web API (HTTP)
```
POST /control
{
  "action": "1_on",
  "node_id": "wc1"
}
```

## Installation and Deployment

### Requirements
- MicroPython firmware for ESP32/ESP8266
- VS Code with MicroPython extension
- Python 3.7+ for PC backup host

### Required Python Libraries
```bash
pip install flask paho-mqtt
```

### MicroPython Libraries
- umqtt.simple
- network
- machine
- json

## Development History

### Version 1.0 (Current)
- Migrated from Flask + ESP32 to ESP32 Host + ESP8266 Nodes architecture
- Using MQTT instead of direct HTTP calls
- Prepared framework for TFT display

### Version 0.9 (Previous)  
- Flask server on PC
- ESP32 with MicroWebSrv
- HTTP communication
- Responsive web interface

## Important Notes

1. **ESP8266 Optimization**: Code for ESP8266 nodes must be minimal to save memory
2. **PC Host Fallback**: PC can serve as backup host when ESP32 fails
3. **Auto-reconnect**: All devices must have automatic reconnection mechanism
4. **OTA Ready**: Framework prepared for future OTA updates

## Contact and Support
- **Developer**: Jakeliedo
- **Repository**: https://github.com/jakeliedo/ESP32-web-control
- **Last Updated**: July 5, 2025

---
*This documentation is continuously updated according to project development progress.*