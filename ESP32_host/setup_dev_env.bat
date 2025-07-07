@echo off
REM ESP32 Remote Control - Development Setup Script
REM This script installs development tools and prepares the environment

echo ===============================================
echo ESP32 Remote Control - Development Setup
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [1/5] Checking Python installation...
python --version

echo.
echo [2/5] Installing development dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

echo.
echo [3/5] Checking ESP32 connection...
echo Please ensure ESP32 is connected via USB
echo Press any key when ready...
pause >nul

REM Try to detect ESP32 port
echo Scanning for ESP32...
python -c "
import serial.tools.list_ports
ports = serial.tools.list_ports.comports()
esp_ports = []
for port in ports:
    if 'USB' in port.description or 'Serial' in port.description:
        esp_ports.append(port.device)
        
if esp_ports:
    print(f'Found potential ESP32 ports: {esp_ports}')
    print(f'Recommended port: {esp_ports[0]}')
else:
    print('No USB serial ports found')
    print('Please check ESP32 connection')
"

echo.
echo [4/5] Development environment setup...
echo Creating project structure...

if not exist "logs" mkdir logs
if not exist "backup" mkdir backup
if not exist "docs" mkdir docs

echo.
echo [5/5] Setup verification...
echo Checking esptool installation...
esptool.py version
if errorlevel 1 (
    echo WARNING: esptool not working properly
    echo Try: pip install --upgrade esptool
)

echo.
echo Checking ampy installation...
ampy --help >nul 2>&1
if errorlevel 1 (
    echo WARNING: ampy not working properly
    echo Try: pip install --upgrade adafruit-ampy
)

echo.
echo ===============================================
echo Setup completed successfully!
echo ===============================================
echo.
echo Next steps:
echo 1. Flash MicroPython firmware to ESP32:
echo    esptool.py --chip esp32 --port COM3 erase_flash
echo    esptool.py --chip esp32 --port COM3 write_flash -z 0x1000 firmware.bin
echo.
echo 2. Upload project files to ESP32:
echo    python upload_project.py
echo.
echo 3. Configure WiFi and MQTT in config.py
echo.
echo 4. Test the system:
echo    python -c "import test_system; test_system.run_all_tests()"
echo.
echo For detailed instructions, see SETUP_GUIDE.md
echo.
pause
