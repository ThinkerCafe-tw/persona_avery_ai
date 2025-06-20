import os
from flask import Flask, request, abort
from dotenv import load_dotenv
import google.generativeai as genai
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# 載入環境變數
load_dotenv()

# Flask 應用程式初始化
app = Flask(__name__)

# LINE Bot 設定
line_bot_api = MessagingApi(ApiClient(Configuration(
    access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
)))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# Gemini AI 設定
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

def get_ai_response(user_message):
    """使用 Gemini AI 產生回應"""
    try:
        # 設定 AI 角色為美業助理
        prompt = f"""你是一個專業的美業助理，專精於接睫毛、美容保養等服務。
請用親切、專業的口吻回答客人的問題。
如果問題與美業無關，請禮貌地引導話題回到美業相關內容。

客人問題：{user_message}

請回答："""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"AI 回應錯誤: {e}")
        return "不好意思，我現在有點忙，請稍後再試試看～"

@app.route("/webhook", methods=['POST'])
def webhook():
    """LINE Webhook 端點"""
    # 取得 X-Line-Signature header 值
    signature = request.headers['X-Line-Signature']
    
    # 取得請求內容
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    # 處理 webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """處理文字訊息"""
    user_message = event.message.text
    
    # 使用 AI 產生回應
    ai_response = get_ai_response(user_message)
    
    # 回覆訊息
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=ai_response)]
        )
    )

@app.route("/")
def index():
    """首頁"""
    return "LINE Bot AI 助理正在運行中！"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)