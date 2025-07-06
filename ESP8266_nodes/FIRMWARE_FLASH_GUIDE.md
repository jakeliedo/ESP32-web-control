# Firmware Flash Guide for Wemos D1 Mini Pro

## 📋 Required Tools & Files

### 1. Download MicroPython Firmware
- Visit: https://micropython.org/download/esp8266/
- Download latest stable firmware: `esp8266-*.bin`
- Recommended: esp8266-20230426-v1.20.0.bin (or newer)

### 2. Install esptool
```bash
pip install esptool
```

### 3. Install USB Driver
- CH340 driver (if using CH340 chip)
- CP2102 driver (if using CP2102 chip)

## 🔌 Hardware Setup

### 1. Connect Wemos D1 Mini Pro
- Connect via USB cable
- Check Device Manager for COM port (e.g., COM3, COM4...)
- No need to press any buttons for flashing

## ⚡ Firmware Flashing Commands

### Step 1: Erase Flash (Important!)
```bash
esptool.py --chip esp8266 --port COM3 erase_flash
```

### Step 2: Flash MicroPython Firmware
```bash
esptool.py --chip esp8266 --port COM3 --baud 460800 write_flash --flash_size=detect 0 esp8266-20230426-v1.20.0.bin
```

### Step 3: Verify Installation
```bash
esptool.py --chip esp8266 --port COM3 chip_id
```

## 🧪 Test MicroPython

### 1. Connect via Serial Terminal
- Use PuTTY, Tera Term, or VS Code terminal
- Settings: 115200 baud, 8N1
- Press Ctrl+C to get Python prompt: >>>

### 2. Basic Test
```python
>>> print("Hello MicroPython!")
>>> import machine
>>> led = machine.Pin(2, machine.Pin.OUT)
>>> led.value(0)  # Turn on LED
>>> led.value(1)  # Turn off LED
```

## 🚨 Troubleshooting

### Common Issues:
1. **"Failed to connect"**: Check COM port, try different USB cable
2. **Permission denied**: Close other programs using COM port
3. **Flash failed**: Try lower baud rate (115200)
4. **Driver issues**: Reinstall USB drivers

### Alternative Commands:
```bash
# Slower but more reliable
esptool.py --chip esp8266 --port COM3 --baud 115200 write_flash --flash_size=detect 0 firmware.bin

# For stubborn devices
esptool.py --chip esp8266 --port COM3 --before default_reset --after hard_reset write_flash 0x0 firmware.bin
```

## ✅ After Flashing Success

### 1. Install required libraries (if needed)
```python
import upip
upip.install('umqtt.simple')
```

### 2. Upload your project files
- Use Thonny, VS Code + Pymakr, or ampy
- Upload main.py, boot.py

### 3. Ready to use!
- Reset ESP8266
- Your code should start automatically
