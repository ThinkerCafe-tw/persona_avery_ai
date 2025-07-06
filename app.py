import os
import logging
from flask import Flask, request, abort
from linebot.v3.messaging import (
    Configuration,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
import ai_logic
import simple_memory

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# LINE Bot 設定
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
channel_secret = os.getenv('LINE_CHANNEL_SECRET')

if not channel_access_token or not channel_secret:
    logger.error("❌ LINE Bot 環境變數未設定")
    raise ValueError("LINE_CHANNEL_ACCESS_TOKEN 和 LINE_CHANNEL_SECRET 必須設定")

# 初始化 LINE Bot API
configuration = Configuration(access_token=channel_access_token)
line_bot_api = MessagingApi(configuration)
handler = WebhookHandler(channel_secret)

# 初始化記憶系統
memory_system = simple_memory.SimpleLumiMemory()

@app.route("/")
def home():
    return "Lumi AI 正在運行！🤖✨"

@app.route("/health")
def health_check():
    try:
        # 測試資料庫連接
        if memory_system._ensure_connection():
            return {"status": "healthy", "message": "Lumi AI 運行正常"}, 200
        else:
            return {"status": "unhealthy", "error": "資料庫連接失敗"}, 500
    except Exception as e:
        logger.error(f"❌ 健康檢查失敗: {e}")
        return {"status": "unhealthy", "error": str(e)}, 500

@app.route("/callback", methods=['POST'])
def callback():
    # 獲取 X-Line-Signature header
    signature = request.headers['X-Line-Signature']

    # 獲取 request body
    body = request.get_data(as_text=True)
    logger.info("✅ LINE webhook 收到請求")
    logger.info(f"📝 請求內容長度: {len(body)}")

    try:
        handler.handle(body, signature)
        logger.info("✅ webhook 處理成功")
    except InvalidSignatureError:
        logger.error("❌ 簽名驗證失敗")
        abort(400)
    except Exception as e:
        logger.error(f"❌ webhook 處理失敗: {e}")
        abort(500)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    logger.info("=== 開始處理訊息 ===")
    try:
        user_id = event.source.user_id
        user_message = event.message.text
        
        logger.info(f"📨 收到用戶 {user_id} 的訊息: {user_message}")
        logger.info(f"🔑 reply_token: {event.reply_token}")
        
        # 使用 AI 邏輯生成回應
        logger.info("🤖 開始生成 AI 回應...")
        lumi_response = ai_logic.get_lumi_response(user_message, user_id)
        
        logger.info(f"🤖 Lumi 回覆內容： {lumi_response}")
        
        # 發送回應
        logger.info("📤 開始發送回應...")
        try:
            reply_request = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=lumi_response)]
            )
            line_bot_api.reply_message(reply_request)
            logger.info("✅ 訊息發送成功")
        except Exception as e:
            logger.error(f"❌ 發送失敗：{e}")
            logger.error(f"❌ 錯誤類型：{type(e)}")
            logger.error(f"❌ 詳細錯誤：{e}")
            
    except Exception as e:
        logger.error(f"❌ 處理訊息時發生錯誤: {e}")
        import traceback
        logger.error(f"❌ 詳細錯誤堆疊: {traceback.format_exc()}")
    
    logger.info("=== 訊息處理結束 ===")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True) 