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

# 极简回复内容（纯文本，无任何格式/换行）
REPLY_TEXT = "回复成功"

@app.route("/bot", methods=["POST"])
def webhook():
    try:
        raw_data = request.get_data().decode("utf-8")
        data = json.loads(raw_data)

        if "guest_message" in data:
            guest_msg = data["guest_message"]
            guest_query_id = guest_msg.get("guest_query_id")

            print(f"📥 收到guest_message | query_id: {guest_query_id}")

            if guest_query_id:
                # 严格按照官方文档的最简格式构造results
                results = [{
                    "type": "article",
                    "id": "1",
                    "title": "回复",
                    "input_message_content": {
                        "type": "text",
                        "message_text": REPLY_TEXT
                    }
                }]

                # 关键：直接打印构造的JSON，确认格式正确
                print(f"📝 构造的results: {json.dumps(results)}")

                # 调用answerGuestQuery，用POST+JSON体
                api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerGuestQuery"
                payload = {
                    "guest_query_id": guest_query_id,
                    "results": results
                }

                response = requests.post(
                    api_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )

                print(f"🔗 API状态码: {response.status_code} | 返回: {response.text}")

                if response.status_code == 200 and response.json().get("ok"):
                    print("✅ 回复成功！")
                else:
                    print(f"❌ 回复失败: {response.text}")

        return "ok", 200
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return "error", 500

if __name__ == "__main__":
    import time
    time.sleep(3)

    # 设置Webhook
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
    webhook_url = f"{RAILWAY_DOMAIN}/bot"
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}")
    print(f"🔗 Webhook设置: {webhook_url}")

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
