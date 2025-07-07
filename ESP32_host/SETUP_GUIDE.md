# ESP32 Remote Control - Hướng dẫn Setup nhanh

## Bước 1: Chuẩn bị phần cứng

### Linh kiện cần thiết:
- ESP32 DevKit v1 (30 pins)
- Màn hình TFT 3.2" ST7789P3 (240x320)
- 5 nút bấm tactile
- 1 LED + điện trở 220Ω
- Breadboard và dây jumper
- Nguồn 5V (USB hoặc adapter)

### Kết nối phần cứng:

```
ESP32 GPIO  →  Component
-------------------------------
GPIO18      →  Display SCLK
GPIO23      →  Display MOSI
GPIO5       →  Display CS
GPIO2       →  Display DC
GPIO4       →  Display RST
GPIO15      →  Display BL
3.3V        →  Display VCC
GND         →  Display GND

GPIO32      →  Button UP
GPIO33      →  Button DOWN
GPIO25      →  Button LEFT
GPIO26      →  Button RIGHT
GPIO27      →  Button SELECT
GND         →  Buttons (other side)

GPIO22      →  LED + (through 220Ω resistor)
GND         →  LED -
```

## Bước 2: Cài đặt MicroPython

1. **Download MicroPython firmware:**
   - Vào https://micropython.org/download/esp32/
   - Tải bản mới nhất (ví dụ: esp32-20210902-v1.17.bin)

2. **Flash firmware:**
   ```bash
   esptool.py --chip esp32 --port COM3 erase_flash
   esptool.py --chip esp32 --port COM3 --baud 460800 write_flash -z 0x1000 esp32-20210902-v1.17.bin
   ```

3. **Kiểm tra kết nối:**
   - Mở terminal serial (115200 baud)
   - Reset ESP32, thấy prompt `>>>`

## Bước 3: Upload code

### Cách 1: Sử dụng Thonny IDE
1. Cài đặt Thonny: https://thonny.org/
2. Cấu hình: Tools → Options → Interpreter → MicroPython (ESP32)
3. Upload các file theo thứ tự:
   ```
   lib/umqtt/simple.py
   lib/st7789p3.py
   lib/simple_ui.py
   lib/remote_control.py
   config.py
   boot.py
   main.py
   ```

### Cách 2: Sử dụng ampy
```bash
pip install adafruit-ampy
ampy --port COM3 put lib/
ampy --port COM3 put config.py
ampy --port COM3 put boot.py  
ampy --port COM3 put main.py
```

### Cách 3: Sử dụng VS Code + Pymakr
1. Cài extension Pymakr
2. Tạo pymakr.conf
3. Sync project

## Bước 4: Cấu hình

### Chỉnh sửa config.py:

```python
# WiFi networks
WIFI_NETWORKS = [
    ("TenWiFiCuaBan", "MatKhauWiFi"),
    ("WiFi2", "MatKhau2"),
]

# MQTT broker (IP của PC host)
MQTT_BROKER = "192.168.1.181"

# WC nodes
WC_NODES = [
    {"id": "room1_male", "name": "Phòng 1 Nam", "topic": "wc/room1_male/command"},
    {"id": "room1_female", "name": "Phòng 1 Nữ", "topic": "wc/room1_female/command"},
]
```

## Bước 5: Test hệ thống

1. **Test từng component:**
   ```python
   import test_system
   test_system.run_all_tests()
   ```

2. **Chạy chương trình chính:**
   ```python
   import main
   # hoặc chỉ reset ESP32
   ```

## Bước 6: Troubleshooting

### Màn hình không hiển thị:
- Kiểm tra kết nối SPI (SCLK, MOSI, CS, DC, RST)
- Kiểm tra nguồn 3.3V
- Thử thay đổi CS pin trong config.py

### Không kết nối WiFi:
- Kiểm tra tên mạng và mật khẩu
- Thử đưa ESP32 gần router
- Kiểm tra băng tần 2.4GHz

### Không kết nối MQTT:
- Kiểm tra IP broker trong config.py
- Kiểm tra firewall trên PC
- Kiểm tra service mosquitto đang chạy

### Nút bấm không hoạt động:
- Kiểm tra kết nối GPIO
- Kiểm tra pull-up trong code
- Thử đổi pin khác

## Bước 7: Sử dụng

### Giao diện:
- **UP/DOWN**: Chọn WC node
- **SELECT**: Gửi lệnh flush
- **LED**: Nhấp nháy khi có hoạt động
- **Màn hình**: Hiển thị trạng thái real-time

### MQTT Topics:
- Subscribe: `wc/[node_id]/status`
- Publish: `wc/[node_id]/command`
- Status: `wc/remote/status`
- Heartbeat: `wc/remote/heartbeat`

## Support

Nếu gặp vấn đề, kiểm tra:
1. Kết nối phần cứng
2. Log serial output
3. Cấu hình network
4. PC host đang chạy

**Happy Coding! 🚀**
