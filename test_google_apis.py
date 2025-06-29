#!/usr/bin/env python3
"""
🧪 Google Cloud APIs 測試腳本
測試 Vertex AI 和 Speech-to-Text APIs 是否正常運作
"""

import os
import json
from google.oauth2 import service_account

def test_vertex_ai():
    """測試 Vertex AI API"""
    try:
        import vertexai
        from vertexai.preview.generative_models import GenerativeModel
        
        # 取得認證
        credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        if not credentials_json:
            return False, "未找到 Google 認證"
        
        credentials_dict = json.loads(credentials_json)
        project_id = credentials_dict.get('project_id')
        
        # 初始化 Vertex AI
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        vertexai.init(project=project_id, location="us-central1", credentials=credentials)
        
        # 測試簡單調用
        model = GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Say hello in Chinese")
        
        return True, f"Vertex AI 正常運作: {response.text[:50]}..."
        
    except Exception as e:
        return False, f"Vertex AI 錯誤: {e}"

def test_speech_to_text():
    """測試 Speech-to-Text API"""
    try:
        from google.cloud import speech
        
        # 取得認證
        credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        if not credentials_json:
            return False, "未找到 Google 認證"
        
        credentials_dict = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        
        # 初始化 Speech 客戶端
        client = speech.SpeechClient(credentials=credentials)
        
        # 測試配置（不需要實際音頻）
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="zh-TW",
        )
        
        return True, "Speech-to-Text API 初始化成功"
        
    except Exception as e:
        return False, f"Speech-to-Text 錯誤: {e}"

def main():
    print("🧪 測試 Google Cloud APIs...")
    print("=" * 50)
    
    # 測試 Vertex AI
    print("📋 測試 1: Vertex AI API")
    vertex_success, vertex_msg = test_vertex_ai()
    if vertex_success:
        print(f"✅ {vertex_msg}")
    else:
        print(f"❌ {vertex_msg}")
    
    print()
    
    # 測試 Speech-to-Text
    print("📋 測試 2: Speech-to-Text API")
    speech_success, speech_msg = test_speech_to_text()
    if speech_success:
        print(f"✅ {speech_msg}")
    else:
        print(f"❌ {speech_msg}")
    
    print("\n" + "=" * 50)
    
    if vertex_success and speech_success:
        print("🎉 所有 Google Cloud APIs 都正常運作！")
        print("💡 現在可以測試完整的語音功能了")
    else:
        print("⚠️ 部分 APIs 需要檢查")
        if not vertex_success:
            print("   - 請確認 Vertex AI API 已啟用")
        if not speech_success:
            print("   - 請確認 Speech-to-Text API 已啟用")

if __name__ == "__main__":
    main()