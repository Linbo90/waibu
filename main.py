from flask import Flask, request
import os
import requests
import json

# 读取Railway环境变量
BOT_TOKEN = os.environ.get("BOT_TOKEN")
RAILWAY_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN")

if not BOT_TOKEN or not RAILWAY_DOMAIN:
    raise ValueError("请在Railway Variables中设置BOT_TOKEN和RAILWAY_PUBLIC_DOMAIN")

if not RAILWAY_DOMAIN.startswith("https://"):
    RAILWAY_DOMAIN = f"https://{RAILWAY_DOMAIN}"

app = Flask(__name__)

# 你要的回复内容（纯文本，避免格式解析错误）
REPLY_CONTENT = """上头音乐 DJ 串烧 @DJRRS
中国人聊天群 @GBJL88
商务合作 @lmdoi"""

# ---------------------- 严格按官方文档实现answerGuestQuery ----------------------
@app.route("/bot", methods=["POST"])
def webhook():
    try:
        # 读取Telegram原始推送，不依赖第三方库解析
        raw_data = request.get_data().decode("utf-8")
        print(f"📩 收到Telegram原始推送：{raw_data}")

        # 解析JSON数据
        data = json.loads(raw_data)

        # 只处理新API的guest_message（非群成员@机器人的消息）
        if "guest_message" in data:
            guest_msg = data["guest_message"]
            guest_query_id = guest_msg.get("guest_query_id")
            chat_id = guest_msg["chat"]["id"]
            text = guest_msg.get("text", "")

            print(f"📥 收到群内@提及：{text} | 群聊ID：{chat_id} | query_id：{guest_query_id}")

            if guest_query_id:
                # 严格按照官方规范构造InlineQueryResultArticle
                results = [
                    {
                        "type": "article",
                        "id": "1",
                        "title": "回复",
                        "input_message_content": {
                            "type": "text",
                            "message_text": REPLY_CONTENT
                        }
                    }
                ]

                # 打印构造的JSON，确保格式正确
                print(f"📝 构造的results JSON：{json.dumps(results)}")

                # 调用官方answerGuestQuery API，POST+JSON参数，避免URL编码
                api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerGuestQuery"
                response = requests.post(
                    api_url,
                    json={
                        "guest_query_id": guest_query_id,
                        "results": results
                    }
                )

                # 打印完整API返回，方便排查问题
                print(f"🔗 API状态码：{response.status_code} | 返回内容：{response.text}")

                if response.status_code == 200 and response.json().get("ok"):
                    print(f"✅ 回复成功！消息已直接发送到群聊")
                else:
                    print(f"❌ 回复失败，官方错误信息：{response.text}")

        return "ok", 200
    except Exception as e:
        print(f"❌ 服务器错误：{str(e)}")
        return "error", 500

# ---------------------- 初始化Webhook ----------------------
if __name__ == "__main__":
    import time
    time.sleep(3)

    # 先删除旧Webhook，避免冲突
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
    # 设置新Webhook，必须和Railway域名一致
    webhook_url = f"{RAILWAY_DOMAIN}/bot"
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}")
    print(f"🔗 Webhook设置成功：{webhook_url}")

    # 启动Flask
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
