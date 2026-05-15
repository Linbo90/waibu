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

# 回复内容：使用单行文本，避免换行符导致JSON解析问题
REPLY_CONTENT = "上头音乐 DJ 串烧 @DJRRS | 中国人聊天群 @GBJL88 | 商务合作 @lmdoi"

# ---------------------- 严格按照官方文档实现answerGuestQuery ----------------------
@app.route("/bot", methods=["POST"])
def webhook():
    try:
        # 读取Telegram原始推送
        raw_data = request.get_data().decode("utf-8")
        print(f"📩 收到Telegram推送：{raw_data}")

        # 解析JSON数据
        data = json.loads(raw_data)

        # 处理guest_message
        if "guest_message" in data:
            guest_msg = data["guest_message"]
            guest_query_id = guest_msg.get("guest_query_id")
            chat_id = guest_msg["chat"]["id"]
            text = guest_msg.get("text", "")

            print(f"📥 收到群内@提及：{text} | 群聊ID：{chat_id} | query_id：{guest_query_id}")

            if guest_query_id:
                # 1. 严格按照官方格式构造InlineQueryResultArticle
                # 必须包含type、id、title、input_message_content（含type和message_text）
                results = [{
                    "type": "article",
                    "id": "1",
                    "title": "回复",
                    "input_message_content": {
                        "type": "text",
                        "message_text": REPLY_CONTENT
                    }
                }]

                # 2. 调用answerGuestQuery API，POST请求+JSON参数
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

                # 打印完整API返回
                print(f"🔗 API状态码：{response.status_code} | 返回内容：{response.text}")

                if response.status_code == 200 and response.json().get("ok"):
                    print(f"✅ 回复成功！消息已直接发送到群聊")
                else:
                    print(f"❌ 回复失败，官方错误：{response.text}")

        return "ok", 200
    except Exception as e:
        print(f"❌ 服务器错误：{str(e)}")
        return "error", 500

# ---------------------- 初始化Webhook ----------------------
if __name__ == "__main__":
    import time
    time.sleep(3)

    # 删除旧Webhook，设置新Webhook
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
    webhook_url = f"{RAILWAY_DOMAIN}/bot"
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}")
    print(f"🔗 Webhook设置成功：{webhook_url}")

    # 启动Flask
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
