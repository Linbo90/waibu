import telebot
from flask import Flask, request
import os

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

# ---------------------- 关键修复：处理所有消息 ----------------------
@bot.message_handler(func=lambda msg: True)
def handle_any_message(msg):
    print(f"📥 收到消息：{msg}")
    print(f"📝 消息内容：{msg.text}")
    print(f"👤 发送者：{msg.from_user.username}")
    print(f"💬 聊天ID：{msg.chat.id}")
    
    # 直接回复，不管是不是@提及，先测试能否发送
    try:
        bot.send_message(msg.chat.id, REPLY_TEXT)
        print(f"✅ 回复成功，消息已发送到 {msg.chat.id}")
    except Exception as e:
        print(f"❌ 回复失败，错误：{e}")

# ---------------------- Webhook路由 ----------------------
@app.route('/bot', methods=['POST'])
def webhook():
    try:
        data = request.get_data().decode('utf-8')
        print(f"📩 收到Telegram推送：{data}")
        update = telebot.types.Update.de_json(data)
        bot.process_new_updates([update])
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
