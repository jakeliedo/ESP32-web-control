# ESP32 Web Control - PC Host Auto Installer (Windows)
# Run this script as Administrator (Run as Administrator)
# Note: Make sure you have extracted the project folder structure correctly before running

# Check for Administrator privileges
If (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "This script must be run as Administrator. Relaunching with admin rights..."
    Start-Process powershell "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host "==== ESP32 Web Control - PC Host Installer ====" -ForegroundColor Cyan

# 1. Check for official Python 3.13.5 version (fixed)
Write-Host "[1/7] Checking for Python 3..."
$python = Get-Command python -ErrorAction SilentlyContinue
$pythonVersion = $null
if ($python) {
    $pythonVersion = & $python.Source --version 2>&1
}

if (-not $python -or $pythonVersion -notmatch "3\\.") {
    Write-Host "[!] Python 3 is not installed or not found in PATH. Downloading Python 3.13.5..." -ForegroundColor Yellow
    $pyInstaller = "python-3.13.5-amd64.exe"
    $pyUrl = "https://www.python.org/ftp/python/3.13.5/python-3.13.5-amd64.exe"
    Write-Host "[i] Will download and install Python version: 3.13.5 from $pyUrl" -ForegroundColor Yellow
    Invoke-WebRequest -Uri $pyUrl -OutFile $pyInstaller
    Write-Host "[+] Installing Python 3.13.5..." -ForegroundColor Cyan
    Start-Process -Wait -FilePath ".\$pyInstaller" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0"
    Remove-Item ".\$pyInstaller"
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        Write-Host "[X] ERROR: Python 3 not found after installation!" -ForegroundColor Red
        exit 1
    }
    Write-Host "[+] Python 3.13.5 installed successfully!" -ForegroundColor Green
} else {
    Write-Host "[+] Found Python: $($python.Source) ($pythonVersion)" -ForegroundColor Green
}

# 2. Create venv if not exists
if (-not (Test-Path "venv")) {
    Write-Host "[+] Creating virtual environment (venv)..." -ForegroundColor Cyan
    & $python.Source -m venv venv
}

# 3. Activate venv and install requirements.txt
$venvPython = "venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "[X] ERROR: python.exe not found in venv!" -ForegroundColor Red
    exit 1
}
Write-Host "[+] Installing Python packages from requirements.txt..." -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

# 4. Install Mosquitto if not exists
$mosqExe = "C:\\Program Files\\mosquitto\\mosquitto.exe"
$mosqInstallerName = "mosquitto-2.0.18-install-windows-x64.exe"
$mosqInstallerAlt = "mosq_installer.exe"
$mosqInstallerPath = Join-Path $PSScriptRoot $mosqInstallerName
$mosqInstallerAltPath = Join-Path $PSScriptRoot $mosqInstallerAlt

if (-not (Test-Path $mosqExe)) {
    Write-Host "[!] Mosquitto is not installed. Checking for installer file..." -ForegroundColor Yellow
    if (Test-Path $mosqInstallerPath) {
        Write-Host "[+] Found Mosquitto installer: $mosqInstallerPath" -ForegroundColor Green
        $installerToUse = $mosqInstallerPath
    } elseif (Test-Path $mosqInstallerAltPath) {
        Write-Host "[+] Found Mosquitto installer: $mosqInstallerAltPath" -ForegroundColor Green
        $installerToUse = $mosqInstallerAltPath
    } else {
        Write-Host "[!] Mosquitto installer not found, downloading..." -ForegroundColor Yellow
        $mosqUrl = "https://mosquitto.org/files/binary/win64/mosquitto-2.0.18-install-windows-x64.exe"
        Invoke-WebRequest -Uri $mosqUrl -OutFile $mosqInstallerName
        $installerToUse = $mosqInstallerPath
    }
    Start-Process -Wait -FilePath $installerToUse -ArgumentList "/S"
    if ($installerToUse -eq $mosqInstallerAltPath) { Remove-Item $mosqInstallerAltPath -ErrorAction SilentlyContinue }
    # Do not remove official installer
    if (-not (Test-Path $mosqExe)) {
        Write-Host "[X] ERROR: Mosquitto not found after installation!" -ForegroundColor Red
        exit 1
    }
    Write-Host "[+] Mosquitto installed successfully!" -ForegroundColor Green
    # Check if Mosquitto broker is running
    $mosqProcess = Get-Process -Name "mosquitto" -ErrorAction SilentlyContinue
    if ($mosqProcess) {
        Write-Host "[+] Mosquitto MQTT broker is running." -ForegroundColor Green
    } else {
        Write-Host "[!] Mosquitto MQTT broker is NOT running. You may need to start it manually." -ForegroundColor Yellow
    }
} else {
    Write-Host "[+] Found Mosquitto: $mosqExe" -ForegroundColor Green
}

# 5. Add Mosquitto to PATH if needed
$mosqPath = "C:\\Program Files\\mosquitto"
$envPath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
if ($envPath -notlike "*${mosqPath}*") {
    Write-Host "[+] Adding Mosquitto to system PATH..." -ForegroundColor Cyan
    [Environment]::SetEnvironmentVariable("Path", "$envPath;${mosqPath}", "Machine")
    Write-Host "[+] Mosquitto added to PATH. Please restart your computer or log out for PATH to take effect." -ForegroundColor Yellow
}

# 6. Configure firewall for Mosquitto
Write-Host "[+] Configuring firewall for Mosquitto..." -ForegroundColor Cyan
if (-not (Get-NetFirewallRule -DisplayName "Mosquitto MQTT" -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName "Mosquitto MQTT" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 1883
}

Write-Host "==============================="
Write-Host "Installation complete!"
Write-Host "- To run the server:"
Write-Host "    .\venv\Scripts\activate"
Write-Host "    python app.py"
Write-Host "==============================="
Write-Host "If you encounter errors, please check your Python version, Mosquitto, or contact support."

Write-Host "\nWould you like to start the app now? Press ENTER to start 'python app.py' in a new window, or close this window to skip." -ForegroundColor Cyan
[void][System.Console]::ReadLine()
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'python app.py'
Write-Host "\n[INFO] Waiting for app.py to start..."
Write-Host "\nTo check node connect to broker, press Enter." -ForegroundColor Yellow
[void][System.Console]::ReadLine()
Write-Host "\n[INFO] Showing all connections to Mosquitto broker (port 1883):" -ForegroundColor Cyan
cmd.exe /c "netstat -an | findstr :1883"
Write-Host "\n[INFO] If you see connections in the list above, your nodes are connected to the MQTT broker."
Write-Host "[INFO] If the list is empty, check that your nodes and app.py are running and configured correctly."
