#!/usr/bin/env python3
"""
🔑 API Keys 檢查和診斷工具
檢查所有 API Keys 的狀態和權限
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def check_elevenlabs_api():
    """檢查 11Labs API Key 狀態"""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    
    if not api_key:
        return False, "ELEVENLABS_API_KEY 環境變數未設定"
    
    try:
        # 測試 API Key
        headers = {
            "Accept": "application/json",
            "xi-api-key": api_key
        }
        
        response = requests.get("https://api.elevenlabs.io/v1/user", headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            return True, f"11Labs API 正常 - 用戶: {user_data.get('email', 'Unknown')}"
        elif response.status_code == 401:
            return False, "11Labs API Key 無效或權限不足"
        else:
            return False, f"11Labs API 錯誤: {response.status_code} - {response.text}"
            
    except Exception as e:
        return False, f"11Labs API 連接錯誤: {e}"

def check_google_credentials():
    """檢查 Google Cloud 認證"""
    credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    
    if not credentials_json:
        return False, "GOOGLE_APPLICATION_CREDENTIALS_JSON 未設定"
    
    try:
        credentials_dict = json.loads(credentials_json)
        project_id = credentials_dict.get('project_id')
        client_email = credentials_dict.get('client_email')
        
        return True, f"Google 認證正常 - 專案: {project_id}, 帳戶: {client_email}"
        
    except Exception as e:
        return False, f"Google 認證解析錯誤: {e}"

def check_vertex_ai_access():
    """檢查 Vertex AI 存取權限"""
    try:
        import vertexai
        from vertexai.preview.generative_models import GenerativeModel
        from google.oauth2 import service_account
        
        credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        if not credentials_json:
            return False, "無法檢查 - 缺少認證"
        
        credentials_dict = json.loads(credentials_json)
        project_id = credentials_dict.get('project_id')
        
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        
        # 嘗試初始化 Vertex AI
        vertexai.init(project=project_id, location="us-central1", credentials=credentials)
        
        # 嘗試建立模型（不實際調用）
        model = GenerativeModel("gemini-1.5-flash")
        
        return True, "Vertex AI 可以初始化（API 可能已啟用）"
        
    except Exception as e:
        if "SERVICE_DISABLED" in str(e) or "403" in str(e):
            return False, "Vertex AI API 未啟用 - 需要手動啟用"
        else:
            return False, f"Vertex AI 錯誤: {e}"

def main():
    print("🔑 API Keys 和服務狀態檢查")
    print("=" * 50)
    
    # 檢查 11Labs API
    print("📋 檢查 1: 11Labs TTS API")
    elevenlabs_ok, elevenlabs_msg = check_elevenlabs_api()
    if elevenlabs_ok:
        print(f"✅ {elevenlabs_msg}")
    else:
        print(f"❌ {elevenlabs_msg}")
    
    print()
    
    # 檢查 Google 認證
    print("📋 檢查 2: Google Cloud 認證")
    google_ok, google_msg = check_google_credentials()
    if google_ok:
        print(f"✅ {google_msg}")
    else:
        print(f"❌ {google_msg}")
    
    print()
    
    # 檢查 Vertex AI
    print("📋 檢查 3: Vertex AI API 存取")
    vertex_ok, vertex_msg = check_vertex_ai_access()
    if vertex_ok:
        print(f"✅ {vertex_msg}")
    else:
        print(f"❌ {vertex_msg}")
    
    print("\n" + "=" * 50)
    print("🎯 修復建議:")
    
    if not elevenlabs_ok:
        print("   1. 🔑 檢查 11Labs API Key:")
        print("      - 前往 https://elevenlabs.io/app/speech-synthesis")
        print("      - 檢查 API Key 是否有效和有足夠額度")
        print("      - 更新 Railway 環境變數 ELEVENLABS_API_KEY")
    
    if not vertex_ok:
        print("   2. ☁️ 啟用 Vertex AI API:")
        print("      - 前往 https://console.developers.google.com/apis/api/aiplatform.googleapis.com/overview?project=probable-axon-451311-e1")
        print("      - 點擊 ENABLE 按鈕")
        print("      - 等待 2-5 分鐘生效")
    
    if elevenlabs_ok and vertex_ok:
        print("   🎉 所有服務都正常！可以測試完整語音功能")

if __name__ == "__main__":
    main()