# ESP32 Room1 Node Setup Guide (COM10)

## 🎯 Objective
Set up ESP32 on COM10 as Room1 node to blink LED when "FLUSH" button is pressed in the web dashboard.

## 📋 Prerequisites
- ESP32 Development Board connected to COM10
- MicroPython firmware flashed on ESP32
- PC Flask application running (with MQTT broker)
- ESP32 connected to same WiFi network as PC

## 🔧 Hardware Setup

### ESP32 Pin Configuration:
```
GPIO 2  → Built-in LED (will blink on flush command)
GPIO 5  → Optional relay output (for future actuator)
GND     → Ground
3.3V    → Power
```

### Current Test Setup:
- **Only built-in LED** will blink when Room1 flush is pressed
- **No external hardware required** for this test

## 💻 Software Setup

### Step 1: Flash MicroPython (if not done)
```bash
# Download MicroPython firmware for ESP32
# Flash using esptool:
esptool.py --chip esp32 --port COM10 erase_flash
esptool.py --chip esp32 --port COM10 write_flash -z 0x1000 esp32-micropython.bin
```

### Step 2: Upload MQTT Library
1. Create folder structure on ESP32:
   ```
   /lib/umqtt/simple.py
   ```
2. Copy the MQTT library from: `ESP32_nodes/lib/umqtt/simple.py`

### Step 3: Upload Room1 Node Code
1. Upload `ESP32_nodes/room1_test.py` as `main.py` to ESP32
2. Or use the existing `ESP32_nodes/room1/main.py`

### Step 4: Configure Network Settings
Update these values in the code before uploading:

```python
# Your PC's IP address (where Flask app runs)
MQTT_BROKER = '192.168.100.72'  # ← Update this!

# Your WiFi credentials
WIFI_SSID = 'Michelle'          # ← Update if needed
WIFI_PASS = '0908800130'        # ← Update if needed
```

## 🚀 Deployment Steps

### Using Thonny IDE:
1. **Connect to ESP32:**
   - Open Thonny IDE
   - Go to Tools → Options → Interpreter
   - Select "MicroPython (ESP32)"
   - Choose COM10 port
   - Click OK

2. **Upload MQTT Library:**
   - Create `/lib/umqtt/` folder on ESP32
   - Upload `simple.py` to `/lib/umqtt/simple.py`

3. **Upload Node Code:**
   - Open `room1_test.py` in Thonny
   - Update IP addresses and WiFi credentials
   - Save as `main.py` to ESP32
   - Click "Run" or press F5

4. **Monitor Output:**
   - Watch the Shell window for connection messages
   - Should see WiFi and MQTT connection success

### Using VS Code + Pymakr:
1. **Open ESP32 folder:**
   ```
   cd ESP32_nodes/room1/
   ```

2. **Connect device:**
   - Ctrl+Shift+P → "Pymakr: Connect Device"
   - Select COM10

3. **Upload project:**
   - Ctrl+Shift+P → "Pymakr: Upload Project"
   - Wait for upload completion

4. **Monitor serial:**
   - Ctrl+Shift+P → "Pymakr: Serial Monitor"

## 📡 Testing the Connection

### Expected Serial Output:
```
==================================================
ESP32 WC Control System - Room1 Node
COM10 - ESP32 Development Board
==================================================
[wc_male_01] Starting Room1 ESP32 Node...
[wc_male_01] Device ID: 30aea4123456
[wc_male_01] Testing LED...
[wc_male_01] LED test complete
[wc_male_01] Scanning for WiFi networks...
[wc_male_01] Found networks: ['Michelle', 'Vinternal']
[wc_male_01] Connecting to Michelle...
[wc_male_01] ✅ WiFi connected to Michelle!
[wc_male_01] IP address: 192.168.100.200
[wc_male_01] MQTT Client ID: wc_male_01_30aea412
[wc_male_01] Connecting to MQTT broker at 192.168.100.72:1883...
[wc_male_01] ✅ MQTT connected!
[wc_male_01] 📡 Subscribed to: wc/wc_male_01/command
[wc_male_01] 📤 Status published
[wc_male_01] 🎉 Room1 ESP32 Node is ready!
[wc_male_01] 💡 LED will blink when flush command is received
[wc_male_01] 🌐 Send commands to: wc/wc_male_01/command
[wc_male_01] 💓 Heartbeat sent (loop: 1000)
```

### Test Web Dashboard:
1. **Open Flask app:** http://localhost:5000
2. **Check Room1 status:** Should show "online" 
3. **Click Room1 FLUSH button**
4. **Watch ESP32:** LED should blink for 5 seconds

### Expected Response When FLUSH Pressed:
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
[wc_male_01] ⏹️ Stopping all operations...
[wc_male_01] 📤 Response sent: stop - SUCCESS
```

## 🐛 Troubleshooting

### Problem: ESP32 not connecting to WiFi
**Solutions:**
- Check WiFi credentials in code
- Ensure WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
- Move ESP32 closer to router
- Check serial output for error messages

### Problem: MQTT connection failed
**Solutions:**
- Verify PC IP address in `MQTT_BROKER` setting
- Check if Flask app is running (MQTT broker)
- Verify ESP32 and PC are on same network
- Check firewall settings on PC

### Problem: No response to flush commands
**Solutions:**
- Check if node appears as "online" in dashboard
- Verify node_id matches: `wc_male_01`
- Check serial output when button is pressed
- Restart ESP32 and try again

### Problem: Upload fails to COM10
**Solutions:**
- Check if COM10 is correct port in Device Manager
- Install ESP32 USB drivers
- Try different USB cable
- Reset ESP32 and try again

## 🔍 Manual MQTT Testing

You can also test manually using MQTT client:

### Send flush command:
```bash
# Topic: wc/wc_male_01/command
# Payload: {"action": "flush"}
```

### Check status:
```bash
# Subscribe to: wc/wc_male_01/status
# Subscribe to: wc/wc_male_01/response
```

## ✅ Success Criteria

Your Room1 ESP32 node is working correctly when:
- [x] ESP32 connects to WiFi automatically
- [x] ESP32 connects to MQTT broker
- [x] Node appears as "online" in web dashboard
- [x] Built-in LED blinks when Room1 FLUSH is pressed
- [x] LED stops blinking after 5 seconds
- [x] Serial monitor shows all messages clearly

## 📂 File Locations

```
ESP32_nodes/
├── room1_test.py           # Simplified test version for COM10
├── room1/main.py           # Full production version
├── lib/umqtt/simple.py     # MQTT library to upload
└── README.md               # Complete setup guide
```

## 🎯 Next Steps

After successful Room1 testing:
1. **Add relay module** for actual actuator control
2. **Set up Room2** ESP32 (COM11, etc.)
3. **Test all 4 nodes** together
4. **Connect physical actuators** (water valves, pumps)
5. **Deploy in actual locations**

---

**Ready to test!** Connect your ESP32 to COM10 and follow the steps above.
