@echo off
echo ==============================
echo ESP32 WC System - Quick Start
echo ==============================

cd /d "b:\Python\MicroPython\ESP_WC_System\PC_host"

echo.
echo 1. Resetting database to clear old data...
python reset_database.py

echo.
echo 2. Starting Flask app...
echo    - Dashboard: http://localhost:5000
echo    - Simple UI: http://localhost:5000/simple
echo.
echo When ESP32 connects, you should see MQTT messages
echo Press Ctrl+C to stop
echo.

python app.py

pause
