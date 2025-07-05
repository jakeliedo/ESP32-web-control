import network
import machine
import time
from machine import Timer
from microWebSrv import MicroWebSrv

print("ESP32 starting...")

# Quét các mạng WiFi xung quanh
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
print("Scanning WiFi...")
nets = sta_if.scan()
ssid_list = [net[0].decode() for net in nets]
print("Found SSIDs:", ssid_list)

# Ưu tiên kết nối theo thứ tự
if "Michelle" in ssid_list:
    print("Connecting to Michelle...")
    sta_if.ifconfig(('192.168.1.43', '255.255.255.0', '192.168.1.1', '8.8.8.8'))
    sta_if.connect('Michelle', '0908800130')
elif "Vinternal" in ssid_list:
    print("Connecting to Vinternal...")
    sta_if.ifconfig(('192.168.100.72','255.255.255.0','192.168.100.1', '8.8.8.8'))
    sta_if.connect('Vinternal', 'Veg@s123')
elif "Floor 9" in ssid_list:
    print("Connecting to Floor 9...")
    sta_if.ifconfig(('192.168.100.72', '255.255.255.0', '192.168.100.1', '8.8.8.8'))
    sta_if.connect('Floor 9', 'Veg@s123')
else:
    print("No known SSID found! Please check WiFi.")
    while True:
        time.sleep(5)

# Đợi kết nối thành công
while not sta_if.isconnected():
    print("Waiting for WiFi connection...")
    time.sleep(1)
print('WiFi connected:', sta_if.ifconfig())

# Khai báo các kênh GPIO
channels = {
    1: machine.Pin(12, machine.Pin.OUT),
    2: machine.Pin(13, machine.Pin.OUT),
    3: machine.Pin(14, machine.Pin.OUT),
    4: machine.Pin(15, machine.Pin.OUT)
}

# LED mặc định trên ESP32 (thường là GPIO2, kiểm tra lại nếu không sáng)
LED_PIN = 2
led = machine.Pin(LED_PIN, machine.Pin.OUT)

timers = {}  # Quản lý timer cho từng channel

def blink_led(times=3, duration=100):
    for _ in range(times):
        led.value(1)
        time.sleep_ms(duration)
        led.value(0)
        time.sleep_ms(duration)

def set_channel(ch, state):
    if ch in channels:
        channels[ch].value(state)
        print(f"[set_channel] Channel {ch} set to {'ON' if state else 'OFF'}")
    else:
        print(f"[set_channel] Invalid channel: {ch}")
        
def auto_off_factory(ch):
    def auto_off(timer):
        set_channel(ch, 0)
        print(f"[auto_off] Channel {ch} auto turned OFF")
        timers.pop(ch, None)
    return auto_off

def handlerIndex(httpClient, httpResponse):
    print("[handlerIndex] Browser accessed main page")
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Web Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    html, body {
        height: 100%;
        margin: 0;
        padding: 0;
    }
    body {
        background: #111;
        color: #fff;
        font-family: Arial, sans-serif;
        min-height: 100vh;
        min-width: 100vw;
        box-sizing: border-box;
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
    }
    .container {
        width: 100vw;
        max-width: 500px;
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: 1fr 1fr;
        gap: 18px;
        padding: 12px 0 32px 0;
        box-sizing: border-box;
    }
    .card {
    background: transparent;
    border: 2.5px solid #444;
    border-radius: 22px;
    padding: 18px 8px 18px 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    box-shadow: 0 2px 16px #000a;
    min-width: 0;
    min-height: 280px;
    width: 95%;
    justify-content: space-between;
    }
    .icon img {
        width: 72px;
        height: 108px;
        margin-bottom: 8px;
        margin-top: 12px;
    }
    .room {
        font-size: 1.4rem;
        margin-bottom: 18px;
        font-weight: bold;
    }
    .flush-btn {
        background: none;
        border: none;
        padding: 0;
        cursor: pointer;
        outline: none;
        margin-top: 8px;
        margin-bottom: 12px;
    }
    .flush-btn img {
        width: 72px;
        height: 72px;
        display: block;
    }
    .flush-btn:active img {
        filter: brightness(0.8);
    }
    .logo {
        position: fixed;
        right: 16px;
        bottom: 16px;
        width: 48px;
        opacity: 0.85;
        z-index: 10;
    }
    @media (max-width: 600px) {
        .container {
            max-width: 98vw;
            gap: 10px;
            padding: 4px 0 24px 0;
        }
        .card {
            padding: 10px 2px 10px 2px;
            min-height: 240px;
        }
        .icon img {
            width: 48px;
            height: 72px;
            margin-bottom: 8px;
        }
        .flush-btn img {
            width: 60px;
            height: 60px;
        }
        .logo {
            width: 32px;
            right: 8px;
            bottom: 8px;
        }
        .room {
            font-size: 1.1rem;
            margin-bottom: 40px;
        }
    }
    </style>
</head>
<body>
    <form method="post" action="/control" style="width:100%;">
        <div class="container">
            <div class="card">
                <div class="icon"><img src="/static/male.png" alt="Male"></div>
                <div class="room">Room 1</div>
                <button class="flush-btn" name="ch" value="1_on">
                    <img src="/static/button.png" alt="FLUSH">
                </button>
            </div>
            <div class="card">
                <div class="icon"><img src="/static/male.png" alt="Male"></div>
                <div class="room">Room 2</div>
                <button class="flush-btn" name="ch" value="2_on">
                    <img src="/static/button.png" alt="FLUSH">
                </button>
            </div>
            <div class="card">
                <div class="icon"><img src="/static/female.png" alt="Female"></div>
                <div class="room">Room 1</div>
                <button class="flush-btn" name="ch" value="3_on">
                    <img src="/static/button.png" alt="FLUSH">
                </button>
            </div>
            <div></div>
        </div>
    </form>
    <img src="/static/logo.png" class="logo" alt="Logo">
</body>
</html>
"""
    httpResponse.WriteResponseOk(contentType="text/html", contentCharset="UTF-8", content=html)

def handlerControl(httpClient, httpResponse):
    try:
        form = httpClient.ReadRequestPostedFormData()
        print("[handlerControl] Received POST data:", form)

        val = form.get("ch")
        if val:
            print("[handlerControl] Button value:", val)
            # Blink LED mỗi khi nhấn nút
            blink_led(times=3, duration=80)

            ch_str, action = val.split("_")
            ch = int(ch_str)
            state = 1 if action == "on" else 0

            set_channel(ch, state)

            # Nếu bật (on), lên kế hoạch tự động tắt sau 1.5 giây
            timer_id = ch - 1  # Channel 1 -> Timer(0), Channel 2 -> Timer(1), ...
            if state == 1:
                if ch in timers:
                    timers[ch].deinit()
                t = Timer(-1)
                t.init(mode=Timer.ONE_SHOT, period=3000, callback=auto_off_factory(ch))
                timers[ch] = t
                print("[handlerControl] Off after 3s for channel")
            else:
                # Nếu nhấn OFF, huỷ timer nếu có
                if ch in timers:
                    timers[ch].deinit()
                    timers.pop(ch, None)
        else:
            print("[handlerControl] Missing field 'ch' in form")
    except Exception as e:
        print("[handlerControl] Exception:", e)

    httpResponse.WriteResponseRedirect("/")

routeHandlers = [
    ("/", "GET", handlerIndex),
    ("/control", "POST", handlerControl)
]

mws = MicroWebSrv(routeHandlers=routeHandlers, webPath="/")
mws.Start(threaded=True)