# ESP32 Remote Control với Màn hình ST7789P3 3.2"

## Mô tả
ESP32_host là một remote control phần cứng để điều khiển hệ thống WC từ xa. Thiết bị sử dụng:
- **ESP32** làm vi điều khiển chính
- **Màn hình TFT 3.2" ST7789P3** với độ phân giải 240x320
- **5 nút bấm** để điều hướng (UP, DOWN, LEFT, RIGHT, SELECT)
- **LED trạng thái** để hiển thị hoạt động
- **Kết nối WiFi và MQTT** để giao tiếp với hệ thống

## Kết nối phần cứng

### Màn hình ST7789P3
```
ESP32     →  ST7789P3
GPIO18    →  SCLK (Serial Clock)
GPIO23    →  MOSI (Data)
GPIO5     →  CS (Chip Select)
GPIO2     →  DC (Data/Command)
GPIO4     →  RST (Reset)
GPIO15    →  BL (Backlight)
3.3V      →  VCC
GND       →  GND
```

### Nút bấm (Pull-up internal)
```
ESP32     →  Chức năng
GPIO32    →  UP
GPIO33    →  DOWN
GPIO25    →  LEFT
GPIO26    →  RIGHT
GPIO27    →  SELECT
```

### LED trạng thái
```
ESP32     →  LED
GPIO22    →  Status LED (+ Resistor 220Ω)
```

## Tính năng

### Giao diện người dùng
- **Header**: Hiển thị tên thiết bị
- **Danh sách WC nodes**: Hiển thị các toilet có thể điều khiển
- **Trạng thái realtime**: Online/Offline cho từng node
- **Biểu tượng phân loại**: M (Nam), F (Nữ)
- **Footer**: Trạng thái kết nối WiFi và MQTT

### Điều khiển
- **UP/DOWN**: Chọn WC node
- **SELECT**: Gửi lệnh flush
- **LED**: Nhấp nháy khi có hoạt động

### Kết nối mạng
- **WiFi**: Tự động kết nối các mạng đã cấu hình
- **MQTT**: Publish/Subscribe để giao tiếp với PC host
- **Heartbeat**: Gửi tín hiệu sống mỗi 30 giây

## Cấu hình

### WiFi Networks
Chỉnh sửa trong `main.py`:
```python
WIFI_NETWORKS = [
    ("TenWiFi1", "MatKhau1"),
    ("TenWiFi2", "MatKhau2")
]
```

### MQTT Broker
```python
MQTT_BROKER = "192.168.1.181"  # IP của PC host
MQTT_PORT = 1883
```

### WC Nodes
```python
WC_NODES = [
    {"id": "room1_male", "name": "Room1 Male", "topic": "wc/room1_male/command"},
    {"id": "room1_female", "name": "Room1 Female", "topic": "wc/room1_female/command"},
    {"id": "room2_male", "name": "Room2 Male", "topic": "wc/room2_male/command"}
]
```

## Cài đặt

### 1. Cài đặt MicroPython
Nạp firmware MicroPython lên ESP32

### 2. Upload files
Copy các file sau lên ESP32:
```
main.py              # Code chính
lib/st7789p3.py      # Driver màn hình
lib/simple_ui.py     # Thư viện UI
lib/umqtt/simple.py  # MQTT client
```

### 3. Cấu hình mạng
Chỉnh sửa `WIFI_NETWORKS` và `MQTT_BROKER` trong `main.py`

### 4. Khởi động
Reset ESP32, thiết bị sẽ:
1. Hiển thị splash screen
2. Kết nối WiFi
3. Kết nối MQTT
4. Hiển thị giao diện chính

## MQTT Protocol

### Topics Subscribe
- `wc/[node_id]/status` - Nhận trạng thái từ WC nodes

### Topics Publish
- `wc/[node_id]/command` - Gửi lệnh flush
- `wc/remote/status` - Trạng thái remote control
- `wc/remote/heartbeat` - Tín hiệu sống

### Message Format
```json
{
    "action": "flush",
    "timestamp": 1641234567,
    "source": "remote_control"
}
```

## Troubleshooting

### Màn hình không hiển thị
1. Kiểm tra kết nối SPI
2. Kiểm tra nguồn 3.3V
3. Kiểm tra reset và backlight

### Không kết nối WiFi
1. Kiểm tra tên mạng và mật khẩu
2. Kiểm tra tín hiệu WiFi
3. Reset ESP32 và thử lại

### Không kết nối MQTT
1. Kiểm tra IP broker
2. Kiểm tra firewall PC host
3. Kiểm tra service mosquitto trên PC

### Nút bấm không hoạt động
1. Kiểm tra kết nối GPIO
2. Kiểm tra pull-up resistor
3. Kiểm tra debouncing trong code

## Development

### Thêm WC node mới
1. Thêm vào `WC_NODES` array
2. Cập nhật UI layout nếu cần
3. Test kết nối MQTT

### Thay đổi giao diện
Chỉnh sửa `lib/simple_ui.py`:
- Colors: `ST7789P3.COLOR_NAME`
- Layout: `header_height`, `footer_height`, `node_height`
- Font: Bitmap trong `FONT_8X8`

### Debug
Enable serial output để xem log:
```python
print(f"🔍 Debug info: {variable}")
```

## Tích hợp với hệ thống

Remote control này tích hợp với:
- **PC_host**: Flask web server và MQTT broker
- **ESP32_nodes**: WC control nodes
- **Database**: SQLite để log events

Xem README chính của project để biết thêm chi tiết về toàn bộ hệ thống.
