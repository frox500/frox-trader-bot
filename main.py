import os
import json
import requests
from fastapi import FastAPI, Request

app = FastAPI()

TOKEN   = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_telegram(mensaje: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id"    : CHAT_ID,
        "text"       : mensaje,
        "parse_mode" : "HTML"
    })

@app.post("/webhook")
async def webhook(request: Request):
    # ✅ Acepta JSON y texto plano
    body = await request.body()
    text = body.decode("utf-8").strip()

    try:
        data = json.loads(text)
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
        mensaje = text

    if mensaje:
        send_telegram(mensaje)
        return {"status": "ok"}
    return {"status": "empty"}

@app.get("/")
def health():
    return {"status": "Frox Alerts Bot running 🟢"}
