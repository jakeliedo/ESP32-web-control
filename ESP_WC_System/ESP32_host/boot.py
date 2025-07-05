# This file is executed on every boot (including wake-boot from deepsleep)
import esp
import gc

esp.osdebug(None)  # Turn off vendor debugging messages
gc.collect()       # Run garbage collection