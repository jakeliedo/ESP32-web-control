# HƯỚNG DẪN CÀI ĐẶT VÀ KHỞI ĐỘNG PC HOST (WINDOWS)

## 1. Yêu cầu hệ thống
- Windows 10/11
- Python 3.10 trở lên (https://www.python.org/downloads/)
- Kết nối Internet để tải package và Mosquitto

## 2. Các bước cài đặt nhanh

### a. Giải nén/copy thư mục `PC_host` vào máy tính đích

### b. Mở PowerShell với quyền Administrator (Run as Administrator)

### c. Chạy script cài đặt tự động:
```powershell
cd đường/dẫn/đến/PC_host
./install_pc_host.ps1
```

Script sẽ tự động:
- Kiểm tra/cài đặt Python virtual environment
- Cài các package Python cần thiết
- Tải và cài Mosquitto MQTT broker (nếu chưa có)
- Thiết lập Mosquitto chạy nền (service)
- Mở firewall cho port 1883

## 3. Khởi động server
Sau khi cài đặt xong, chạy các lệnh sau trong PowerShell:
```powershell
cd PC_host
./venv/Scripts/Activate.ps1
python app.py
```

- Truy cập dashboard tại: http://localhost:5000
- Giao diện đơn giản: http://localhost:5000/simple

## 4. Ghi chú cấu hình
- File cấu hình Mosquitto: `mosquitto_esp32.conf`
- Các script fix lỗi Mosquitto: `fix_mosquitto.ps1`, `fix_mosquitto.bat`
- Nếu cần reset database: xóa file `wc_system.db` (sẽ tự tạo lại)

## 5. Troubleshooting
- Nếu Mosquitto không chạy, kiểm tra service trong Windows Services (`services.msc`)
- Nếu port 1883 bị chặn, kiểm tra firewall rule
- Nếu thiếu package Python, chạy lại: `pip install -r requirements.txt`

## 6. Thông tin thêm
- Để cài đặt lại Mosquitto hoặc sửa lỗi, xem các script và tài liệu kèm theo trong thư mục `PC_host`
- Nếu cần hỗ trợ, liên hệ người phát triển hệ thống.

---
**Chúc bạn cài đặt thành công!**
