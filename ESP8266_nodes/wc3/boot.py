# ESP8266 WC Node Boot Configuration
# This file is executed on every boot (including wake-boot from deepsleep)

import esp
esp.osdebug(None)  # Turn off vendor OS debugging

import gc
import webrepl

# Enable garbage collection
gc.collect()

# Optional: Enable WebREPL for remote debugging (comment out for production)
# webrepl.start()

print("Boot complete - WC Node ready")
