import os
from dotenv import load_dotenv
from flask import Flask, request, abort

# 使用 LINE Bot SDK v3 正確導入方式
from linebot.v3.messaging import MessagingApi, TextMessage, ReplyMessageRequest
from linebot.v3.messaging.configuration import Configuration
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
print("✅ 使用 LINE Bot SDK v3 正確導入方式")

# Import your AI logic
try:
    from ai_logic import get_lumi_response
    print("✅ AI 邏輯模組導入成功")
except Exception as e:
    print(f"⚠️ AI 邏輯模組導入失敗: {e}")
    get_lumi_response = None

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
import sys; print("✅ Flask app 啟動，Python 版本:", sys.version)
print("✅ Flask app 已初始化，準備等待 Gunicorn 啟動")

# 加強啟動日誌
print("🔍 檢查環境變數...")
print(f"🔍 LINE_CHANNEL_SECRET: {'已設定' if os.getenv('LINE_CHANNEL_SECRET') else '未設定'}")
print(f"🔍 LINE_CHANNEL_ACCESS_TOKEN: {'已設定' if os.getenv('LINE_CHANNEL_ACCESS_TOKEN') else '未設定'}")
print(f"🔍 DATABASE_URL: {'已設定' if os.getenv('DATABASE_URL') else '未設定'}")
print(f"🔍 OPENAI_API_KEY: {'已設定' if os.getenv('OPENAI_API_KEY') else '未設定'}")

# 顯示端口資訊
port = os.getenv('PORT', '8080')
print(f"✅ 應用程式將在端口 {port} 上運行")

# Get Channel Secret and Channel Access Token from environment variables
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

if CHANNEL_SECRET is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    exit(1)
if CHANNEL_ACCESS_TOKEN is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    exit(1)

# 這才是 v3 正規初始化方式！
configuration = Configuration(
    access_token=CHANNEL_ACCESS_TOKEN
)
line_bot_api = MessagingApi(configuration)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    print("=== LINE Webhook 被呼叫 ===")
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print("==== Raw body ====")
    print(body)
    
    # 這裡加入直接 parse 並印出 events
    import json
    try:
        events = json.loads(body).get("events", [])
        print("==== Events ====")
        print(events)
    except Exception as e:
        print("== 解析 events 失敗 ==")
        print(e)

    # handle webhook body
    try:
        print("🔍 開始處理 webhook...")
        handler.handle(body, signature)
        print("✅ webhook 處理成功")
    except InvalidSignatureError:
        print("❌ LINE 簽名驗證失敗")
        abort(400)
    except Exception as e:
        print(f"❌ webhook 處理失敗: {e}")
        import traceback
        print(f"❌ 詳細錯誤: {traceback.format_exc()}")
        abort(500)

    return 'OK'

@handler.add(MessageEvent)
def handle_message(event):
    print("=== handle_message 進來了 ===")
    try:
        print(f"event: {event}")
        # 判斷訊息型態
        if isinstance(event.message, TextMessageContent):
            user_message = event.message.text
            print("使用者訊息：", user_message)
            
            if get_lumi_response:
                reply_message = get_lumi_response(user_message, event.source.user_id)
                print("Lumi 回覆內容：", reply_message)
            else:
                reply_message = "抱歉，AI 系統正在初始化中，請稍後再試！"
            
            # 使用官方正確格式發送回覆
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_message)]
                )
            )
            print("✅ 發送成功")
        else:
            print("❌ 非文字訊息，忽略")
    except Exception as e:
        print(f"❌ 發送失敗：{e}")
        print(f"❌ 錯誤類型：{type(e)}")
        import traceback
        print(f"❌ 詳細錯誤：{traceback.format_exc()}")

@app.route('/health', methods=['GET'])
def health_check():
    print("✅ /health 路由被呼叫")
    print("✅ 健康檢查通過")
    return 'OK', 200

@app.route("/", methods=['GET'])
def home():
    """首頁端點"""
    print("✅ / 路由被呼叫")
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