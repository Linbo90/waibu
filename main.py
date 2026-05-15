from flask import Flask, request
import os
import requests
import json

BOT_TOKEN = os.environ.get("BOT_TOKEN")
RAILWAY_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN")

if not BOT_TOKEN or not RAILWAY_DOMAIN:
    raise ValueError("请设置BOT_TOKEN和RAILWAY_PUBLIC_DOMAIN")

if not RAILWAY_DOMAIN.startswith("https://"):
    RAILWAY_DOMAIN = f"https://{RAILWAY_DOMAIN}"

app = Flask(__name__)

# 回复内容（纯文本，无任何格式/换行）
REPLY_TEXT = "上头音乐 DJ 串烧 @DJRRS"

@app.route("/bot", methods=["POST"])
def webhook():
    try:
        raw_data = request.get_data().decode("utf-8")
        print(f"📩 收到Telegram推送：{raw_data}")

        data = json.loads(raw_data)

        if "guest_message" in data:
            guest_msg = data["guest_message"]
            guest_query_id = guest_msg.get("guest_query_id")

            print(f"📥 收到guest_message | query_id: {guest_query_id}")

            if guest_query_id:
                # 严格按照成功案例的格式构造results
                results = [{
                    "type": "article",
                    "id": "1",
                    "title": "回复",
                    "input_message_content": {
                        "message_text": REPLY_TEXT
                    }
                }]

                print(f"📝 构造的results JSON: {json.dumps(results)}")

                # 调用answerGuestQuery，用POST+form-data格式（和成功案例一致）
                api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerGuestQuery"
                payload = {
                    "guest_query_id": guest_query_id,
                    "results": json.dumps(results)
                }

                response = requests.post(api_url, data=payload)

                print(f"🔗 API状态码: {response.status_code} | 返回内容: {response.text}")

                if response.status_code == 200 and response.json().get("ok"):
                    print("✅ 回复成功！消息已直接发送到群聊")
                else:
                    print(f"❌ 回复失败: {response.text}")

        return "ok", 200
    except Exception as e:
        print(f"❌ 服务器错误: {str(e)}")
        return "error", 500

if __name__ == "__main__":
    import time
    time.sleep(3)

    # 设置Webhook
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
    webhook_url = f"{RAILWAY_DOMAIN}/bot"
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}")
    print(f"🔗 Webhook设置成功：{webhook_url}")

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
