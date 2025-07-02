# app.py
from flask import Flask, render_template_string, request, redirect
import requests

# Địa chỉ IP của ESP32 (thay bằng IP thực tế của bạn)
ESP32_IP = "http://192.168.1.42"

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
            max-width: 600px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 24px;
            padding: 16px;
            box-sizing: border-box;
        }
        .card {
            background: #222;
            border-radius: 24px;
            padding: 24px 8px 16px 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            box-shadow: 0 4px 24px #0008;
            min-width: 0;
            min-height: 200px;
            width: 100%;
        }
        .icon img {
            width: 64px;
            height: 64px;
            margin-bottom: 12px;
        }
        .room {
            font-size: 1.5rem;
            margin-bottom: 24px;
            font-weight: bold;
        }
        .flush-btn {
            background: none;
            border: none;
            padding: 0;
            cursor: pointer;
            outline: none;
        }
        .flush-btn img {
            width: 90px;
            height: 90px;
            display: block;
        }
        .flush-btn:active img {
            filter: brightness(0.8);
        }
        .logo {
            position: fixed;
            left: 24px;
            bottom: 24px;
            width: 60px;
            opacity: 0.85;
        }
        @media (max-width: 600px) {
            .container {
                grid-template-columns: 1fr 1fr;
                gap: 12px;
                max-width: 100vw;
                padding: 4px;
            }
            .card {
                padding: 12px 4px 8px 4px;
            }
            .icon img {
                width: 48px;
                height: 48px;
            }
            .flush-btn img {
                width: 60px;
                height: 60px;
            }
            .logo {
                width: 40px;
                left: 8px;
                bottom: 8px;
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
    app.run(debug=True, host='0.0.0.0')