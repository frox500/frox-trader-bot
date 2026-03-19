from flask import Flask, request
import requests
import os
import threading
import time

app = Flask(__name__)

TELEGRAM_TOKEN   = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
RENDER_URL       = os.environ["RENDER_URL"]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id"    : TELEGRAM_CHAT_ID,
            "text"       : message,
            "parse_mode" : "HTML"
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
    data = request.get_json(silent=True)

    if data and "side" in data:
        # ✅ JSON estructurado de Frox Trader
        side   = data.get("side", "")
        signal = data.get("signal", "")
        conf   = data.get("conf", "")
        tf     = data.get("tf", "")
        par    = data.get("par", "BTCUSDT")
        entry  = data.get("entry", "")
        sl     = data.get("sl", "")
        tp1    = data.get("tp1", "")
        tp2    = data.get("tp2", "")
        mac    = data.get("mac", "")

        emoji  = "🟢" if side == "LONG" else "🔴"

        message = (
            f"{emoji} <b>{side} — Frox Trader</b>\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"📌 Señal: {signal} | Conf: {conf}/5\n"
            f"💹 Par: {par} | TF: {tf}\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"🎯 Entry: <code>{entry}</code>\n"
            f"🛑 SL:    <code>{sl}</code>\n"
            f"✅ TP1:   <code>{tp1}</code>\n"
            f"🚀 TP2:   <code>{tp2}</code>\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"📊 MAC: {mac}"
        )

    elif data:
        # JSON genérico
        message = data.get("value") or data.get("message") or str(data)
    else:
        # Texto plano
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
