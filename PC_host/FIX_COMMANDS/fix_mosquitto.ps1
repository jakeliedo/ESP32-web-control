# Fix Mosquitto cho ESP32
Write-Host "🔧 Cấu hình Mosquitto cho ESP32..." -ForegroundColor Green

# Kiểm tra Mosquitto có chạy không
Write-Host "🔍 Kiểm tra Mosquitto service..." -ForegroundColor Yellow
$service = Get-Service -Name "mosquitto" -ErrorAction SilentlyContinue

if ($service) {
    Write-Host "✅ Tìm thấy Mosquitto service" -ForegroundColor Green
    
    # Stop service
    Write-Host "🛑 Dừng Mosquitto service..." -ForegroundColor Yellow
    Stop-Service mosquitto -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "⚠️ Không tìm thấy Mosquitto service" -ForegroundColor Red
}

# Tạo cấu hình ESP32
$configPath = "C:\Program Files\mosquitto\mosquitto.conf"
$backupPath = "C:\Program Files\mosquitto\mosquitto.conf.backup"

Write-Host "📝 Tạo cấu hình ESP32..." -ForegroundColor Yellow

# Backup cấu hình cũ nếu tồn tại
if (Test-Path $configPath) {
    Copy-Item $configPath $backupPath -Force
    Write-Host "💾 Đã backup cấu hình cũ" -ForegroundColor Green
}

# Tạo cấu hình mới
$esp32Config = @"
# ESP32 WC System - Mosquitto Configuration
# Cấu hình cho phép ESP32 kết nối

# Lắng nghe trên tất cả interfaces, port 1883
listener 1883 0.0.0.0

# Cho phép kết nối ẩn danh (không cần xác thực)
allow_anonymous true

# Log chi tiết để debug
log_dest stdout
log_type all

# Không lưu persistence để đơn giản
persistence false

# Cho phép retained messages
retain_available true

# Giới hạn kích thước message (tương thích ESP32)
message_size_limit 8192

# Timeout settings cho ESP32
keepalive_interval 60
retry_interval 20

# End of ESP32 configuration
"@

try {
    Set-Content -Path $configPath -Value $esp32Config -Force
    Write-Host "✅ Đã tạo cấu hình ESP32: $configPath" -ForegroundColor Green
} catch {
    # Nếu không có quyền ghi vào Program Files, tạo ở thư mục hiện tại
    $localConfigPath = ".\mosquitto_esp32.conf"
    Set-Content -Path $localConfigPath -Value $esp32Config -Force
    Write-Host "✅ Đã tạo cấu hình ESP32: $localConfigPath" -ForegroundColor Green
    $configPath = $localConfigPath
}

# Khởi động lại service hoặc chạy thủ công
Write-Host "🚀 Khởi động Mosquitto..." -ForegroundColor Yellow

if ($service) {
    try {
        Start-Service mosquitto
        Write-Host "✅ Đã khởi động Mosquitto service" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Không thể khởi động service, thử chạy thủ công..." -ForegroundColor Yellow
    }
} else {
    Write-Host "🔄 Chạy Mosquitto thủ công..." -ForegroundColor Yellow
    Write-Host "📋 Sử dụng lệnh: mosquitto -c $configPath -v" -ForegroundColor Cyan
}

# Kiểm tra kết nối
Write-Host "🧪 Kiểm tra kết nối..." -ForegroundColor Yellow
Start-Sleep 2

# Test socket connection
try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $tcpClient.Connect("127.0.0.1", 1883)
    $tcpClient.Close()
    Write-Host "✅ MQTT broker hoạt động trên localhost:1883" -ForegroundColor Green
} catch {
    Write-Host "❌ Không thể kết nối localhost:1883" -ForegroundColor Red
}

try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $tcpClient.Connect("192.168.100.121", 1883)
    $tcpClient.Close()
    Write-Host "✅ MQTT broker hoạt động trên 192.168.100.121:1883" -ForegroundColor Green
    Write-Host "🎉 ESP32 có thể kết nối được!" -ForegroundColor Green
} catch {
    Write-Host "❌ Không thể kết nối 192.168.100.121:1883" -ForegroundColor Red
    Write-Host "💡 Kiểm tra Windows Firewall hoặc chạy thủ công: mosquitto -c $configPath -v" -ForegroundColor Cyan
}

# Hiển thị thông tin port
Write-Host "`n📊 Kiểm tra port 1883:" -ForegroundColor Yellow
netstat -an | findstr 1883

Write-Host "`n✅ Hoàn thành cấu hình Mosquitto cho ESP32!" -ForegroundColor Green
Write-Host "📡 ESP32 có thể kết nối tới: 192.168.100.121:1883" -ForegroundColor Cyan
