import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
BOT_USERNAME = os.getenv("BOT_USERNAME", "@uuuuloikbot").strip()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "tg_guest_hook").strip()

PUBLIC_DOMAIN = os.getenv("PUBLIC_DOMAIN", "waibu-production.up.railway.app").strip()
PORT = int(os.getenv("PORT", "8080"))

API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def set_webhook():
    webhook_url = f"https://{PUBLIC_DOMAIN}/{WEBHOOK_SECRET}"
    payload = {
        "url": webhook_url,
        "allowed_updates": ["guest_message"],
    }
    r = requests.post(f"{API}/setWebhook", json=payload, timeout=20)
    r.raise_for_status()
    print("Webhook set:", r.json())


def answer_guest_query(guest_query_id: str):
    result = {
        "type": "photo",
        "id": "reply_card_1",
        "photo_url": "https://cdn.phototourl.com/free/2026-05-16-6823516e-43e8-41a2-95eb-96e811e34fb6.jpg",
        "thumbnail_url": "https://cdn.phototourl.com/free/2026-05-16-6823516e-43e8-41a2-95eb-96e811e34fb6.jpg",
        "caption": (
            '<a href="https://t.me/DJRRS">上头DJ @DJRRS</a>\n'
            '<a href="https://t.me/GBJL88">聊天群 @GBJL88</a>\n'
            '<a href="https://t.me/WNFFX">文案馆 @WNFFX</a>\n'
            '<a href="https://t.me/hrgxx">搞笑吃瓜 @hrgxx</a>\n'
            '<a href="https://t.me/lmdoi">商务合作 @lmdoi</a>'
        ),
        "parse_mode": "HTML",
    }

    payload = {
        "guest_query_id": guest_query_id,
        "result": result,
    }

    r = requests.post(f"{API}/answerGuestQuery", json=payload, timeout=20)
    r.raise_for_status()
    print("answerGuestQuery:", r.json())


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != f"/{WEBHOOK_SECRET}":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"

        try:
            update = json.loads(raw.decode("utf-8"))
        except Exception:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Bad Request")
            return

        guest_message = update.get("guest_message")
        if guest_message:
            text = (guest_message.get("text") or "").strip().lower()
            guest_query_id = guest_message.get("guest_query_id")

            if guest_query_id and BOT_USERNAME.lower() in text:
                try:
                    answer_guest_query(guest_query_id)
                except Exception as e:
                    print("reply failed:", repr(e))

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is required")

    set_webhook()
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Listening on 0.0.0.0:{PORT}")
    server.serve_forever()