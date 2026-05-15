import telebot
from flask import Flask, request

# 从Railway环境变量读取Token
import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# 你要的回复内容
REPLY = """上头音乐 DJ 串烧 @DJRRS
中国人聊天群 @GBJL88
商务合作 @lmdoi"""

# 监听所有访客@消息 + 普通消息
@bot.message_handler(func=lambda msg: True)
def handle_all(msg):
    bot.reply_to(msg, REPLY)

# Webhook路由
@app.route('/bot', methods=['POST'])
def webhook():
    data = request.get_data().decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(data)])
    return "ok", 200

# 启动Webhook
if __name__ == "__main__":
    import time
    time.sleep(3)
    # 自动获取Railway域名
    domain = os.environ.get("RAILWAY_STATIC_URL")
    bot.remove_webhook()
    bot.set_webhook(url=domain + "bot")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
