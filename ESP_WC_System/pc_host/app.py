# app.py
from flask import Flask, render_template_string, request, redirect
import requests

# Địa chỉ IP của ESP32 (thay bằng IP thực tế của bạn)
ESP32_IP = "http://192.168.100.72"

app = Flask(__name__)

# ...existing code...
HTML = """
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
    <form method="post" style="width:100%;">
        <div class="container">
            <div class="card">
                <div class="icon"><img src="/static/male.png" alt="Male"></div>
                <div class="room">Room 1</div>
                <button class="flush-btn" name="action" value="1_on">
                    <img src="/static/button.png" alt="FLUSH">
                </button>
            </div>
            <div class="card">
                <div class="icon"><img src="/static/male.png" alt="Male"></div>
                <div class="room">Room 2</div>
                <button class="flush-btn" name="action" value="2_on">
                    <img src="/static/button.png" alt="FLUSH">
                </button>
            </div>
            <div class="card">
                <div class="icon"><img src="/static/female.png" alt="Female"></div>
                <div class="room">Room 1</div>
                <button class="flush-btn" name="action" value="3_on">
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
# ...existing code...

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action")
        # Gửi lệnh tới ESP32
        try:
            resp = requests.post(f"{ESP32_IP}/control", data={"ch": action}, timeout=2)
        except Exception as e:
            print("Lỗi gửi lệnh tới ESP32:", e)
        return redirect("/")
    return render_template_string(HTML)

if __name__ == "__main__":
    try:
        print(f"🚀 PC Host running at http://{HOST}:{PORT}")
        print(f"Simple UI available at http://{HOST}:{PORT}/simple")
        socketio.run(app, host=HOST, port=PORT, debug=DEBUG)
    except KeyboardInterrupt:
        print("Shutting down by keyboard interrupt...")
        shutdown_handler()
    except Exception as e:
        print(f"Error starting server: {e}")