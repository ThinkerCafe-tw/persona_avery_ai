import os
import json
from dotenv import load_dotenv

load_dotenv()

print("🧪 測試新的 Google Cloud 憑證")
print("=" * 40)

# 檢查基本設定
project_id = os.getenv('VERTEX_AI_PROJECT_ID')
credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')

print(f"Project ID: {project_id}")

if credentials_json:
    try:
        creds = json.loads(credentials_json)
        print(f"Service Account: {creds.get('client_email')}")
        print(f"憑證專案: {creds.get('project_id')}")
        
        if creds.get('project_id') == project_id:
            print("✅ 專案 ID 匹配!")
        else:
            print("❌ 專案 ID 不匹配!")
    except Exception as e:
        print(f"❌ 憑證解析錯誤: {e}")
else:
    print("❌ 未找到憑證")

# 測試 Vertex AI
print("\n🤖 測試 Vertex AI...")
try:
    import vertexai
    from google.oauth2 import service_account
    
    creds_dict = json.loads(credentials_json)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    
    vertexai.init(project=project_id, location="us-central1", credentials=credentials)
    print("✅ Vertex AI 初始化成功!")
    
except Exception as e:
    if "SERVICE_DISABLED" in str(e):
        print("⚠️ Vertex AI API 未啟用，需要手動啟用")
    else:
        print(f"❌ Vertex AI 錯誤: {e}")

print("\n完成測試!")