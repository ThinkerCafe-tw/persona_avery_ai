#!/usr/bin/env python3
"""
🧪 測試新的 Google Cloud 憑證
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

def test_new_google_credentials():
    """測試新的 Google Cloud 憑證"""
    try:
        print("🔍 檢查新憑證...")
        
        # 檢查環境變數
        project_id = os.getenv('VERTEX_AI_PROJECT_ID')
        credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        
        print(f"   Project ID: {project_id}")
        
        if credentials_json:
            creds = json.loads(credentials_json)
            print(f"   Service Account: {creds.get('client_email')}")
            print(f"   認證專案: {creds.get('project_id')}")
            
            if creds.get('project_id') == project_id:
                print("✅ 專案 ID 匹配!")
            else:
                print("❌ 專案 ID 不匹配!")
                return False
        
        # 測試 Vertex AI 連接
        print("\n🤖 測試 Vertex AI 連接...")
        try:
            import vertexai
            from vertexai.preview.generative_models import GenerativeModel
            from google.oauth2 import service_account
            
            # 建立認證
            credentials = service_account.Credentials.from_service_account_info(creds)
            
            # 初始化 Vertex AI
            vertexai.init(project=project_id, location="us-central1", credentials=credentials)
            
            # 嘗試建立模型
            model = GenerativeModel("gemini-1.5-flash")
            print("✅ Vertex AI 初始化成功!")
            
            # 測試簡單調用
            response = model.generate_content("Hello, say hi in Chinese")
            print(f"✅ Vertex AI 測試成功: {response.text[:50]}...")
            
            return True
            
        except Exception as e:
            if "SERVICE_DISABLED" in str(e) or "403" in str(e):
                print("⚠️ Vertex AI API 未啟用，需要手動啟用")
                print(f"   前往: https://console.developers.google.com/apis/api/aiplatform.googleapis.com/overview?project={project_id}")
            else:
                print(f"❌ Vertex AI 錯誤: {e}")
            return False
        
    except Exception as e:
        print(f"❌ 憑證測試失敗: {e}")
        return False

def test_speech_to_text():
    """測試 Speech-to-Text API"""
    try:
        print("\n🎤 測試 Speech-to-Text API...")
        from google.cloud import speech
        from google.oauth2 import service_account
        
        credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        creds = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(creds)
        
        client = speech.SpeechClient(credentials=credentials)
        print("✅ Speech-to-Text 初始化成功!")
        return True
        
    except Exception as e:
        if "SERVICE_DISABLED" in str(e) or "403" in str(e):
            project_id = os.getenv('VERTEX_AI_PROJECT_ID')
            print("⚠️ Speech-to-Text API 未啟用")
            print(f"   前往: https://console.developers.google.com/apis/api/speech.googleapis.com/overview?project={project_id}")
        else:
            print(f"❌ Speech-to-Text 錯誤: {e}")
        return False

def main():
    print("🧪 測試新的 Google Cloud 認證和 APIs")
    print("=" * 50)
    
    # 測試憑證
    creds_ok = test_new_google_credentials()
    
    # 測試 Speech-to-Text
    speech_ok = test_speech_to_text()
    
    print("\n" + "=" * 50)
    print("📋 測試結果:")
    print(f"   憑證和 Vertex AI: {'✅' if creds_ok else '❌'}")
    print(f"   Speech-to-Text: {'✅' if speech_ok else '❌'}")
    
    if creds_ok and speech_ok:
        print("\n🎉 所有系統準備就緒！可以部署到 Railway")
    else:
        print("\n⚠️ 需要啟用 APIs 後重新測試")

if __name__ == "__main__":
    main()