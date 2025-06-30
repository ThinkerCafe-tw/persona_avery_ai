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

print("🚀 Lumi LINE Bot - 記憶強制版本")
print("=" * 50)
print(f"🧠 Gemini AI:        {'✅ 強制要求' if gemini_available else '❌ 系統崩潰'}")
print(f"🧠 記憶系統:         ✅ 強制啟動")
print(f"🎤 Whisper STT:      ⏸️ (暫時停用 - 避免映像大小限制)")
print(f"💾 映像大小:         < 1GB (Railway 相容)")

def build_smart_prompt(user_message, user_info, recent_memories):
    """
    智能構建提示詞，避免幻覺記憶問題
    """
    
    # 基本人格設定
    prompt = """你是 Lumi，一個溫暖親切的 AI 朋友。

你的個性特點：
- 溫暖但不過度熱情
- 真誠且有點俏皮
- 會適度關心但不會過度擔心
- 說話自然，像個真實的朋友
- 對話是延續的，不要像要結束話題

回應風格：
- 避免使用「希望你一切安好」、「希望你今天過得很好」等結束語
- 不要用客套的祝福語結尾
- 多問問題或給回應空間，保持對話活躍
- 用日常聊天的語氣，不是正式問候

格式要求：
- 每個不同想法都要換行分段
- 不要用空格分段，要用真正的換行
- 回應簡潔但溫暖
- 可以用一些表情符號，但不要過多

記憶使用原則：
- 只使用你確實知道的記憶
- 沒有記憶就當作第一次聊天
- 不要編造任何對話內容

"""
    
    # 檢查是否有有效的用戶資訊
    has_valid_memory = False
    
    if user_info.get('name'):
        prompt += f"用戶資訊：這位用戶叫 {user_info['name']}"
        if user_info.get('job'):
            prompt += f"，職業是 {user_info['job']}"
        prompt += "。\n\n"
        has_valid_memory = True
    
    # 檢查是否有有效的對話記憶 (至少2條有意義的對話)
    if recent_memories and len(recent_memories) >= 2:
        valid_conversations = []
        for mem in recent_memories:
            user_msg = mem.get('user_message', '').strip()
            # 過濾掉太短或測試性質的訊息
            if len(user_msg) > 5 and not user_msg.startswith('測試'):
                valid_conversations.append(mem)
        
        if len(valid_conversations) >= 2:
            prompt += "最近的對話記錄：\n"
            for mem in valid_conversations[-2:]:  # 只取最近2條
                prompt += f"- 用戶：{mem.get('user_message', '')}\n"
                prompt += f"- 你：{mem.get('lumi_response', '')}\n"
            prompt += "\n"
            has_valid_memory = True
    
    # 根據記憶情況調整回應指導
    if not has_valid_memory:
        prompt += "這似乎是你們第一次聊天，要自然友善地介紹自己。\n\n"
    else:
        prompt += "基於以上記憶，像老朋友一樣自然地回應。\n\n"
    
    prompt += f"用戶現在說：{user_message}\n\n"
    prompt += """請回應：
- 用溫暖朋友的語氣，像朋友間日常聊天
- 每個想法都要換行分段
- 真實不編造
- 適度關心但不說教
- 不要用結束語，保持對話開放性
- 可以問問題或給予回應空間"""
    
    return prompt

def get_ai_response(text, user_id=None):
    """
    使用 Gemini AI 生成回應 (帶智能記憶功能)
    """
    if not gemini_available:
        return "🤖 AI 系統正在初始化中，請稍後再試。"
    
    try:
        # 強制使用記憶系統 (沒有用戶ID就報錯)
        if not user_id:
            raise ValueError("❌ 必須提供用戶ID才能使用記憶功能")
        
        # 獲取用戶記憶上下文
        user_info = memory.get_user_info(user_id)
        recent_memories = memory.get_recent_memories(user_id, limit=3)
        
        # 智能構建提示詞
        prompt = build_smart_prompt(text, user_info, recent_memories)
        
        response = gemini_model.generate_content(prompt)
        
        if response and response.text:
            response_text = response.text.strip()
            
            # 強制儲存記憶 (失敗就報錯)
            memory.add_interaction(user_id, text, response_text)
            
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