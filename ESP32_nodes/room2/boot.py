# boot.py -- run on boot-up
# ESP32 Room2 Node Boot Configuration

import esp
import gc
import webrepl
from machine import unique_id
import ubinascii

# Disable ESP debug output
esp.osdebug(None)

# Print boot information
print("ESP32 Room 2 Node - Boot Complete")
print(f"Device ID: {ubinascii.hexlify(unique_id()).decode()}")
print("Starting main.py...")

# Enable garbage collection
gc.enable()

# Optional: Enable WebREPL for remote debugging
# webrepl.start()

print("ESP32 Room2 Node - Boot Complete")
print("Starting main.py...")
