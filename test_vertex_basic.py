#!/usr/bin/env python3
"""
基本 Vertex AI 連接測試
"""
import os
import json
import tempfile
from dotenv import load_dotenv

load_dotenv()

def test_vertex_basic():
    """基本 Vertex AI 測試"""
    print("🔍 基本 Vertex AI 連接測試...")
    print("=" * 40)
    
    try:
        from google.cloud import aiplatform
        from google.oauth2 import service_account
        
        # 解析認證
        credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        credentials_dict = json.loads(credentials_json)
        project_id = credentials_dict.get('project_id')
        
        # 建立認證
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        
        # 初始化 AI Platform
        aiplatform.init(
            project=project_id,
            location="us-central1",
            credentials=credentials
        )
        
        print(f"✅ AI Platform 初始化成功")
        print(f"   專案: {project_id}")
        print(f"   位置: us-central1")
        
        # 嘗試列出可用模型
        try:
            from google.cloud.aiplatform import Model
            models = Model.list()
            print(f"✅ 可以存取模型列表 (找到 {len(list(models))} 個模型)")
            return True
        except Exception as e:
            print(f"⚠️ 模型列表存取: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 基本測試失敗: {e}")
        return False

if __name__ == "__main__":
    success = test_vertex_basic()
    if success:
        print("\n🎉 基本連接成功！")
        print("💡 可能需要啟用 Vertex AI Generative AI API")
    else:
        print("\n❌ 連接失敗")