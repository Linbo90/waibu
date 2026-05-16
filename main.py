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

CHANNEL_NAME = "上头音乐 DJ 串烧"
CHANNEL_USERNAME = "@DJRRS"

GROUP_NAME = "中国人聊天群"
GROUP_USERNAME = "@GBJL88"

SUPPORT_NAME = "商务合作"
SUPPORT_USERNAME = "@lmdoi"


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
        "photo_url": "https://picsum.photos/1200/900",
        "thumbnail_url": "https://picsum.photos/300/200",
        "caption": (
            "上头音乐 DJ 串烧 @DJRRS\n"
            "中国人聊天群 @GBJL88\n"
            "商务合作 @lmdoi"
        ),
        "reply_markup": {
            "inline_keyboard": [
                [{"text": CHANNEL_NAME, "url": f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"}],
                [{"text": GROUP_NAME, "url": f"https://t.me/{GROUP_USERNAME.lstrip('@')}"}],
                [{"text": SUPPORT_NAME, "url": f"https://t.me/{SUPPORT_USERNAME.lstrip('@')}"}],
            ]
        },
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