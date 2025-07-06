# ESP8266 Nodes Deployment Guide

## 📋 Templates đã tạo sẵn

### Node WC1 (Male Room 1)
- **Folder**: `ESP8266_nodes/wc1/`
- **NODE_ID**: `'wc1'`
- **MQTT Topics**: 
  - Subscribe: `wc/wc1/command`
  - Publish: `wc/wc1/status`
- **Files**: ✅ main.py, boot.py, pymakr.conf

### Node WC2 (Male Room 2)  
- **Folder**: `ESP8266_nodes/wc2/`
- **NODE_ID**: `'wc2'`
- **MQTT Topics**:
  - Subscribe: `wc/wc2/command`
  - Publish: `wc/wc2/status`
- **Files**: ✅ main.py, boot.py, pymakr.conf

### Node WC3 (Female Room 1)
- **Folder**: `ESP8266_nodes/wc3/`
- **NODE_ID**: `'wc3'`
- **MQTT Topics**:
  - Subscribe: `wc/wc3/command`
  - Publish: `wc/wc3/status`
- **Files**: ✅ main.py, boot.py, pymakr.conf

## 🔧 Deployment Steps

### 1. Connect ESP8266 Device
```
1. Connect ESP8266 D1 Mini Pro via USB
2. Check Device Manager for COM port
3. Open VS Code with this workspace
```

### 2. Select Target Node
```
4. Navigate to desired node folder:
   - ESP8266_nodes/wc1/ (for first node)
   - ESP8266_nodes/wc2/ (for second node) 
   - ESP8266_nodes/wc3/ (for third node)
```

### 3. Upload Files using Pymakr
```
5. Ctrl+Shift+P → "Pymakr: Connect Device"
6. Select correct COM port
7. Upload project files (main.py, boot.py)
8. Reset ESP8266 to start
```

### 4. Verify Connection
```
9. Monitor Serial Console for:
   - WiFi connection success
   - MQTT broker connection
   - Heartbeat messages every 30s
```

## 🧪 Testing Commands

### Send test commands via MQTT:
```json
Topic: wc/wc1/command
Payload: {"action": "flush"}

Topic: wc/wc2/command  
Payload: {"action": "flush"}

Topic: wc/wc3/command
Payload: {"action": "flush"}
```

### Or simple text commands:
```
Topic: wc/wc1/command
Payload: flush

Topic: wc/wc1/command
Payload: stop
```

## 🔌 Hardware Connections

### ESP8266 D1 Mini Pro Pinout:
```
GPIO2  → Built-in LED (Blue LED on board)
GPIO5  → Relay Control (D1 pin)
GPIO4  → Status LED (D2 pin) - optional external LED
```

### Relay Module Connection:
```
VCC    → 3.3V or 5V (depending on relay module)
GND    → GND
IN     → GPIO5 (D1)
```

## 🐛 Troubleshooting

### Common Issues:
1. **WiFi not connecting**: Check SSID/password in code
2. **MQTT not connecting**: Verify broker IP address
3. **Upload fails**: Check COM port and driver installation
4. **No response**: Check serial monitor for error messages

### Debug Commands:
```python
# In MicroPython REPL:
import network
sta = network.WLAN(network.STA_IF)
print(sta.ifconfig())  # Check IP address
```

## 🚀 Ready to Deploy!

All templates are ready. Simply:
1. Connect your ESP8266
2. Choose the appropriate folder (wc1, wc2, or wc3)
3. Upload and test!

Each node will automatically:
- ✅ Connect to available WiFi
- ✅ Connect to MQTT broker
- ✅ Listen for flush commands
- ✅ Send status updates
- ✅ Blink LED during operation
- ✅ Auto-disconnect relay after 5 seconds

