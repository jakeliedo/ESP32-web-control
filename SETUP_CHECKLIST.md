# ✅ WC Control System - Setup Checklist

Checklist đầy đủ để clone và chạy project trên máy tính mới.

## 📋 Pre-requirements Checklist

### ✅ Bắt buộc có sẵn:
- [ ] **Python 3.8+** đã cài đặt
  ```bash
  python --version  # Should show 3.8 or higher
  ```
- [ ] **Git** đã cài đặt để clone repository
- [ ] **Internet connection** để download dependencies

### ✅ Tùy chọn (để phát triển ESP32):
- [ ] **Visual Studio Code** với extension Pymakr
- [ ] **ESP32 Development Board** 
- [ ] **USB Cable** để kết nối ESP32

## 🛠️ Installation Checklist

### ✅ Bước 1: Clone Project
- [ ] Clone repository về máy local
- [ ] Navigate vào thư mục project

### ✅ Bước 2: Python Environment
- [ ] Tạo virtual environment
- [ ] Activate virtual environment  
- [ ] Install dependencies từ requirements.txt

### ✅ Bước 3: Configuration
- [ ] Tạo file `.env` trong thư mục `PC_host/`
- [ ] Cấu hình MQTT broker settings
- [ ] Cấu hình Flask settings

### ✅ Bước 4: Dependencies
- [ ] MQTT Broker đã cài đặt (mosquitto hoặc built-in)
- [ ] Database directory đã tạo
- [ ] Static files accessible

## 🚀 Running Checklist

### ✅ Start Application:
- [ ] Activate virtual environment
- [ ] Navigate to PC_host directory
- [ ] Run quick_start.py hoặc app.py
- [ ] Web server starts without errors

### ✅ Test Basic Functions:
- [ ] Dashboard loads tại http://localhost:5000
- [ ] Mobile UI loads tại http://localhost:5000/simple
- [ ] No console errors in browser
- [ ] MQTT broker connection successful

### ✅ Test Advanced Features:
- [ ] Node control buttons work (show notifications)
- [ ] Events page shows data
- [ ] Theme toggle works (dark/light)
- [ ] Auto-refresh functions properly

## 🔧 ESP32 Setup Checklist (Optional)

### ✅ ESP32 Development:
- [ ] ESP32 development tools installed
- [ ] ESP32 board connected via USB
- [ ] WiFi credentials configured in code
- [ ] MicroPython firmware uploaded
- [ ] Node code uploaded successfully

### ✅ ESP32 Testing:
- [ ] ESP32 connects to WiFi
- [ ] ESP32 connects to MQTT broker
- [ ] Commands from web interface reach ESP32
- [ ] ESP32 responses appear in web interface

## ⚡ Quick Commands Reference

### Clone and Setup:
```bash
# Clone
git clone <repository-url>
cd ESP_WC_System

# Auto setup
setup.bat          # Windows
./setup.sh         # Linux/Mac
```

### Manual Setup:
```bash
# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install deps
pip install -r requirements.txt

# Run app
cd PC_host
python quick_start.py
```

### Test Commands:
```bash
cd PC_host

# Test system
python test_system_full.py

# Test MQTT
python debug_mqtt_monitor.py

# Test database
python -c "from database import get_all_nodes; print(get_all_nodes())"
```

## 🎯 Success Indicators

### ✅ Everything Working:
- [ ] ✅ Web interface loads without errors
- [ ] ✅ Dashboard shows node controls
- [ ] ✅ Button clicks show success notifications
- [ ] ✅ Events page shows logs
- [ ] ✅ Console shows MQTT messages
- [ ] ✅ No error messages in terminal

### ✅ ESP32 Working (if used):
- [ ] ✅ ESP32 serial monitor shows WiFi connection
- [ ] ✅ ESP32 shows MQTT connection success
- [ ] ✅ Commands from web reach ESP32
- [ ] ✅ ESP32 LED blinks when commanded
- [ ] ✅ Status updates appear in web interface

## 🚨 Common Issues & Solutions

### ❌ Python Import Errors:
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### ❌ MQTT Connection Failed:
```bash
# Solution: Start MQTT broker
cd PC_host
python start_mqtt_broker.py
```

### ❌ Port 5000 Already in Use:
```bash
# Windows: Kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac: Kill process  
lsof -ti:5000 | xargs kill -9
```

### ❌ Database Errors:
```bash
# Solution: Reset database
cd PC_host
python reset_nodes.py
```

### ❌ ESP32 Not Connecting:
1. Check WiFi credentials in code
2. Check MQTT broker IP address
3. Check ESP32 power and USB connection
4. Check MicroPython firmware

## 📞 Getting Help

### 🔍 Debug Information:
- Check console output for error messages
- Test each component individually
- Verify network connectivity
- Check file permissions

### 📚 Documentation:
- Read `INSTALLATION_GUIDE.md` for detailed setup
- Check `PC_host/README.md` for web app details
- Review `ESP32_host/README.md` for ESP32 setup

### 🧪 Testing:
```bash
# Quick system test
cd PC_host
python test_ui.py

# Full system test
python test_system_full.py
```

---

## ✅ Final Verification

**Your setup is complete when:**
1. ✅ Web dashboard loads and looks good
2. ✅ Buttons work and show notifications  
3. ✅ No errors in browser console
4. ✅ MQTT shows connection success
5. ✅ Events page shows activities
6. ✅ Mobile UI works on phone
7. ✅ Theme toggle functions
8. ✅ Auto-refresh works

**🎉 Congratulations! Your WC Control System is ready to use!**

---
*WC Control System v2.0 - Setup Checklist*
