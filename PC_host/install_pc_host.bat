@echo off
REM =====================================
REM  WC Control System - PC_host Installer
REM  Tự động cài Python, pip, Mosquitto, các package cần thiết
REM =====================================

REM 1. Kiểm tra/cài đặt Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python chưa được cài. Đang tải Python 3.11...
    powershell -Command "Start-Process 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -Wait"
    echo Hãy cài Python, tick Add to PATH, rồi chạy lại script này!
    pause
    exit /b
) else (
    echo Python đã có sẵn.
)

REM 2. Kiểm tra/cài đặt pip
python -m pip --version >nul 2>nul
if %errorlevel% neq 0 (
    echo pip chưa có. Đang cài pip...
    python -m ensurepip --upgrade
)

REM 3. Cài đặt Mosquitto MQTT Broker
where mosquitto >nul 2>nul
if %errorlevel% neq 0 (
    echo Đang tải Mosquitto...
    powershell -Command "Start-Process 'https://mosquitto.org/files/binary/win64/mosquitto-2.0.18-install-windows-x64.exe' -Wait"
    echo Hãy cài Mosquitto (Next, Next, Finish), rồi chạy lại script này nếu cần!
    pause
) else (
    echo Mosquitto đã có sẵn.
)

REM 4. Cài các package Python cần thiết
cd /d %~dp0..
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM 5. Hướng dẫn chạy server
cd PC_host
@echo.
@echo =====================================
@echo  Để chạy server, dùng lệnh:
@echo    python app.py
@echo hoặc:
@echo    start.bat
@echo =====================================
@echo.
pause
