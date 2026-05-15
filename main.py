from flask import Flask, request
import os
import requests
import json

BOT_TOKEN = os.environ.get("BOT_TOKEN")
RAILWAY_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN")

if not BOT_TOKEN or not RAILWAY_DOMAIN:
    raise ValueError("请在Railway Variables中设置BOT_TOKEN和RAILWAY_PUBLIC_DOMAIN")

if not RAILWAY_DOMAIN.startswith("https://"):
    RAILWAY_DOMAIN = f"https://{RAILWAY_DOMAIN}"

app = Flask(__name__)

# 回复内容
REPLY_TEXT = """上头音乐 DJ 串烧 @DJRRS
中国人聊天群 @GBJL88
商务合作 @lmdoi"""

@app.route("/bot", methods=["POST"])
def webhook():
    try:
        raw_data = request.get_data().decode("utf-8")
        print(f"📩 收到Telegram推送：{raw_data}")

        data = json.loads(raw_data)

        if "guest_message" in data:
            guest_msg = data["guest_message"]
            guest_query_id = guest_msg.get("guest_query_id")

            print(f"📥 收到群内@提及 | query_id: {guest_query_id}")

            if guest_query_id:
                # 关键：使用text类型的InlineQueryResult，不需要input_message_content
                results = [{
                    "type": "text",
                    "id": "1",
                    "title": "回复",
                    "message_text": REPLY_TEXT
                }]

                print(f"📝 构造的results JSON: {json.dumps(results)}")

                # 调用answerGuestQuery API，用POST+form-data格式
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
