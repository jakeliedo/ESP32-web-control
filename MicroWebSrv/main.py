import network
import machine
import time
from microWebSrv import MicroWebSrv
print("ESP32 starting...")

# Kết nối WiFi (thay đổi SSID và PASSWORD)
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Michelle', '0908800130')
while not sta_if.isconnected():
    time.sleep(1)
print('WiFi connected:', sta_if.ifconfig())

# Khai báo các kênh GPIO
channels = {
    1: machine.Pin(12, machine.Pin.OUT),
    2: machine.Pin(13, machine.Pin.OUT),
    3: machine.Pin(14, machine.Pin.OUT),
    4: machine.Pin(15, machine.Pin.OUT)
}

# Hàm điều khiển GPIO
def set_channel(ch, state):
    if ch in channels:
        channels[ch].value(state)

# Xử lý trang chính
def handlerIndex(httpClient, httpResponse):
    html = """<!DOCTYPE html>
<html>
<head><title>ESP32 Control</title></head>
<body>
<h2>Điều khiển thiết bị</h2>
<form method="POST" action="/control">
"""
    for ch in channels:
        html += f'Kênh {ch}: <button name="ch" value="{ch}_on">Bật</button> <button name="ch" value="{ch}_off">Tắt</button><br>'
    html += """
</form>
</body>
</html>
"""
    httpResponse.WriteResponseOk(contentType="text/html", contentCharset="UTF-8", content=html)

# Xử lý điều khiển
def handlerControl(httpClient, httpResponse):
    form = httpClient.ReadRequestPostedFormData()
    if "ch" in form:
        val = form["ch"]
        ch, action = val.split("_")
        ch = int(ch)
        if action == "on":
            set_channel(ch, 1)
        else:
            set_channel(ch, 0)
    httpResponse.WriteResponseRedirect("/")

routeHandlers = [
    ("/", "GET", handlerIndex),
    ("/control", "POST", handlerControl)
]

mws = MicroWebSrv(routeHandlers=routeHandlers)
mws.Start(threaded=True)