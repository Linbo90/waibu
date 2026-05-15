import telebot
from flask import Flask, request
import os

# 从Railway环境变量读取Token
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("请在Railway的Variables中设置BOT_TOKEN环境变量")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# 你要的回复内容
REPLY = """上头音乐 DJ 串烧 @DJRRS
中国人聊天群 @GBJL88
商务合作 @lmdoi"""

# 监听所有@提及消息（关键：只处理@机器人的消息）
@bot.message_handler(func=lambda msg: msg.entities and any(e.type == 'mention' and e.user.username == bot.get_me().username for e in msg.entities))
def handle_mention(msg):
    try:
        bot.reply_to(msg, REPLY)
        print(f"✅ 成功回复群聊消息 | 聊天ID: {msg.chat.id}")
    except Exception as e:
        print(f"❌ 回复失败: {e}")

# Webhook路由
@app.route('/bot', methods=['POST'])
def webhook():
    try:
        data = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(data)
        bot.process_new_updates([update])
        return "ok", 200
    except Exception as e:
        print(f"❌ Webhook处理错误: {e}")
        return "error", 500

# 启动Webhook
if __name__ == "__main__":
    import time
    time.sleep(3)
    
    # 修复：改用Railway新的环境变量RAILWAY_PUBLIC_DOMAIN
    domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
    
    if not domain:
        print("❌ 无法获取Railway域名，请手动配置环境变量RAILWAY_PUBLIC_DOMAIN")
        exit(1)
    
    # 确保域名格式正确（带https://）
    if not domain.startswith("https://"):
        domain = f"https://{domain}"
    
    webhook_url = f"{domain}/bot"
    print(f"🔗 设置Webhook: {webhook_url}")
    
    # 先移除旧的Webhook，再设置新的
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=webhook_url)
    
    # 启动Flask应用
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
