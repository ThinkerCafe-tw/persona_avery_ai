#!/usr/bin/env python3
"""
🚀 Lumi LINE Bot - 應急版本 (無 Whisper)
確保基本功能運作，然後逐步添加 Whisper
"""

import os
from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent, AudioMessageContent
from datetime import datetime
import json

# 🧠 嘗試導入 Gemini AI
try:
    from gemini_ai import gemini_ai
    gemini_available = True
    print("✅ Gemini AI 已載入")
except ImportError:
    gemini_available = False
    print("⚠️ Gemini AI 模組未找到，使用備用回應")

# 🧠 嘗試導入記憶系統
try:
    from simple_memory import SimpleLumiMemory
    memory = SimpleLumiMemory()
    memory_available = True
    print("✅ 記憶系統已載入")
except ImportError:
    memory_available = False
    print("⚠️ 記憶系統未找到")

load_dotenv()
app = Flask(__name__)

# LINE Bot 設定
line_bot_api = MessagingApi(ApiClient(Configuration(
    access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
)))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

print("🚀 Lumi LINE Bot - 應急版本")
print("=" * 50)
print(f"🧠 Gemini AI:        {'✅' if gemini_available else '❌'}")
print(f"🧠 記憶系統:         {'✅' if memory_available else '❌'}")
print(f"🎤 Whisper STT:      ❌ (此版本暫時移除)")
print(f"🔊 11Labs TTS:       ⏸️ (此版本暫時停用)")

def get_ai_response(text, user_id=None):
    """
    獲取 AI 回應 (帶降級機制)
    """
    if gemini_available:
        try:
            if memory_available and user_id:
                user_info = memory.get_user_info(user_id)
                response = gemini_ai.get_personalized_response(text, user_info)
            else:
                response = gemini_ai.get_response(text)
            
            if response:
                if memory_available and user_id:
                    memory.add_interaction(user_id, text, response)
                return response
        except Exception as e:
            print(f"❌ Gemini AI 錯誤: {e}")
    
    # 備用回應
    return f"收到您的訊息：{text}\n\n目前系統正在優化中，感謝您的耐心等待！"

@app.route("/callback", methods=['POST'])
def callback():
    """
    LINE Webhook 回調
    """
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    """
    處理文字訊息
    """
    user_id = event.source.user_id
    user_text = event.message.text
    
    print(f"📝 收到文字訊息: {user_text} (用戶: {user_id})")
    
    # 獲取回應
    response_text = get_ai_response(user_text, user_id)
    
    # 回覆訊息
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=response_text)]
        )
    )

@handler.add(MessageEvent, message=AudioMessageContent)
def handle_audio_message(event):
    """
    處理語音訊息 (暫時回應說明)
    """
    user_id = event.source.user_id
    
    print(f"🎤 收到語音訊息 (用戶: {user_id})")
    
    # 暫時回應
    response_text = "🎤 感謝您的語音訊息！\n\n語音轉文字功能正在優化中，請暫時使用文字訊息。\n\n即將支援 Whisper 語音識別，敬請期待！"
    
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=response_text)]
        )
    )

@app.route("/")
def hello():
    """
    健康檢查端點
    """
    status = {
        "service": "Lumi LINE Bot",
        "version": "Fallback Version (No Whisper)",
        "status": "running",
        "components": {
            "gemini_ai": gemini_available,
            "memory_system": memory_available,
            "whisper_stt": False,
            "elevenlabs_tts": False
        },
        "note": "基礎功能運作中，語音功能開發中"
    }
    
    return json.dumps(status, indent=2, ensure_ascii=False)

@app.route("/health")
def health_check():
    """
    詳細健康檢查
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)