@echo off
echo ====================================
echo  WC Control System v2.0 - Enhanced UI
echo ====================================
echo.

echo Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo Python found. Checking dependencies...
cd /d "%~dp0"

echo Installing/updating required packages...
pip install flask flask-socketio requests paho-mqtt sqlite3 --quiet

echo.
echo Starting WC Control System...
echo.
echo Available URLs:
echo   Dashboard:  http://localhost:5000/
echo   Events:     http://localhost:5000/events
echo   Analytics:  http://localhost:5000/analytics
echo   Simple UI:  http://localhost:5000/simple
echo.
echo Press Ctrl+C to stop the server
echo ====================================
echo.

python demo.py

echo.
echo Server stopped.
pause
