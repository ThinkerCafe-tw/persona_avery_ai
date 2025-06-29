#!/usr/bin/env python3
"""
調試 STT 模組導入問題
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 調試 STT 模組導入...")
print("=" * 40)

# 先確保環境變數載入
from dotenv import load_dotenv
load_dotenv()
print("✅ 環境變數已載入")

# 檢查認證
credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
print(f"✅ 認證狀態: {'已找到' if credentials_json else '未找到'}")

# 然後導入 STT 系統
try:
    print("🎤 正在導入 speech_to_text...")
    from speech_to_text import stt_system
    print(f"✅ STT 系統狀態: {'已啟用' if stt_system.enabled else '未啟用'}")
    
    if stt_system.enabled:
        print(f"   專案: {stt_system.project_id}")
        print(f"   客戶端: {type(stt_system.client)}")
    else:
        print("❌ STT 系統未啟用")
        
except Exception as e:
    print(f"❌ 導入失敗: {e}")
    import traceback
    traceback.print_exc()

# 測試導入順序
print("\n🔄 測試導入 main.py...")
try:
    from main import voice_system
    print(f"✅ Voice 系統: {'已啟用' if voice_system and voice_system.enabled else '未啟用'}")
except Exception as e:
    print(f"❌ Main 導入失敗: {e}")