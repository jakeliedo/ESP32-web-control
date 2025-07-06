# ESP WC System - Multi-Device Configuration Guide

## Device Management Structure

### Current Project Structure:
```
ESP_WC_System/
├── ESP32_host/           # Device 1: ESP32 Host
│   ├── main.py
│   ├── boot.py
│   └── pymakr.conf       # Config for ESP32
│
├── ESP8266_nodes/
│   ├── wc1/              # Device 2: ESP8266 Node 1
│   │   ├── main.py
│   │   └── pymakr.conf   # Config for ESP8266 WC1
│   │
│   ├── wc2/              # Device 3: ESP8266 Node 2 (future)
│   │   ├── main.py
│   │   └── pymakr.conf   # Config for ESP8266 WC2
│   │
│   └── wc3/              # Device 4: ESP8266 Node 3 (future)
│       ├── main.py
│       └── pymakr.conf   # Config for ESP8266 WC3
```

## How to Add New Device:

### Method 1: VS Code Pymakr Extension
1. Open Command Palette (Ctrl+Shift+P)
2. Type "Pymakr: Add Device"
3. Select COM port for new device
4. Choose project folder (e.g., ESP8266_nodes/wc2/)

### Method 2: Manual Configuration
1. Create new folder for device
2. Create pymakr.conf in that folder
3. Connect device via USB
4. Use Pymakr terminal to connect

### Method 3: Workspace-level Management
1. Each subfolder can have its own pymakr.conf
2. Switch between devices using Pymakr device list
3. Upload to specific device by selecting active folder

## Device Connection Workflow:
1. Connect ESP32 → Work in ESP32_host/ folder
2. Connect ESP8266 Node 1 → Work in ESP8266_nodes/wc1/ folder
3. Connect ESP8266 Node 2 → Work in ESP8266_nodes/wc2/ folder

## Tips:
- Each device maintains separate connection
- Use descriptive names in pymakr.conf
- Keep device-specific code in respective folders
- Use shared libraries in common folders
