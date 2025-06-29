#!/usr/bin/env python3
"""
🚀 Lumi LINE Bot - 最小化版本 (避免 Railway 限制)
先讓 Gemini AI + LINE Bot 上線，語音功能後續優化
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

load_dotenv()
app = Flask(__name__)

# LINE Bot 設定
line_bot_api = MessagingApi(ApiClient(Configuration(
    access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
)))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# 🧠 嘗試載入 Gemini AI
try:
    import google.generativeai as genai
    
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        gemini_available = True
        print("✅ Gemini AI 已初始化")
    else:
        gemini_available = False
        print("⚠️ Gemini API Key 未設定")
        
except Exception as e:
    gemini_available = False
    print(f"❌ Gemini AI 初始化失敗: {e}")

print("🚀 Lumi LINE Bot - 最小化版本")
print("=" * 50)
print(f"🧠 Gemini AI:        {'✅' if gemini_available else '❌'}")
print(f"🎤 Whisper STT:      ⏸️ (暫時停用 - 避免映像大小限制)")
print(f"💾 映像大小:         < 1GB (Railway 相容)")

def get_ai_response(text):
    """
    使用 Gemini AI 生成回應
    """
    if not gemini_available:
        return "🤖 AI 系統正在初始化中，請稍後再試。"
    
    try:
        # 個性化提示
        prompt = f"""你是 Lumi，一個友善溫暖的 AI 助手。請用親切自然的語調回應用戶。

用戶說：{text}

請回應："""
        
        response = gemini_model.generate_content(prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            return "抱歉，我現在無法回應。請稍後再試。"
            
    except Exception as e:
        print(f"❌ Gemini API 錯誤: {e}")
        return "抱歉，AI 系統暫時無法回應。請稍後再試。"

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
    
    # 獲取 AI 回應
    response_text = get_ai_response(user_text)
    
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
    處理語音訊息 (暫時說明功能開發中)
    """
    user_id = event.source.user_id
    
    print(f"🎤 收到語音訊息 (用戶: {user_id})")
    
    response_text = """🎤 感謝您的語音訊息！

🔧 語音轉文字功能正在優化中...

目前 Lumi 可以：
✅ 文字對話 (Gemini AI)
🔄 語音功能開發中

請暫時使用文字訊息，謝謝您的耐心！"""
    
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
        "version": "Minimal Version v1.0",
        "architecture": "Gemini AI Only (Railway Optimized)",
        "status": "running",
        "features": {
            "text_chat": True,
            "gemini_ai": gemini_available,
            "voice_stt": False,
            "voice_tts": False
        },
        "deployment": {
            "image_size": "< 1GB",
            "railway_compatible": True,
            "whisper_status": "Planned for future upgrade"
        },
        "timestamp": datetime.now().isoformat()
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
    print(f"🚀 在端口 {port} 啟動 Lumi...")
    app.run(host="0.0.0.0", port=port, debug=False)