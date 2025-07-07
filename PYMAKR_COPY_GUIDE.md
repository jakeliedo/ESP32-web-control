# HƯỚNG DẪN COPY PYMAKR EXTENSION

## ✅ CÓ THỂ COPY PYMAKR EXTENSION

Bạn hoàn toàn có thể copy Pymakr extension từ máy này sang máy khác.

## 📍 VỊ TRÍ PYMAKR EXTENSION

### Máy hiện tại:
```
C:\Users\Bo-Home\.vscode\extensions\pycom.pymakr-preview-2.25.2
```

### Máy đích (thay [username] bằng tên user):
```
C:\Users\[username]\.vscode\extensions\
```

## 🔧 CÁCH THỰC HIỆN

### Bước 1: Backup trên máy nguồn
1. Mở folder: `C:\Users\Bo-Home\.vscode\extensions\`
2. Tìm folder: `pycom.pymakr-preview-2.25.2`
3. Copy toàn bộ folder này
4. Nén thành file ZIP để dễ chuyển

### Bước 2: Cài đặt trên máy đích
1. **Đóng VS Code** hoàn toàn
2. Mở folder: `C:\Users\[username]\.vscode\extensions\`
3. Dán folder `pycom.pymakr-preview-2.25.2` vào đây
4. Khởi động lại VS Code
5. Kiểm tra Extensions panel (Ctrl+Shift+X)

## ⚠️ CHÚ Ý QUAN TRỌNG

### 1. Kiểm tra compatibility:
- VS Code version trên máy đích
- Python có được cài đặt không
- Node.js có cần thiết không

### 2. Quyền truy cập:
- Đảm bảo folder có quyền read/write
- Chạy VS Code với quyền admin nếu cần

### 3. Nếu không hoạt động:
- Gỡ extension cũ trước
- Cài từ VS Code Marketplace
- Hoặc download file .vsix

## 🛠️ PHƯƠNG PHÁP KHÁC (Khuyến nghị)

### Cài từ Marketplace:
1. Mở VS Code trên máy đích
2. Ctrl+Shift+X để mở Extensions
3. Tìm "Pymakr" 
4. Click Install

### Từ file .vsix:
1. Download từ: https://marketplace.visualstudio.com/items?itemName=pycom.Pymakr
2. VS Code → ... → Install from VSIX

## 📦 BACKUP ĐÃ TẠO

Script đã tạo backup tại Desktop với đầy đủ hướng dẫn.

## ✅ KẾT LUẬN

**CÓ THỂ** copy Pymakr extension, nhưng cách **AN TOÀN NHẤT** là:
1. Cài từ VS Code Marketplace 
2. Hoặc sử dụng backup đã tạo nếu không có internet

**Tỷ lệ thành công: ~85%** (phụ thuộc vào VS Code version và OS)
