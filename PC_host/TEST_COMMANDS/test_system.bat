@echo off
echo ================================================
echo            WC Control System - Test
echo ================================================
echo.
echo 1. Starting Flask app in background...
start /B python app.py
timeout /t 3 /nobreak >nul

echo 2. Testing UI requests...
python test_ui_requests.py

echo.
echo 3. Check ESP32 terminal for MQTT messages and LED blinking
echo.
pause
