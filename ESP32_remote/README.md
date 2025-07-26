# ESP32 Remote Control

ESP32-C3 remote control device with DMT touchscreen for controlling WC system nodes via MQTT.

## Features

- **DMT Touchscreen Interface**: 4.3" touchscreen for visual control
- **MQTT Communication**: Connects to same MQTT broker as other nodes
- **Multi-Node Control**: Controls 4 WC nodes (male/female WC 1&2)
- **Real-time Status**: Shows online/offline status of each node
- **Touch Controls**: 4 touch areas (VP2100-2400) to send FLUSH commands
- **WiFi Debug Page**: Shows connection details and MQTT status

## Hardware

- **MCU**: ESP32-C3 Super Mini
- **Display**: DMT48270C43 4.3" touchscreen
- **Communication**: UART (pins 20/21)

## VP Address Mapping

### Main Control Page
- `0x5000`: Page title
- `0x3100-0x3400`: Node status display (4 nodes)
- `0x2100-0x2400`: Touch areas for FLUSH commands
- `0x5400`: Instructions text

### WiFi Debug Page  
- `0x5000`: Page title
- `0x5500`: WiFi SSID
- `0x5600`: IP Address
- `0x5700`: RSSI value
- `0x5800`: MQTT status

### Common Areas
- `0x5100`: WiFi connection status
- `0x5200`: MQTT connection status
- `0x5300`: Last command sent
- `0x1000`: Touch to switch to main page
- `0x1001`: Touch to switch to WiFi debug page

## MQTT Topics

### Subscribed Topics
- `wc/{node_id}/status` - Node status updates
- `wc/{node_id}/response` - Command responses

### Published Topics
- `wc/esp32_remote/status` - Remote control status
- `wc/{node_id}/command` - Flush commands to nodes

## Configuration

WiFi and MQTT settings match room4 configuration:
- **WiFi**: Floor 9 / Vinternal
- **MQTT Broker**: 192.168.20.18:1883

## Controlled Nodes

1. **wc_male_01** (Male WC 1) - VP2100
2. **wc_female_01** (Female WC 1) - VP2200  
3. **wc_male_02** (Male WC 2) - VP2300
4. **wc_female_02** (Female WC 2) - VP2400

## Build & Upload

```bash
pio run -t upload
pio device monitor
```
