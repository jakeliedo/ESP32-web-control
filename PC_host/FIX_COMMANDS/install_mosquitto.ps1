# PowerShell script to install and configure Mosquitto for ESP32
Write-Host "🚀 Installing Mosquitto MQTT Broker for ESP32..." -ForegroundColor Green

# Function to check if a command exists
function Test-CommandExists {
    param($command)
    try {
        if (Get-Command $command -ErrorAction Stop) { return $true }
    }
    catch { return $false }
}

# Try to install via Chocolatey
if (Test-CommandExists "choco") {
    Write-Host "📦 Installing via Chocolatey..." -ForegroundColor Yellow
    choco install mosquitto -y
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Mosquitto installed via Chocolatey" -ForegroundColor Green
    }
} elseif (Test-CommandExists "winget") {
    Write-Host "📦 Installing via winget..." -ForegroundColor Yellow
    winget install Eclipse.Mosquitto --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Mosquitto installed via winget" -ForegroundColor Green
    }
} else {
    Write-Host "❌ No package manager found" -ForegroundColor Red
    Write-Host "📋 Please install manually from: https://mosquitto.org/download/" -ForegroundColor Yellow
    exit 1
}

# Wait for installation to complete
Start-Sleep -Seconds 3

# Create ESP32-compatible configuration
$configContent = @"
# ESP32 WC System - Mosquitto Configuration
# Allow connections from ESP32 devices

# Listen on all interfaces (0.0.0.0) on port 1883
listener 1883 0.0.0.0

# Allow anonymous connections (no authentication required)
allow_anonymous true

# Log settings
log_dest file C:\Program Files\mosquitto\mosquitto.log
log_type error
log_type warning
log_type notice
log_type information

# Set maximum message size (for ESP32 compatibility)
message_size_limit 8192

# Allow retained messages
retain_available true
"@

# Try to create config file
$configPath = "C:\Program Files\mosquitto\mosquitto_esp32.conf"
try {
    $configContent | Out-File -FilePath $configPath -Encoding UTF8
    Write-Host "✅ Created ESP32 config: $configPath" -ForegroundColor Green
} catch {
    $configPath = "mosquitto_esp32.conf"
    $configContent | Out-File -FilePath $configPath -Encoding UTF8
    Write-Host "✅ Created ESP32 config: $(Resolve-Path $configPath)" -ForegroundColor Green
}

# Stop any existing mosquitto service
Write-Host "🛑 Stopping existing Mosquitto service..." -ForegroundColor Yellow
Stop-Service mosquitto -ErrorAction SilentlyContinue

# Start Mosquitto with ESP32 configuration
Write-Host "🚀 Starting Mosquitto with ESP32 configuration..." -ForegroundColor Green
Write-Host "📡 MQTT broker will listen on 0.0.0.0:1883 (all interfaces)" -ForegroundColor Cyan

try {
    # Try to start as service first
    if (Test-Path "C:\Program Files\mosquitto\mosquitto.exe") {
        $mosquittoPath = "C:\Program Files\mosquitto\mosquitto.exe"
    } else {
        $mosquittoPath = "mosquitto"
    }
    
    Write-Host "🔧 Starting Mosquitto manually..." -ForegroundColor Yellow
    Start-Process -FilePath $mosquittoPath -ArgumentList "-c", $configPath, "-v" -NoNewWindow -PassThru
    
    Start-Sleep -Seconds 3
    
    # Test connectivity
    Write-Host "🧪 Testing MQTT connectivity..." -ForegroundColor Yellow
    
    # Test if port 1883 is listening
    $connection = Test-NetConnection -ComputerName "192.168.100.121" -Port 1883 -ErrorAction SilentlyContinue
    if ($connection.TcpTestSucceeded) {
        Write-Host "✅ MQTT broker is accessible on 192.168.100.121:1883" -ForegroundColor Green
        Write-Host "🎉 ESP32 should now be able to connect!" -ForegroundColor Green
    } else {
        Write-Host "❌ MQTT broker is not accessible on external IP" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Error starting Mosquitto: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n📋 Setup completed!" -ForegroundColor Green
Write-Host "🔍 Check if ESP32 can now connect to MQTT broker at 192.168.100.121:1883" -ForegroundColor Cyan
