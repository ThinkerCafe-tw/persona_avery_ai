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

# 🧠 強制載入記憶系統 (沒有記憶就崩潰)
from simple_memory import SimpleLumiMemory
memory = SimpleLumiMemory()
print("🧠 記憶系統已強制啟動 - 無記憶不運行")

# 🎭 載入人格系統
from persona_prompts import PersonaPrompts, PersonaMode
print("🎭 六人格系統已載入 - 療癒/幽默/閨蜜/知性/導師/智者")

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

print("🚀 Lumi LINE Bot - 六人格記憶版本")
print("=" * 50)
print(f"🧠 Gemini AI:        {'✅ 強制要求' if gemini_available else '❌ 系統崩潰'}")
print(f"🧠 記憶系統:         ✅ 強制啟動")
print(f"🎭 六人格系統:       ✅ 療癒/幽默/閨蜜/知性/導師/智者")
print(f"🎤 Whisper STT:      ⏸️ (暫時停用 - 避免映像大小限制)")
print(f"💾 映像大小:         < 1GB (Railway 相容)")

def build_smart_prompt(user_message, user_info, recent_memories, persona_mode=None):
    """
    智能構建提示詞，支援六種人格模式
    """
    
    # 檢測或使用指定的人格模式
    if not persona_mode:
        # 自動檢測人格模式
        persona_mode = PersonaPrompts.detect_persona_from_message(user_message)
        
        # 檢查是否為手動切換指令
        switch_commands = PersonaPrompts.get_persona_switch_commands()
        for cmd, mode in switch_commands.items():
            if cmd in user_message:
                persona_mode = mode
                # 存儲用戶的人格偏好
                if user_info:
                    memory.set_user_info(user_info.get('user_id', 'default'), 'preferred_persona', mode.value)
                break
    
    # 如果沒有檢測到特定模式，使用用戶偏好或默認閨蜜模式
    if not persona_mode:
        if user_info and user_info.get('preferred_persona'):
            try:
                persona_mode = PersonaMode(user_info['preferred_persona'])
            except ValueError:
                persona_mode = PersonaMode.BESTIE  # 默認閨蜜模式
        else:
            persona_mode = PersonaMode.BESTIE  # 默認閨蜜模式
    
    # 使用人格系統生成提示詞
    prompt = PersonaPrompts.get_persona_prompt(
        mode=persona_mode,
        user_message=user_message,
        user_info=user_info,
        recent_memories=recent_memories
    )
    
    return prompt, persona_mode

def get_ai_response(text, user_id=None):
    """
    使用 Gemini AI 生成回應 (帶六人格智能記憶功能)
    """
    if not gemini_available:
        return "🤖 AI 系統正在初始化中，請稍後再試。"
    
    try:
        # 強制使用記憶系統 (沒有用戶ID就報錯)
        if not user_id:
            raise ValueError("❌ 必須提供用戶ID才能使用記憶功能")
        
        # 獲取用戶記憶上下文
        user_info = memory.get_user_info(user_id)
        user_info['user_id'] = user_id  # 確保 user_id 在 user_info 中
        recent_memories = memory.get_recent_memories(user_id, limit=3)
        
        # 智能構建提示詞 (支援六人格)
        prompt, active_persona = build_smart_prompt(text, user_info, recent_memories)
        
        print(f"🎭 使用人格: {active_persona.value}")
        
        response = gemini_model.generate_content(prompt)
        
        if response and response.text:
            response_text = response.text.strip()
            
            # 儲存記憶，包含使用的人格模式
            emotion_tag = active_persona.value.split('模式')[0] if '模式' in active_persona.value else active_persona.value
            memory.add_interaction(user_id, text, response_text, emotion_tag)
            
            # 如果用戶手動切換人格，給予確認
            switch_commands = PersonaPrompts.get_persona_switch_commands()
            if any(cmd in text for cmd in switch_commands.keys()):
                response_text = f"✨ 已切換到 {active_persona.value} ✨\n\n{response_text}"
            
            return response_text
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
    
    # 獲取 AI 回應 (傳入用戶ID以支援記憶)
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
        "version": "Six Persona Version v2.0",
        "architecture": "Gemini AI + pgvector + Six Persona System",
        "status": "running",
        "features": {
            "text_chat": True,
            "gemini_ai": gemini_available,
            "memory_system": memory.use_pgvector,
            "persona_modes": ["療癒對話", "幽默聊天", "閨蜜模式", "知性深度", "心靈導師", "日記智者"],
            "voice_stt": False,
            "voice_tts": False
        },
        "persona_system": {
            "available_modes": 6,
            "auto_detection": True,
            "manual_switching": True,
            "default_mode": "閨蜜模式"
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