#!/bin/bash
# WC Control System - Auto Setup Script for macOS/Linux

echo "🚀 WC Control System - Auto Setup"
echo "=================================="

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>/dev/null || echo "Not found")
echo "Python version: $python_version"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

# Create virtual environment
echo "🐍 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created."
else
    echo "✅ Virtual environment already exists."
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p PC_host/data
mkdir -p PC_host/logs
mkdir -p config

# Create .env file if not exists
if [ ! -f "PC_host/.env" ]; then
    echo "⚙️ Creating .env configuration file..."
    cat > PC_host/.env << EOL
# WC Control System Configuration

# MQTT Configuration
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_CLIENT_ID=wc_control_pc

# Flask Configuration
SECRET_KEY=wc_control_secret_$(date +%s)
DEBUG=True
HOST=0.0.0.0
PORT=5000

# Database
DB_PATH=data/wc_system.db
EOL
    echo "✅ .env file created with default settings."
else
    echo "✅ .env file already exists."
fi

# Install MQTT broker (if not installed)
echo "🔧 Checking MQTT broker..."
if command -v mosquitto &> /dev/null; then
    echo "✅ Mosquitto MQTT broker found."
    
    # Check if mosquitto is running
    if pgrep -x "mosquitto" > /dev/null; then
        echo "✅ Mosquitto is already running."
    else
        echo "🚀 Starting Mosquitto..."
        # Try different methods to start mosquitto
        if command -v systemctl &> /dev/null; then
            sudo systemctl start mosquitto 2>/dev/null || mosquitto -d 2>/dev/null || echo "ℹ️ Mosquitto may need manual start."
        elif command -v brew &> /dev/null; then
            brew services start mosquitto 2>/dev/null || mosquitto -d 2>/dev/null || echo "ℹ️ Mosquitto may need manual start."
        else
            mosquitto -d 2>/dev/null || echo "ℹ️ Mosquitto may need manual start."
        fi
    fi
    
elif command -v brew &> /dev/null; then
    echo "📦 Installing Mosquitto via Homebrew..."
    brew install mosquitto
    if [ $? -eq 0 ]; then
        echo "✅ Mosquitto installed successfully via Homebrew."
        echo "🚀 Starting Mosquitto service..."
        brew services start mosquitto
        echo "✅ Mosquitto started."
    else
        echo "❌ Homebrew installation failed."
        echo "ℹ️ Will use built-in MQTT broker."
    fi
    
elif command -v apt-get &> /dev/null; then
    echo "📦 Installing Mosquitto via apt..."
    sudo apt update
    sudo apt install -y mosquitto mosquitto-clients
    if [ $? -eq 0 ]; then
        echo "✅ Mosquitto installed successfully via apt."
        echo "🚀 Starting Mosquitto service..."
        sudo systemctl start mosquitto
        sudo systemctl enable mosquitto
        echo "✅ Mosquitto started and enabled."
    else
        echo "❌ apt installation failed."
        echo "ℹ️ Will use built-in MQTT broker."
    fi
    
elif command -v yum &> /dev/null; then
    echo "📦 Installing Mosquitto via yum..."
    sudo yum install -y mosquitto mosquitto-clients
    if [ $? -eq 0 ]; then
        echo "✅ Mosquitto installed successfully via yum."
        echo "🚀 Starting Mosquitto service..."
        sudo systemctl start mosquitto
        sudo systemctl enable mosquitto
        echo "✅ Mosquitto started and enabled."
    else
        echo "❌ yum installation failed."
        echo "ℹ️ Will use built-in MQTT broker."
    fi
    
elif command -v pacman &> /dev/null; then
    echo "📦 Installing Mosquitto via pacman..."
    sudo pacman -S --noconfirm mosquitto
    if [ $? -eq 0 ]; then
        echo "✅ Mosquitto installed successfully via pacman."
        echo "🚀 Starting Mosquitto service..."
        sudo systemctl start mosquitto
        sudo systemctl enable mosquitto
        echo "✅ Mosquitto started and enabled."
    else
        echo "❌ pacman installation failed."
        echo "ℹ️ Will use built-in MQTT broker."
    fi
    
else
    echo "⚠️ Could not install MQTT broker automatically."
    echo "📋 Manual installation options:"
    echo "  - macOS: brew install mosquitto"
    echo "  - Ubuntu/Debian: sudo apt install mosquitto"
    echo "  - CentOS/RHEL: sudo yum install mosquitto"
    echo "  - Arch Linux: sudo pacman -S mosquitto"
    echo "  - Or use the built-in broker included with this system"
    echo ""
    read -p "Do you want to continue with built-in broker? (y/n): " install_choice
    if [[ "$install_choice" != "y" && "$install_choice" != "Y" ]]; then
        echo "Installation cancelled."
        exit 1
    fi
    echo "ℹ️ Will use built-in MQTT broker."
fi

# Test installation
echo "🧪 Testing installation..."
cd PC_host

# Initialize database
echo "🗄️ Initializing database..."
python -c "from database import init_database; init_database()" 2>/dev/null || echo "Database initialization will happen on first run."

# Test imports
echo "📋 Testing imports..."
python -c "
try:
    import flask, flask_socketio, paho.mqtt.client, requests
    print('✅ All required modules imported successfully.')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Go to PC_host directory: cd PC_host"
echo "3. Start the application: python quick_start.py"
echo "4. Open browser: http://localhost:5000"
echo ""
echo "📚 For more details, see: INSTALLATION_GUIDE.md"
echo ""
echo "🔧 To customize settings, edit: PC_host/.env"
