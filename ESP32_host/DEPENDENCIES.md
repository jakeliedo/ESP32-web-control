# ESP32 Remote Control - Complete Dependencies Guide

## 📋 Overview
This document lists all dependencies, requirements, and setup files for the ESP32 Remote Control project.

## 🖥️ PC Development Requirements (requirements.txt)

### Core Tools
```
esptool>=4.5.1              # Flash MicroPython firmware
adafruit-ampy>=1.1.0        # Upload files to ESP32
mpfshell>=0.9.2             # Alternative file manager
```

### Code Quality
```
pylint>=2.15.0              # Code analysis
black>=22.0.0               # Code formatting
isort>=5.10.0               # Import sorting
```

### Testing & Communication
```
paho-mqtt>=1.6.1            # MQTT testing
pyserial>=3.5               # Serial communication
requests>=2.28.0            # HTTP testing
ping3>=4.0.0                # Network testing
netifaces>=0.11.0           # Network interfaces
```

### Documentation
```
markdown>=3.4.0             # Markdown processing
mkdocs>=1.4.0               # Documentation generator (optional)
```

## 🔧 ESP32 MicroPython Libraries (micropython_libs.txt)

### Built-in Libraries (Pre-installed)
- `machine` - Hardware control (GPIO, SPI, I2C)
- `network` - WiFi networking
- `time` - Time functions
- `json` - JSON parsing
- `ubinascii` - Binary/ASCII conversion
- `gc` - Garbage collection
- `os/uos` - Operating system interface

### External Libraries (Need to upload)
- `umqtt.simple` - MQTT client
  - Location: `lib/umqtt/simple.py`
  - Source: micropython-lib

### Custom Project Libraries
- `lib/st7789p3.py` - ST7789P3 display driver
- `lib/simple_ui.py` - UI framework
- `lib/remote_control.py` - Remote control logic

## 📁 Project Files Structure
```
ESP32_host/
├── main.py                 # Main application
├── boot.py                 # Boot configuration  
├── config.py               # System configuration
├── requirements.txt        # PC development deps
├── micropython_libs.txt    # MicroPython library info
├── pymakr.conf            # VS Code Pymakr config
├── lib/
│   ├── umqtt/
│   │   └── simple.py      # MQTT client
│   ├── st7789p3.py        # Display driver
│   ├── simple_ui.py       # UI framework
│   └── remote_control.py  # Remote logic
├── test_system.py         # System testing
├── upload_project.py      # Auto upload script
├── setup_dev_env.bat      # Windows setup script
├── SETUP_GUIDE.md         # Setup instructions
└── README_Remote.md       # Project documentation
```

## 🚀 Installation Steps

### 1. PC Development Environment
```bash
# Install Python 3.8+
# Then install dependencies:
pip install -r requirements.txt
```

### 2. ESP32 Firmware
```bash
# Flash MicroPython firmware
esptool.py --chip esp32 --port COM3 erase_flash
esptool.py --chip esp32 --port COM3 write_flash -z 0x1000 esp32-firmware.bin
```

### 3. Upload Project Files

#### Option A: Automatic Upload
```bash
python upload_project.py
```

#### Option B: Manual with ampy
```bash
ampy --port COM3 mkdir lib
ampy --port COM3 mkdir lib/umqtt
ampy --port COM3 put lib/umqtt/simple.py lib/umqtt/simple.py
ampy --port COM3 put lib/st7789p3.py lib/st7789p3.py
ampy --port COM3 put lib/simple_ui.py lib/simple_ui.py
ampy --port COM3 put lib/remote_control.py lib/remote_control.py
ampy --port COM3 put config.py config.py
ampy --port COM3 put boot.py boot.py
ampy --port COM3 put main.py main.py
```

#### Option C: VS Code + Pymakr
1. Install Pymakr extension
2. Use `pymakr.conf` configuration
3. Sync project with ESP32

#### Option D: Thonny IDE
1. Configure for MicroPython (ESP32)
2. Upload files via File menu

## 🔧 Hardware Requirements

### ESP32 Board
- ESP32 DevKit v1 (30 pins recommended)
- USB cable for programming
- 3.3V/5V power supply

### Display
- ST7789P3 3.2" TFT (240x320 pixels)
- SPI interface
- RGB565 color support

### Input Controls
- 5x Tactile push buttons
- Pull-up resistors (internal used)

### Status Indicators
- 1x LED + 220Ω resistor

### Connections
```
ESP32 GPIO → Component
GPIO18     → Display SCLK
GPIO23     → Display MOSI
GPIO5      → Display CS
GPIO2      → Display DC
GPIO4      → Display RST
GPIO15     → Display BL
GPIO32-27  → Buttons
GPIO22     → Status LED
```

## 🌐 Network Requirements

### WiFi
- 2.4GHz WiFi network
- WPA/WPA2 security
- Internet access (for MQTT)

### MQTT Broker
- PC host running mosquitto
- Port 1883 (default)
- Same network as ESP32

## 🧪 Testing & Verification

### System Test
```python
import test_system
test_system.run_all_tests()
```

### Component Tests
- Hardware: Buttons, LED, Display
- Network: WiFi connectivity
- MQTT: Broker communication
- Integration: Full system test

## 📚 Documentation Files

- `README_Remote.md` - Complete project documentation
- `SETUP_GUIDE.md` - Quick setup instructions
- `micropython_libs.txt` - Library information
- `DEPENDENCIES.md` - This file

## 🔍 Troubleshooting

### Common Issues
1. **Display not working**: Check SPI connections
2. **WiFi connection failed**: Verify network credentials
3. **MQTT connection failed**: Check broker IP and firewall
4. **Upload failed**: Check ESP32 port and drivers

### Debug Tools
- Serial monitor (115200 baud)
- ESP32 debug prints
- MQTT client testing
- Network connectivity tools

## 📞 Support

For issues:
1. Check hardware connections
2. Verify configuration in `config.py`
3. Monitor serial output for errors
4. Test individual components
5. Refer to setup guides

Happy coding! 🎉
