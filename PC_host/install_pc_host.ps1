# PC_host Installer for WC Control System (PowerShell)
Write-Host "=== WC Control System - PC_host Installer (PowerShell) ===" -ForegroundColor Cyan

# 1. Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python chưa được cài. Đang mở trang tải Python 3.11..." -ForegroundColor Yellow
    Start-Process "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    Write-Host "Hãy cài Python, tick Add to PATH, rồi chạy lại script này!" -ForegroundColor Yellow
    pause
    exit
} else {
    Write-Host "Python đã có sẵn." -ForegroundColor Green
}

# 2. Check pip
$pip = python -m pip --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "pip chưa có. Đang cài pip..." -ForegroundColor Yellow
    python -m ensurepip --upgrade
}

# 3. Cài đặt Mosquitto MQTT Broker
$mosquitto = Get-Command mosquitto -ErrorAction SilentlyContinue
if (-not $mosquitto) {
    Write-Host "Đang mở trang tải Mosquitto..." -ForegroundColor Yellow
    Start-Process "https://mosquitto.org/files/binary/win64/mosquitto-2.0.18-install-windows-x64.exe"
    Write-Host "Hãy cài Mosquitto (Next, Next, Finish), rồi chạy lại script này nếu cần!" -ForegroundColor Yellow
    pause
}
else {
    Write-Host "Mosquitto đã có sẵn." -ForegroundColor Green
}

# 4. Cài các package Python cần thiết
Set-Location -Path (Split-Path $MyInvocation.MyCommand.Path -Parent)\..
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 5. Hướng dẫn chạy server
Set-Location -Path .\PC_host
Write-Host "\n====================================="
Write-Host " Để chạy server, dùng lệnh:"
Write-Host "    python app.py" -ForegroundColor Yellow
Write-Host " hoặc:"
Write-Host "    start.bat" -ForegroundColor Yellow
Write-Host "====================================="
Write-Host ""
pause
