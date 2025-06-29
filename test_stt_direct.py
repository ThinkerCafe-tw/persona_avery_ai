#!/usr/bin/env python3
"""
直接測試 STT 系統初始化
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

def test_stt_initialization():
    """測試 STT 系統初始化"""
    print("🎤 測試 STT 系統初始化...")
    print("=" * 40)
    
    # 檢查環境變數
    credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if not credentials_json:
        print("❌ 未找到 GOOGLE_APPLICATION_CREDENTIALS_JSON")
        return False
    
    print("✅ 找到 Google 認證 JSON")
    
    try:
        # 解析 JSON
        credentials_dict = json.loads(credentials_json)
        project_id = credentials_dict.get('project_id')
        print(f"✅ 專案 ID: {project_id}")
        
        # 嘗試初始化 Speech-to-Text
        from google.cloud import speech
        from google.oauth2 import service_account
        
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        client = speech.SpeechClient(credentials=credentials)
        
        print("✅ Speech-to-Text 客戶端初始化成功")
        
        # 測試基本功能
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code="zh-TW",
        )
        
        print("✅ 認識設定建立成功")
        print("🎉 STT 系統完全正常！")
        
        return True
        
    except Exception as e:
        print(f"❌ STT 初始化失敗: {e}")
        return False

if __name__ == "__main__":
    success = test_stt_initialization()
    if success:
        print("\n💡 現在可以導入 speech_to_text 模組")
        
        # 測試實際模組
        try:
            from speech_to_text import stt_system
            print(f"✅ STT 系統狀態: {'已啟用' if stt_system.enabled else '未啟用'}")
            if stt_system.enabled:
                print(f"   專案: {stt_system.project_id}")
        except Exception as e:
            print(f"❌ 模組導入失敗: {e}")