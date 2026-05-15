import telebot
from flask import Flask, request
import os
import json
import requests

# 读取Railway环境变量
BOT_TOKEN = os.environ.get("BOT_TOKEN")
RAILWAY_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN")

if not BOT_TOKEN or not RAILWAY_DOMAIN:
    raise ValueError("请在Railway的Variables中设置BOT_TOKEN和RAILWAY_PUBLIC_DOMAIN")

if not RAILWAY_DOMAIN.startswith("https://"):
    RAILWAY_DOMAIN = f"https://{RAILWAY_DOMAIN}"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# 你要的回复内容
REPLY_TEXT = """上头音乐 DJ 串烧 @DJRRS
中国人聊天群 @GBJL88
商务合作 @lmdoi"""

# ---------------------- 关键修复：改用POST请求传递JSON，避免URL编码 ----------------------
@app.route('/bot', methods=['POST'])
def webhook():
    try:
        raw_data = request.get_data().decode('utf-8')
        print(f"📩 收到Telegram推送：{raw_data}")
        
        data = json.loads(raw_data)
        
        if "guest_message" in data:
            guest_msg = data["guest_message"]
            guest_query_id = guest_msg.get("guest_query_id")
            chat_id = guest_msg["chat"]["id"]
            text = guest_msg["text"]
            
            print(f"📥 收到访客消息：{text} | query_id: {guest_query_id}")
            
            if guest_query_id:
                # 构造回复（格式保持不变）
                results = [{
                    "type": "article",
                    "id": "1",
                    "title": "回复",
                    "input_message_content": {
                        "message_text": REPLY_TEXT
                    }
                }]
                
                # 调用answerGuestQuery API，改用POST请求，传递原始JSON
                api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerGuestQuery"
                payload = {
                    "guest_query_id": guest_query_id,
                    "results": results  # 直接传递Python列表，requests会自动序列化JSON
                }
                
                # 关键：用POST请求，且用json参数传递，避免URL编码
                response = requests.post(api_url, json=payload)
                print(f"🔗 API返回：{response.status_code} {response.text}")
                
                if response.status_code == 200 and response.json().get("ok"):
                    print(f"✅ 回复成功！消息已发送到群聊")
                else:
                    print(f"❌ 回复失败，API错误：{response.text}")
        
        return "ok", 200
    except Exception as e:
        print(f"❌ 错误：{str(e)}")
        return "error", 500

# ---------------------- 初始化Webhook ----------------------
if __name__ == "__main__":
    import time
    time.sleep(3)
    
    webhook_url = f"{RAILWAY_DOMAIN}/bot"
    print(f"🔗 设置Webhook：{webhook_url}")
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
