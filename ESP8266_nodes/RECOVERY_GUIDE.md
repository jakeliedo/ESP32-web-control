# ESP8266 Recovery Guide - Fix Boot Issues

## 🚨 Boot Error Fix for Wemos D1 Mini Pro

### Error Analysis:
```
ets Jan  8 2013,rst cause:4, boot mode:(3,3)
wdt reset
```
- rst cause:4 = Watchdog reset
- boot mode:(3,3) = UART download mode  
- Corrupted firmware or bootloader issue

## 🔧 Recovery Steps

### Step 1: Complete Flash Erase
```bash
# Replace COM3 with your actual port
esptool.py --chip esp8266 --port COM3 erase_flash
```

### Step 2: Flash Bootloader (if needed)
```bash
# Download ESP8266 bootloader first
# From: https://github.com/esp8266/esp8266-wiki/wiki/Boot-Process
esptool.py --chip esp8266 --port COM3 --baud 115200 write_flash 0x0 boot_v1.7.bin
```

### Step 3: Flash MicroPython with specific parameters
```bash
# Use slower baud rate and specific flash parameters
esptool.py --chip esp8266 --port COM3 --baud 115200 write_flash \
  --flash_size=4MB --flash_mode=dio --flash_freq=40m \
  0x0 esp8266-20230426-v1.20.0.bin
```

### Step 4: Alternative flash method (if above fails)
```bash
# Try with default reset parameters
esptool.py --chip esp8266 --port COM3 \
  --before default_reset --after hard_reset \
  --baud 115200 write_flash 0x0 firmware.bin
```

## 🔄 If Still Failing:

### Method 1: Manual Boot Mode
1. Hold FLASH button on Wemos D1 Mini Pro
2. Press and release RESET button  
3. Release FLASH button
4. Run esptool command immediately

### Method 2: Different Baud Rates
```bash
# Try even slower
esptool.py --chip esp8266 --port COM3 --baud 57600 erase_flash

# Or try faster (if USB cable is good)
esptool.py --chip esp8266 --port COM3 --baud 921600 erase_flash
```

### Method 3: Check Hardware
- Try different USB cable
- Check if D1 Mini Pro has sufficient power
- Ensure clean connections

## 🧪 Test After Recovery

### 1. Check with esptool
```bash
esptool.py --chip esp8266 --port COM3 chip_id
esptool.py --chip esp8266 --port COM3 flash_id
```

### 2. Connect via Terminal
- Open serial terminal at 115200 baud
- Press Ctrl+C to get Python prompt
- Should see: >>>

### 3. Basic Test
```python
>>> print("Hello World")
>>> import machine
>>> led = machine.Pin(2, machine.Pin.OUT)
>>> led.value(0)  # Turn on LED
```

## 📋 Required Files

Download these files:
1. **MicroPython firmware**: esp8266-20230426-v1.20.0.bin
   - From: https://micropython.org/download/esp8266/

2. **ESP8266 bootloader** (if needed): boot_v1.7.bin  
   - From: https://github.com/esp8266/esp8266-wiki/wiki/Boot-Process

## ⚠️ Last Resort: AT Firmware
If MicroPython still fails, try flashing AT firmware first, then MicroPython:
```bash
# Flash AT firmware to test hardware
esptool.py --chip esp8266 --port COM3 write_flash 0x0 ESP8266_AT_bin_v2.2.1.0.bin
```
