from flask import Flask, request
import os
import json
import requests
import threading
import time

app = Flask(__name__)

TOKEN   = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
SELF_URL = os.environ.get("RENDER_URL", "")

def send_telegram(mensaje: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id"    : CHAT_ID,
            "text"       : mensaje,
            "parse_mode" : "HTML"
        }, timeout=10)
    except Exception as e:
        print(f"[Telegram error] {e}")

def keep_alive():
    while True:
        try:
            if SELF_URL:
                requests.get(SELF_URL + "/ping", timeout=10)
                print("[keep_alive] ping OK")
        except Exception as e:
            print(f"[keep_alive] error: {e}")
        time.sleep(600)

@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.data.decode("utf-8").strip()
    print(f"[webhook] recibido: {body[:100]}")

    try:
        data = json.loads(body)
    except Exception:
        data = {}

    if data and "side" in data:
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

        mensaje = (
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
    else:
        mensaje = body

    if mensaje:
        send_telegram(mensaje)
        return "OK", 200
    return "Empty", 400

@app.route("/", methods=["GET"])
def home():
    return "Angel Bot - Online ✅", 200

if __name__ == "__main__":
    t = threading.Thread(target=keep_alive, daemon=True)
    t.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
