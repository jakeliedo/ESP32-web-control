# ESP32 WC Control System - Node Setup Guide

## Overview
This guide will help you set up 4 ESP32 development boards as actuator nodes for your WC control system.

## System Architecture
```
[Web Browser] → [Flask App] → [MQTT Broker] → [ESP32 Nodes]
     ↑              ↑              ↑              ↓
[Dashboard UI] [PC Database] [Message Hub] [Physical Actuators]
```

## Hardware Requirements (per ESP32 node)

### Required Components:
1. **ESP32 Development Board** (ESP32 DevKit v1 or similar)
2. **5V Relay Module** (for controlling actuators)
3. **External LED** (status indicator - optional)
4. **Jumper Wires** (male-to-male and male-to-female)
5. **Breadboard** (for prototyping)
6. **Power Supply** (USB cable or external 5V power)

### Actuator Options:
- **Water solenoid valve** (12V DC)
- **Water pump** (12V DC)
- **Servo motor** (for mechanical flushing)
- **LED strip** (for visual indication)

## GPIO Pin Assignments

### Standard Pinout for All Nodes:
```
GPIO 2  → Built-in LED (status indication)
GPIO 5  → Relay control (to actuator)
GPIO 18 → External status LED (optional)
GND     → Common ground
3.3V    → Power for relay module (if compatible)
```

### Relay Module Connections:
```
ESP32 GPIO 5 → Relay IN
ESP32 GND    → Relay GND
ESP32 3.3V   → Relay VCC (or use external 5V)

Relay NO (Normally Open) → Actuator positive
Relay COM (Common)       → Power supply positive
Actuator negative        → Power supply negative
```

## Software Setup

### 1. Install MicroPython
1. Download and install **Thonny IDE** or **esptool**
2. Flash MicroPython firmware to ESP32:
   ```bash
   esptool.py --chip esp32 --port COM3 erase_flash
   esptool.py --chip esp32 --port COM3 write_flash -z 0x1000 esp32-micropython.bin
   ```

### 2. Install MQTT Library
Copy the `umqtt` library to your ESP32:
- Copy `umqtt/simple.py` to the ESP32's `/lib/umqtt/simple.py`

### 3. Node Configuration
Each ESP32 needs a unique configuration:

#### Room1 (Male WC) - `main.py`:
```python
NODE_ID = 'wc_male_01'
NODE_TYPE = 'male'
ROOM_NAME = 'Room1'
```

#### Room2 (Male WC) - `main.py`:
```python
NODE_ID = 'wc_male_02'
NODE_TYPE = 'male'
ROOM_NAME = 'Room2'
```

#### Room3 (Female WC) - `main.py`:
```python
NODE_ID = 'wc_female_01'
NODE_TYPE = 'female'
ROOM_NAME = 'Room3'
```

#### Room4 (Female WC) - `main.py`:
```python
NODE_ID = 'wc_female_02'
NODE_TYPE = 'female'
ROOM_NAME = 'Room4'
```

### 4. Update Network Configuration
In each `main.py`, update the WiFi credentials:
```python
# Add your WiFi networks
if "YourWiFiName" in networks:
    wlan.connect('YourWiFiName', 'YourWiFiPassword')
```

### 5. Update MQTT Broker IP
Update the MQTT broker IP to match your PC:
```python
MQTT_BROKER = '192.168.1.100'  # Replace with your PC's IP address
```

## Physical Setup Steps

### Step 1: Basic ESP32 Setup
1. Connect ESP32 to computer via USB
2. Upload the appropriate `main.py` for each room
3. Test basic connectivity (WiFi + MQTT)

### Step 2: Relay Module Connection
1. Connect relay module to ESP32 as per pinout above
2. Test relay switching with simple commands
3. Verify relay LED indicators work correctly

### Step 3: Actuator Integration
1. Connect your chosen actuator to relay output
2. Ensure proper power supply for actuator
3. Test actuator operation with relay control

### Step 4: Status Indicators
1. Connect external LED to GPIO 18 (optional)
2. Test LED blinking during flush operations
3. Verify built-in LED status indication

## MQTT Topics Structure

### Command Topics (ESP32 subscribes):
- `wc/wc_male_01/command` → Room1 commands
- `wc/wc_male_02/command` → Room2 commands  
- `wc/wc_female_01/command` → Room3 commands
- `wc/wc_female_02/command` → Room4 commands

### Status Topics (ESP32 publishes):
- `wc/wc_male_01/status` → Room1 status updates
- `wc/wc_male_02/status` → Room2 status updates
- `wc/wc_female_01/status` → Room3 status updates
- `wc/wc_female_02/status` → Room4 status updates

### Response Topics (ESP32 publishes):
- `wc/wc_male_01/response` → Room1 command responses
- `wc/wc_male_02/response` → Room2 command responses
- `wc/wc_female_01/response` → Room3 command responses
- `wc/wc_female_02/response` → Room4 command responses

## Testing Procedure

### 1. Individual Node Testing
1. Upload code to ESP32
2. Open serial monitor in Thonny
3. Verify WiFi connection
4. Verify MQTT connection
5. Test relay operation manually

### 2. System Integration Testing
1. Start PC Flask application
2. Connect all 4 ESP32 nodes
3. Verify all nodes appear as "online" in dashboard
4. Test flush commands from web interface
5. Verify actuator responses

### 3. End-to-End Testing
1. Open dashboard in web browser
2. Click flush button for each room
3. Verify:
   - Relay activates immediately
   - Status LED blinks for 5 seconds
   - Actuator operates correctly
   - Relay auto-deactivates after 5 seconds
   - Dashboard shows event in real-time

## Troubleshooting

### Common Issues:

#### WiFi Connection Problems:
- Check WiFi credentials in code
- Verify WiFi network is 2.4GHz (ESP32 doesn't support 5GHz)
- Check signal strength at ESP32 location

#### MQTT Connection Problems:
- Verify MQTT broker IP address
- Check firewall settings on PC
- Ensure MQTT broker is running on PC

#### Relay Not Activating:
- Check GPIO pin connections
- Verify relay module power supply
- Test with multimeter for signal on GPIO 5

#### Actuator Not Working:
- Check actuator power supply requirements
- Verify relay switching (listen for click)
- Check actuator wiring connections

## Advanced Features

### Optional Enhancements:
1. **Sensor Integration**: Add occupancy sensors
2. **Power Monitoring**: Monitor actuator power consumption
3. **Temperature Sensing**: Add environment monitoring
4. **Water Flow Sensing**: Monitor flush effectiveness
5. **Battery Backup**: Add UPS for critical operations

### Future Expansion:
1. **Mobile App**: Direct ESP32 to smartphone communication
2. **Voice Control**: Integration with smart speakers
3. **Scheduling**: Automatic maintenance cycles
4. **Analytics**: Usage pattern analysis
5. **Alert System**: Email/SMS notifications for issues

## Node File Structure
```
ESP32_nodes/
├── room1/
│   └── main.py        # Room1 (Male WC) code
├── room2/
│   └── main.py        # Room2 (Male WC) code
├── room3/
│   └── main.py        # Room3 (Female WC) code
├── room4/
│   └── main.py        # Room4 (Female WC) code
└── lib/
    └── umqtt/
        └── simple.py  # MQTT library (copy to each ESP32)
```

## Safety Considerations

1. **Electrical Safety**:
   - Use proper isolation for AC loads
   - Install circuit breakers
   - Use waterproof enclosures in wet areas

2. **Water Safety**:
   - Install overflow protection
   - Use pressure relief valves
   - Regular maintenance schedules

3. **System Reliability**:
   - Implement watchdog timers
   - Add manual override switches
   - Regular backup procedures

---

This completes your ESP32 node setup. Each node will automatically connect to WiFi, register with the MQTT broker, and respond to flush commands from your web interface!
