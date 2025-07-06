# ESP32 Room1 Node Project

## 📋 Overview
This project contains the MicroPython code for ESP32 Room1 Node (Male WC) connected to COM10.

## 📂 Project Structure
```
room1/
├── main.py              # Main application code
├── boot.py              # Boot configuration
├── pymakr.conf          # Pymakr project configuration
├── lib/umqtt/simple.py  # MQTT client library
└── README.md            # This file
```

## 🔧 Hardware Configuration
- **Device**: ESP32 Development Board
- **Port**: COM10
- **Node ID**: wc_male_01
- **Room**: Room1 (Male WC)

## 🔌 GPIO Pins
- **GPIO 2**: Built-in LED (status indication)
- **GPIO 5**: Relay control (for future actuator)
- **GPIO 18**: Optional external LED

## 🚀 Upload Instructions

### Using VS Code + Pymakr:
1. **Open this folder** in VS Code
2. **Connect ESP32** to COM10
3. **Connect Device**: 
   - Ctrl+Shift+P → "Pymakr: Connect Device"
   - Select COM10
4. **Upload Project**:
   - Right-click on folder → "Pymakr: Upload project to device"
   - Or use Ctrl+Shift+P → "Pymakr: Upload project"

### Files to Upload:
- ✅ `main.py` → Root directory of ESP32
- ✅ `boot.py` → Root directory of ESP32  
- ✅ `lib/umqtt/simple.py` → `/lib/umqtt/simple.py` on ESP32

## ⚙️ Configuration
Before uploading, update these settings in `main.py`:

```python
# Network Configuration
MQTT_BROKER = '192.168.100.72'  # Your PC's IP address
WIFI_SSID = 'Michelle'          # Your WiFi network
WIFI_PASS = '0908800130'        # Your WiFi password
```

## 🧪 Testing
1. **Upload code** to ESP32
2. **Monitor serial output** in Pymakr terminal
3. **Check web dashboard** - Room1 should appear online
4. **Press FLUSH button** - ESP32 LED should blink for 5 seconds

## 📡 MQTT Topics
- **Subscribe**: `wc/wc_male_01/command` (receives flush commands)
- **Publish**: `wc/wc_male_01/status` (sends status updates)
- **Publish**: `wc/wc_male_01/response` (sends command responses)

## 🔍 Expected Serial Output
```
[wc_male_01] Starting Room1 ESP32 Node...
[wc_male_01] ✅ WiFi connected to Michelle!
[wc_male_01] ✅ MQTT connected!
[wc_male_01] 🎉 Room1 ESP32 Node is ready!
[wc_male_01] 💡 LED will blink when flush command is received
```

## 🐛 Troubleshooting
- **Upload fails**: Check COM10 port and ESP32 connection
- **WiFi fails**: Update WiFi credentials and check 2.4GHz network
- **MQTT fails**: Verify PC IP address and Flask app running
- **No LED blink**: Check serial output when FLUSH button is pressed
