@echo off
cls
echo ==========================================
echo   ESP32 WC System - Quick Setup
echo ==========================================
echo.
echo This script will automatically configure
echo the system for your network environment.
echo.
echo What it does:
echo - Detect your IP address
echo - Scan for MQTT broker
echo - Create configuration files
echo - Install Python dependencies
echo - Create startup scripts
echo.
pause

echo.
echo Running network detection...
python detect_network.py

echo.
echo ==========================================
echo   Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit config/network_config.json with WiFi credentials
echo 2. Run start_system.bat to start the web server
echo 3. Deploy ESP32 code if needed
echo.
pause
