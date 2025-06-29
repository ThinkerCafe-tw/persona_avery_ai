#!/usr/bin/env python3
"""
🔍 Lumi LINE Bot - 診斷版本
逐步檢查哪個組件導致崩潰
"""

import os
import sys
from datetime import datetime

print("🔍 [DEBUG] Python 版本:", sys.version)
print("🔍 [DEBUG] 開始時間:", datetime.now())

try:
    print("🔍 [DEBUG] 載入 Flask...")
    from flask import Flask, request, abort
    print("✅ [DEBUG] Flask 載入成功")
except Exception as e:
    print(f"❌ [DEBUG] Flask 載入失敗: {e}")
    sys.exit(1)

try:
    print("🔍 [DEBUG] 載入 dotenv...")
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ [DEBUG] dotenv 載入成功")
except Exception as e:
    print(f"❌ [DEBUG] dotenv 載入失敗: {e}")
    sys.exit(1)

try:
    print("🔍 [DEBUG] 載入 LINE Bot SDK...")
    from linebot.v3 import WebhookHandler
    from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
    print("✅ [DEBUG] LINE Bot SDK 載入成功")
except Exception as e:
    print(f"❌ [DEBUG] LINE Bot SDK 載入失敗: {e}")
    sys.exit(1)

try:
    print("🔍 [DEBUG] 檢查環境變數...")
    line_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    line_secret = os.getenv('LINE_CHANNEL_SECRET')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    print(f"🔍 [DEBUG] LINE_CHANNEL_ACCESS_TOKEN: {'設定' if line_token else '未設定'}")
    print(f"🔍 [DEBUG] LINE_CHANNEL_SECRET: {'設定' if line_secret else '未設定'}")
    print(f"🔍 [DEBUG] GEMINI_API_KEY: {'設定' if gemini_key else '未設定'}")
    
    if not line_token or not line_secret:
        print("❌ [DEBUG] LINE Bot 環境變數缺失")
        sys.exit(1)
    
    print("✅ [DEBUG] 環境變數檢查通過")
except Exception as e:
    print(f"❌ [DEBUG] 環境變數檢查失敗: {e}")
    sys.exit(1)

# 嘗試載入自定義模組 (可能的問題點)
try:
    print("🔍 [DEBUG] 嘗試載入 gemini_ai...")
    from gemini_ai import gemini_ai
    print("✅ [DEBUG] gemini_ai 載入成功")
    gemini_available = True
except Exception as e:
    print(f"⚠️ [DEBUG] gemini_ai 載入失敗: {e}")
    gemini_available = False

try:
    print("🔍 [DEBUG] 嘗試載入 whisper_stt...")
    from whisper_stt import whisper_stt
    print("✅ [DEBUG] whisper_stt 載入成功")
    whisper_available = True
except Exception as e:
    print(f"⚠️ [DEBUG] whisper_stt 載入失敗: {e}")
    whisper_available = False

try:
    print("🔍 [DEBUG] 嘗試載入 simple_memory...")
    from simple_memory import SimpleLumiMemory
    memory = SimpleLumiMemory()
    print("✅ [DEBUG] simple_memory 載入成功")
    memory_available = True
except Exception as e:
    print(f"⚠️ [DEBUG] simple_memory 載入失敗: {e}")
    memory_available = False

# 創建 Flask 應用
try:
    print("🔍 [DEBUG] 創建 Flask 應用...")
    app = Flask(__name__)
    print("✅ [DEBUG] Flask 應用創建成功")
except Exception as e:
    print(f"❌ [DEBUG] Flask 應用創建失敗: {e}")
    sys.exit(1)

# 設定 LINE Bot
try:
    print("🔍 [DEBUG] 設定 LINE Bot...")
    line_bot_api = MessagingApi(ApiClient(Configuration(
        access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    )))
    handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
    print("✅ [DEBUG] LINE Bot 設定成功")
except Exception as e:
    print(f"❌ [DEBUG] LINE Bot 設定失敗: {e}")
    sys.exit(1)

@app.route("/")
def hello():
    return {
        "service": "Lumi LINE Bot",
        "version": "Debug Version", 
        "status": "running",
        "debug_info": {
            "gemini_ai": gemini_available,
            "whisper_stt": whisper_available,
            "memory_system": memory_available,
            "timestamp": datetime.now().isoformat()
        }
    }

@app.route("/health")
def health():
    return {"status": "healthy"}

@app.route("/callback", methods=['POST'])
def callback():
    return 'OK'

if __name__ == "__main__":
    try:
        print("🔍 [DEBUG] 準備啟動 Flask...")
        port = int(os.environ.get("PORT", 5000))
        print(f"🔍 [DEBUG] 使用端口: {port}")
        print("🔍 [DEBUG] 啟動 Flask 應用...")
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        print(f"❌ [DEBUG] Flask 啟動失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)