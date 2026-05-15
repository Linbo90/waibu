import telebot
from flask import Flask, request
import os
import json
import requests

# 读取Railway环境变量
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("请在Railway的Variables中设置BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# 你要的回复内容
REPLY_TEXT = """上头音乐 DJ 串烧 @DJRRS
中国人聊天群 @GBJL88
商务合作 @lmdoi"""

# ---------------------- 关键修复：用正确的sendMessage回复 ----------------------
@app.route('/bot', methods=['POST'])
def webhook():
    try:
        # 直接读取原始推送数据
        raw_data = request.get_data().decode('utf-8')
        print(f"📩 收到Telegram原始推送：{raw_data}")
        
        # 解析JSON数据
        data = json.loads(raw_data)
        
        # 处理访客消息（机器人不在群里时）
        if "guest_message" in data:
            guest_msg = data["guest_message"]
            chat_id = guest_msg["chat"]["id"]
            text = guest_msg["text"]
            
            print(f"📥 收到访客消息：{text} | 聊天ID：{chat_id}")
            
            # 调用正确的sendMessage API
            api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            params = {
                "chat_id": chat_id,
                "text": REPLY_TEXT
            }
            
            response = requests.get(api_url, params=params)
            print(f"🔗 调用sendMessage API，返回：{response.status_code} {response.text}")
            
            if response.status_code == 200:
                print(f"✅ 消息发送请求成功！")
            else:
                print(f"❌ 消息发送失败，API错误：{response.text}")
        
        return "ok", 200
    except Exception as e:
        print(f"❌ Webhook处理错误：{e}")
        return "error", 500

# ---------------------- 启动配置 ----------------------
if __name__ == "__main__":
    import time
    time.sleep(3)
    
    # 读取Railway域名
    domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
    if not domain:
        print("❌ 未找到RAILWAY_PUBLIC_DOMAIN环境变量")
        exit(1)
    if not domain.startswith("https://"):
        domain = f"https://{domain}"
    
    # 设置Webhook
    webhook_url = f"{domain}/bot"
    print(f"🔗 设置Webhook：{webhook_url}")
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=webhook_url)
    
    # 启动Flask
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
