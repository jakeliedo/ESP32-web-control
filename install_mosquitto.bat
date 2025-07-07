@echo off
REM Install Mosquitto MQTT Broker for Windows
REM WC Control System - MQTT Setup

echo 🦟 Mosquitto MQTT Broker Installer
echo ===================================

REM Check if already installed
where mosquitto >nul 2>&1
if not errorlevel 1 (
    echo ✅ Mosquitto is already installed!
    mosquitto -h | findstr "version" 2>nul || echo Version info not available
    echo.
    echo 🚀 Starting Mosquitto service...
    sc query mosquitto | find "RUNNING" >nul 2>&1
    if errorlevel 1 (
        net start mosquitto >nul 2>&1 && echo ✅ Mosquitto started successfully! || echo ⚠️ Could not start service automatically
    ) else (
        echo ✅ Mosquitto is already running!
    )
    goto :test_connection
)

echo 📋 Mosquitto not found. Attempting installation...
echo.

REM Method 1: Try Chocolatey
echo 🍫 Checking for Chocolatey...
where choco >nul 2>&1
if not errorlevel 1 (
    echo ✅ Chocolatey found! Installing Mosquitto...
    choco install mosquitto -y
    if not errorlevel 1 (
        echo ✅ Mosquitto installed successfully via Chocolatey!
        goto :start_service
    ) else (
        echo ❌ Chocolatey installation failed.
    )
)

REM Method 2: Try WinGet (Windows 10/11)
echo 📦 Checking for WinGet...
where winget >nul 2>&1
if not errorlevel 1 (
    echo ✅ WinGet found! Installing Mosquitto...
    winget install mosquitto.mosquitto --accept-package-agreements --accept-source-agreements
    if not errorlevel 1 (
        echo ✅ Mosquitto installed successfully via WinGet!
        goto :start_service
    ) else (
        echo ❌ WinGet installation failed.
    )
)

REM Method 3: Try Scoop
echo 🥄 Checking for Scoop...
where scoop >nul 2>&1
if not errorlevel 1 (
    echo ✅ Scoop found! Installing Mosquitto...
    scoop install mosquitto
    if not errorlevel 1 (
        echo ✅ Mosquitto installed successfully via Scoop!
        goto :start_service
    ) else (
        echo ❌ Scoop installation failed.
    )
)

REM Method 4: Manual download and install
echo 📥 Attempting direct download...
echo.
echo 🌐 Downloading Mosquitto installer...

REM Create temp directory
set TEMP_DIR=%TEMP%\mosquitto_install
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"
cd /d "%TEMP_DIR%"

REM Download using PowerShell (available on Windows 7+)
echo Downloading from mosquitto.org...
powershell -Command "& {
    try {
        $url = 'https://mosquitto.org/files/binary/win64/mosquitto-2.0.18-install-windows-x64.exe'
        $output = 'mosquitto-installer.exe'
        Write-Host 'Downloading Mosquitto installer...'
        Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing
        if (Test-Path $output) {
            Write-Host '✅ Download completed!'
            exit 0
        } else {
            Write-Host '❌ Download failed!'
            exit 1
        }
    } catch {
        Write-Host '❌ Download error:' $_.Exception.Message
        exit 1
    }
}"

if exist "mosquitto-installer.exe" (
    echo 📦 Installing Mosquitto...
    echo ⚠️ You may need to approve the installation in the next dialog.
    start /wait mosquitto-installer.exe /S
    
    REM Wait a moment for installation to complete
    timeout /t 3 /nobreak >nul
    
    REM Check if installation succeeded
    where mosquitto >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Mosquitto installed successfully!
        goto :start_service
    ) else (
        echo ❌ Installation may have failed.
    )
) else (
    echo ❌ Could not download Mosquitto installer.
    goto :manual_instructions
)

:start_service
echo.
echo 🚀 Starting Mosquitto service...

REM Try to install and start as Windows service
sc create mosquitto binPath= "\"C:\Program Files\mosquitto\mosquitto.exe\" -c \"C:\Program Files\mosquitto\mosquitto.conf\"" DisplayName= "Mosquitto MQTT Broker" start= auto >nul 2>&1

REM Start the service
net start mosquitto >nul 2>&1
if not errorlevel 1 (
    echo ✅ Mosquitto service started successfully!
) else (
    echo ⚠️ Could not start as service. Trying manual start...
    start /b mosquitto -c "C:\Program Files\mosquitto\mosquitto.conf" >nul 2>&1
    timeout /t 2 /nobreak >nul
    echo ℹ️ Mosquitto started manually.
)

:test_connection
echo.
echo 🧪 Testing Mosquitto connection...
timeout /t 2 /nobreak >nul

REM Test with mosquitto_pub/sub if available
where mosquitto_pub >nul 2>&1
if not errorlevel 1 (
    echo Testing MQTT publish/subscribe...
    
    REM Start subscriber in background
    start /b mosquitto_sub -h localhost -t test/topic >nul 2>&1
    timeout /t 1 /nobreak >nul
    
    REM Test publish
    mosquitto_pub -h localhost -t test/topic -m "test_message" >nul 2>&1
    if not errorlevel 1 (
        echo ✅ MQTT test successful!
    ) else (
        echo ⚠️ MQTT test may have issues.
    )
) else (
    echo ℹ️ MQTT tools not available for testing.
)

echo.
echo 🎉 Mosquitto MQTT Broker Setup Complete!
echo.
echo 📋 Summary:
echo   - Broker: localhost:1883
echo   - Service: mosquitto
echo   - Config: C:\Program Files\mosquitto\mosquitto.conf
echo.
echo 🔧 To manage Mosquitto service:
echo   Start:   net start mosquitto
echo   Stop:    net stop mosquitto
echo   Status:  sc query mosquitto
echo.
goto :end

:manual_instructions
echo.
echo ❌ Automatic installation failed.
echo.
echo 📋 Manual Installation Instructions:
echo.
echo 1. 🍫 Install Chocolatey (recommended):
echo    Visit: https://chocolatey.org/install
echo    Then run: choco install mosquitto
echo.
echo 2. 📦 Install via WinGet (Windows 10/11):
echo    Run: winget install mosquitto.mosquitto
echo.
echo 3. 🌐 Manual Download:
echo    Visit: https://mosquitto.org/download/
echo    Download Windows installer and run it
echo.
echo 4. 🔧 Alternative - Use built-in broker:
echo    The WC Control System includes a built-in MQTT broker
echo    No additional installation required!
echo.

:end
REM Clean up temp files
if exist "%TEMP_DIR%" (
    cd /d "%TEMP%"
    rmdir /s /q "%TEMP_DIR%" >nul 2>&1
)

echo Press any key to continue...
pause >nul
