# ESP32 Room1 Node - Pymakr Deployment Guide

## 🎯 Quick Start (COM10)

### 1. Prerequisites
- ✅ ESP32 connected to COM10
- ✅ MicroPython firmware flashed on ESP32
- ✅ VS Code with Pymakr extension installed
- ✅ Flask app running on PC (for MQTT broker)

### 2. Open Project in VS Code
```bash
# Navigate to room1 folder
cd "b:\Python\MicroPython\ESP_WC_System\ESP32_nodes\room1"

# Open in VS Code
code .
```

### 3. Configure Network Settings
Edit `main.py` and update:
```python
# Line 18: Your PC's IP address
MQTT_BROKER = '192.168.1.182'  # ← Change this!

# Line 21-22: Your WiFi credentials  
WIFI_SSID = 'Michelle'          # ← Your WiFi name
WIFI_PASS = '0908800130'        # ← Your WiFi password
```

### 4. Upload to ESP32

#### Method 1: Using Pymakr Extension
1. **Connect Device**:
   - Press `Ctrl+Shift+P`
   - Type: "Pymakr: Connect Device"
   - Select COM10

2. **Upload Project**:
   - Right-click on `room1` folder in Explorer
   - Select "Pymakr: Upload project to device"
   - Wait for upload completion

#### Method 2: Manual Upload
1. **Connect to ESP32**:
   - Press `Ctrl+Shift+P`
   - Type: "Pymakr: Connect Device"
   - Select COM10

2. **Upload Files One by One**:
   - Right-click `main.py` → "Upload to device"
   - Right-click `boot.py` → "Upload to device"  
   - Right-click `lib` folder → "Upload to device"

### 5. Monitor Serial Output
- Press `Ctrl+Shift+P`
- Type: "Pymakr: Toggle Serial Monitor"
- Watch for connection messages

### 6. Test the Node
1. **Check serial output** for WiFi and MQTT connection
2. **Open web dashboard**: http://localhost:5000
3. **Verify Room1 is online** (green border)
4. **Click Room1 FLUSH button**
5. **Watch ESP32 LED** blink for 5 seconds!

## 📊 Expected Results

### Serial Monitor Output:
```
ESP32 Room1 Node - Boot Complete
Starting main.py...
[wc_male_01] Starting Room1 ESP32 Node...
[wc_male_01] Device ID: 30aea4123456
[wc_male_01] Testing LED...
[wc_male_01] LED test complete
[wc_male_01] ✅ WiFi connected to Michelle!
[wc_male_01] IP address: 192.168.100.200
[wc_male_01] ✅ MQTT connected!
[wc_male_01] 📡 Subscribed to: wc/wc_male_01/command
[wc_male_01] 🎉 Room1 ESP32 Node is ready!
[wc_male_01] 💡 LED will blink when flush command is received
```

### When FLUSH Button Pressed:
```
[wc_male_01] 📨 Received: wc/wc_male_01/command -> {"action":"flush","timestamp":1704546789.123}
[wc_male_01] 🚽 FLUSH command received for Room1!
[wc_male_01] 🔄 Executing flush for Room1...
[wc_male_01] 📤 Response sent: flush - SUCCESS
[wc_male_01] 💡 LED blinking... 20 blinks remaining
[wc_male_01] 💡 LED blinking... 15 blinks remaining
[wc_male_01] 💡 LED blinking... 10 blinks remaining
[wc_male_01] 💡 LED blinking... 5 blinks remaining
[wc_male_01] ✅ LED blinking completed
```

## 🔧 Project Files Overview

### Files that get uploaded to ESP32:
```
ESP32 File System:
├── main.py              # Main application (auto-runs on boot)
├── boot.py              # Boot configuration  
└── lib/umqtt/simple.py  # MQTT library
```

### Files that stay on PC:
```
room1/ (PC folder):
├── pymakr.conf          # Pymakr configuration
└── README.md            # Documentation
```

## 🐛 Troubleshooting

### Upload Fails:
- Check ESP32 is connected to COM10
- Verify ESP32 drivers installed
- Try different USB cable
- Reset ESP32 and try again

### WiFi Connection Fails:
- Check WiFi credentials in main.py
- Ensure WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
- Move ESP32 closer to router

### MQTT Connection Fails:
- Verify PC IP address in MQTT_BROKER setting
- Check Flask app is running (provides MQTT broker)
- Check firewall settings on PC

### LED Doesn't Blink:
- Check serial output when FLUSH button pressed
- Verify Room1 shows as "online" in dashboard
- Restart ESP32 and check connections

## ✅ Success Checklist

- [ ] ESP32 connected to COM10
- [ ] MicroPython firmware flashed
- [ ] Network settings updated in main.py
- [ ] Project uploaded successfully
- [ ] WiFi connection established
- [ ] MQTT connection established  
- [ ] Room1 appears online in dashboard
- [ ] LED blinks when FLUSH pressed
- [ ] Serial monitor shows clear messages

---

**Ready to test!** Your ESP32 Room1 node should now respond to FLUSH commands from the web dashboard! 🚽💡
