@echo off
REM WC Control System - Auto Setup Script for Windows

echo 🚀 WC Control System - Auto Setup
echo ==================================

REM Check Python version
echo 📋 Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not found.
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

python --version
echo.

REM Create virtual environment
echo 🐍 Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created.
) else (
    echo ✅ Virtual environment already exists.
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📚 Installing Python dependencies...
pip install -r requirements.txt

REM Create directories
echo 📁 Creating directories...
if not exist "PC_host\data" mkdir PC_host\data
if not exist "PC_host\logs" mkdir PC_host\logs
if not exist "config" mkdir config

REM Create .env file if not exists
if not exist "PC_host\.env" (
    echo ⚙️ Creating .env configuration file...
    (
        echo # WC Control System Configuration
        echo.
        echo # MQTT Configuration
        echo MQTT_BROKER=localhost
        echo MQTT_PORT=1883
        echo MQTT_USERNAME=
        echo MQTT_PASSWORD=
        echo MQTT_CLIENT_ID=wc_control_pc
        echo.
        echo # Flask Configuration
        echo SECRET_KEY=wc_control_secret_%RANDOM%
        echo DEBUG=True
        echo HOST=0.0.0.0
        echo PORT=5000
        echo.
        echo # Database
        echo DB_PATH=data/wc_system.db
    ) > PC_host\.env
    echo ✅ .env file created with default settings.
) else (
    echo ✅ .env file already exists.
)

REM Check for MQTT broker and install if needed
echo 🔧 Checking MQTT broker...
where mosquitto >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Mosquitto MQTT broker not found.
    echo 🔧 Attempting to install Mosquitto...
    
    REM Check if Chocolatey is available
    where choco >nul 2>&1
    if not errorlevel 1 (
        echo 📦 Installing Mosquitto via Chocolatey...
        choco install mosquitto -y
        if not errorlevel 1 (
            echo ✅ Mosquitto installed successfully via Chocolatey.
            echo 🚀 Starting Mosquitto service...
            net start mosquitto >nul 2>&1 || echo ℹ️ Mosquitto will start automatically.
        ) else (
            echo ❌ Chocolatey installation failed.
            goto :manual_mosquitto
        )
    ) else (
        REM Check if Scoop is available
        where scoop >nul 2>&1
        if not errorlevel 1 (
            echo 📦 Installing Mosquitto via Scoop...
            scoop install mosquitto
            if not errorlevel 1 (
                echo ✅ Mosquitto installed successfully via Scoop.
            ) else (
                echo ❌ Scoop installation failed.
                goto :manual_mosquitto
            )
        ) else (
            REM Check if winget is available (Windows 10/11)
            where winget >nul 2>&1
            if not errorlevel 1 (
                echo 📦 Installing Mosquitto via WinGet...
                winget install mosquitto.mosquitto
                if not errorlevel 1 (
                    echo ✅ Mosquitto installed successfully via WinGet.
                ) else (
                    echo ❌ WinGet installation failed.
                    goto :manual_mosquitto
                )
            ) else (
                goto :manual_mosquitto
            )
        )
    )
    goto :mosquitto_done
    
    :manual_mosquitto
    echo ❌ Could not auto-install Mosquitto.
    echo 📋 Manual installation options:
    echo 1. Download from: https://mosquitto.org/download/
    echo 2. Install Chocolatey first: https://chocolatey.org/install
    echo    Then run: choco install mosquitto
    echo 3. Or use the built-in MQTT broker included with this system
    echo.
    set /p install_choice="Do you want to continue with built-in broker? (y/n): "
    if /i "%install_choice%"=="n" (
        echo Installation cancelled.
        pause
        exit /b 1
    )
    echo ℹ️ Will use built-in MQTT broker.
    
    :mosquitto_done
) else (
    echo ✅ Mosquitto MQTT broker found.
    REM Try to start mosquitto service if not running
    sc query mosquitto | find "RUNNING" >nul 2>&1
    if errorlevel 1 (
        echo 🚀 Starting Mosquitto service...
        net start mosquitto >nul 2>&1 || echo ℹ️ Mosquitto service may need manual start.
    ) else (
        echo ✅ Mosquitto service is already running.
    )
)

REM Test installation
echo 🧪 Testing installation...
cd PC_host

REM Initialize database
echo 🗄️ Initializing database...
python -c "from database import init_database; init_database()" 2>nul || echo Database initialization will happen on first run.

REM Test imports
echo 📋 Testing imports...
python -c "try: import flask, flask_socketio, paho.mqtt.client, requests; print('✅ All required modules imported successfully.'); except ImportError as e: print(f'❌ Import error: {e}'); exit(1)"

echo.
echo 🎉 Setup completed successfully!
echo.
echo 📋 Next steps:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Go to PC_host directory: cd PC_host
echo 3. Start the application: python quick_start.py
echo 4. Open browser: http://localhost:5000
echo.
echo 📚 For more details, see: INSTALLATION_GUIDE.md
echo.
echo 🔧 To customize settings, edit: PC_host\.env

pause
