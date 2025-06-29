#!/usr/bin/env python3
"""
🚀 Lumi LINE Bot - Cruz 最優架構版本
使用 Whisper + Gemini + 11Labs 的簡化架構
"""

import os
from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest,
    TextMessage, AudioMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent, AudioMessageContent
from datetime import datetime
import json
import requests
import tempfile

# 🚀 導入 Cruz 最優架構組件
from whisper_stt import whisper_stt
from gemini_ai import gemini_ai
from simple_memory import SimpleLumiMemory

load_dotenv()
app = Flask(__name__)

# LINE Bot 設定
line_bot_api = MessagingApi(ApiClient(Configuration(
    access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
)))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# 🧠 初始化記憶系統
memory = SimpleLumiMemory()

# 🔊 11Labs TTS 設定
elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')

print("🚀 Lumi LINE Bot - Cruz 最優架構")
print("=" * 50)
print(f"🎤 Whisper STT:      {'✅' if whisper_stt.enabled else '❌'}")
print(f"🧠 Gemini AI:        {'✅' if gemini_ai.enabled else '❌'}")
print(f"🔊 11Labs TTS:       {'✅' if elevenlabs_api_key else '❌'}")
print(f"🧠 記憶系統:         ✅")

class LumiVoiceSystem:
    """
    Lumi 語音系統整合類
    """
    
    def process_text_message(self, user_id, text):
        """
        處理文字訊息
        """
        try:
            # 從記憶中獲取用戶資訊
            user_info = memory.get_user_info(user_id)
            
            # 使用 Gemini 生成回應
            response = gemini_ai.get_personalized_response(text, user_info)
            
            if response:
                # 更新記憶
                memory.add_interaction(user_id, text, response)
                return response
            else:
                return "抱歉，我現在無法回應。請稍後再試。"
                
        except Exception as e:
            print(f"❌ 處理文字訊息失敗: {e}")
            return "抱歉，處理訊息時發生錯誤。"
    
    def process_audio_message(self, user_id, audio_content):
        """
        處理語音訊息 - 使用 Whisper STT
        """
        try:
            print(f"🎤 處理用戶 {user_id} 的語音訊息")
            
            # 1. 語音轉文字 (Whisper)
            transcribed_text = whisper_stt.transcribe_audio_content(
                audio_content, 
                audio_format="m4a",  # LINE 語音格式
                language="zh"
            )
            
            if not transcribed_text:
                return "抱歉，我無法理解您的語音內容。請再試一次。"
            
            print(f"✅ 語音轉文字: {transcribed_text}")
            
            # 2. 處理轉錄的文字
            response = self.process_text_message(user_id, transcribed_text)
            
            # 3. 可選：生成語音回應
            # TODO: 這裡可以加入 TTS 功能
            
            return f"🎤 您說：{transcribed_text}\n\n{response}"
            
        except Exception as e:
            print(f"❌ 處理語音訊息失敗: {e}")
            return "抱歉，處理語音時發生錯誤。"
    
    def generate_voice_response(self, text, voice_id="ErXwobaYiN019PkySvjV"):
        """
        生成語音回應 (可選功能)
        """
        if not elevenlabs_api_key:
            return None
        
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"❌ TTS 失敗: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 語音生成失敗: {e}")
            return None

# 初始化語音系統
voice_system = LumiVoiceSystem()

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
    
    # 處理訊息
    response_text = voice_system.process_text_message(user_id, user_text)
    
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
    處理語音訊息 - 使用 Whisper STT
    """
    user_id = event.source.user_id
    message_id = event.message.id
    
    print(f"🎤 收到語音訊息 (用戶: {user_id}, 訊息ID: {message_id})")
    
    try:
        # 從 LINE 下載語音檔案
        audio_content = line_bot_api.get_message_content(message_id)
        audio_data = b''.join(audio_content.iter_content())
        
        # 處理語音
        response_text = voice_system.process_audio_message(user_id, audio_data)
        
        # 回覆訊息
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)]
            )
        )
        
    except Exception as e:
        print(f"❌ 語音訊息處理失敗: {e}")
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="抱歉，處理語音時發生錯誤。請稍後再試。")]
            )
        )

@app.route("/")
def hello():
    """
    健康檢查端點
    """
    status = {
        "service": "Lumi LINE Bot",
        "architecture": "Cruz Optimal (Whisper + Gemini + 11Labs)",
        "status": "running",
        "components": {
            "whisper_stt": whisper_stt.enabled,
            "gemini_ai": gemini_ai.enabled,
            "elevenlabs_tts": bool(elevenlabs_api_key),
            "memory_system": True
        },
        "gemini_usage": f"{gemini_ai.daily_usage}/{gemini_ai.daily_limit}" if gemini_ai.enabled else "N/A"
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