# ESP WC Control System

## Project Overview
Smart WC control system using ESP32 as host and ESP8266 as control nodes. The system supports both web interface and TFT touchscreen display (future implementation).

## System Architecture
```
┌─────────────────┐    MQTT/HTTP    ┌──────────────────┐
│   ESP32 Host    │◄───────────────►│  ESP8266 Node 1  │
│ Web + TFT UI    │                 │   (WC1 - Male)   │
└─────────────────┘                 └──────────────────┘
         │                                    │
         │                          ┌──────────────────┐
         │          MQTT/HTTP       │  ESP8266 Node 2  │
         └─────────────────────────►│   (WC2 - Male)   │
         │                          └──────────────────┘
         │                                    │
         │                          ┌──────────────────┐
         │          MQTT/HTTP       │  ESP8266 Node 3  │
         └─────────────────────────►│  (WC3 - Female)  │
                                    └──────────────────┘
┌─────────────────┐
│   PC Backup     │
│  Flask Server   │
└─────────────────┘
```

## Directory Structure
```
ESP_WC_System/
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