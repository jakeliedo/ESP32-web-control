# This file is executed on every boot (including wake-boot from deepsleep)
import esp
import gc
import time

# Turn off vendor debugging messages
esp.osdebug(None)

# Run garbage collection
gc.collect()

# Print boot information
print("\n" + "=" * 50)
print("🚀 ESP32 WC Control System")
print("📅 Boot Time:", time.localtime())
print("💾 Free Memory:", gc.mem_free(), "bytes")
print("=" * 50)

# Auto-start main application
try:
    print("🔄 Auto-starting main application...")
    import main
except Exception as e:
    print(f"❌ Failed to start main application: {e}")
    print("💡 You can manually run: import main")