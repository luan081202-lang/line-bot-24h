from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from googletrans import Translator
import os

app = Flask(__name__)

# 從環境變數讀取金鑰
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
translator = Translator()

# 首頁：讓 Cron-job 檢查用
@app.route("/", methods=['GET'])
def index():
    return "Bot is running!"

# LINE Webhook 路徑
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    try:
        # 簡單判定：含英文字母就翻中，其餘翻英
        is_english = any(c.isalpha() for c in user_text) and not any('\u4e00' <= c <= '\u9fff' for c in user_text)
        dest_lang = 'zh-tw' if is_english else 'en'
        translated = translator.translate(user_text, dest=dest_lang).text
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=translated))
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="翻譯繁忙中，請稍後再試。"))

if __name__ == "__main__":
    app.run()
