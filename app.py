import os
from dotenv import load_dotenv
from flask import Flask, request, abort

# 使用 LINE Bot SDK v3 正確導入方式
from linebot.v3.messaging import MessagingApi, TextMessage
from linebot.v3.webhook import WebhookHandler, MessageEvent
from linebot.v3.exceptions import InvalidSignatureError
print("✅ 使用 LINE Bot SDK v3 正確導入方式")

# Import your AI logic
from ai_logic import get_lumi_response

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
print("✅ Flask app 已初始化，準備等待 Gunicorn 啟動")

# Get Channel Secret and Channel Access Token from environment variables
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

if CHANNEL_SECRET is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    exit(1)
if CHANNEL_ACCESS_TOKEN is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    exit(1)

line_bot_api = MessagingApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    print("✅ 收到 LINE 訊息:", user_message) 

    reply_message = get_lumi_response(user_message, event.source.user_id)
    print("🤖 Lumi 回覆內容:", reply_message)
    
    # 使用 v3 API 發送回覆
    from linebot.v3.messaging import ReplyMessageRequest
    
    request = ReplyMessageRequest(
        reply_token=event.reply_token,
        messages=[TextMessage(text=reply_message)]
    )
    line_bot_api.reply_message(request)

@app.route("/health", methods=['GET'])
def health_check():
    """Railway 健康檢查端點"""
    return {
        "status": "healthy",
        "service": "Lumi AI",
        "memory_system": "Railway pgvector",
        "timestamp": "2024-01-01T00:00:00Z"
    }, 200

@app.route("/", methods=['GET'])
def home():
    """首頁端點"""
    return {
        "message": "Lumi AI 服務運行中",
        "features": [
            "長期記憶系統",
            "Railway pgvector 服務",
            "多元人格模式",
            "LINE Bot 整合"
        ],
        "status": "active"
    }, 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False) 