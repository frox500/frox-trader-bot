from flask import Flask, request
import requests
import os
import threading
import time

app = Flask(__name__)

TELEGRAM_TOKEN    = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID  = os.environ["TELEGRAM_CHAT_ID"]
RENDER_URL        = os.environ["RENDER_URL"]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id":    TELEGRAM_CHAT_ID,
            "text":       message,
            "parse_mode": "HTML"
        }, timeout=10)
    except Exception as e:
        print(f"[Telegram error] {e}")

def keep_alive():
    while True:
        try:
            requests.get(RENDER_URL + "/ping", timeout=10)
            print("[keep_alive] ping OK")
        except Exception as e:
            print(f"[keep_alive] error: {e}")
        time.sleep(600)

@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    # Intentar JSON primero
    data = request.get_json(silent=True)
    if data:
        message = data.get("value") or data.get("message") or str(data)
    else:
        # TradingView envía texto plano
        message = request.data.decode("utf-8").strip()

    if message:
        send_telegram(message)
        print(f"[webhook] enviado: {message[:80]}")
        return "OK", 200
    return "Empty payload", 400

@app.route("/", methods=["GET"])
def home():
    return "Frox Trader Bot - Online ✅", 200

if __name__ == "__main__":
    t = threading.Thread(target=keep_alive, daemon=True)
    t.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
