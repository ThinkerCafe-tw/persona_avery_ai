#!/usr/bin/env python3
"""
用最新 API 測試 Vertex AI
"""
import os
import json
import tempfile
from dotenv import load_dotenv

load_dotenv()

def test_vertex_new_api():
    """用最新 API 測試 Vertex AI"""
    print("🧪 用最新 API 測試 Vertex AI...")
    print("=" * 50)
    
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        from google.oauth2 import service_account
        
        # 解析認證
        credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        credentials_dict = json.loads(credentials_json)
        project_id = credentials_dict.get('project_id')
        
        # 建立認證
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        
        # 創建臨時認證檔案
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(credentials_dict, f)
            temp_cred_file = f.name
        
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_cred_file
        
        print(f"✅ 認證設定完成")
        
        # 初始化 Vertex AI
        vertexai.init(project=project_id, location="us-central1")
        print(f"✅ Vertex AI 已初始化 (專案: {project_id})")
        
        # 測試不同模型名稱
        models_to_test = [
            "gemini-1.5-pro",
            "gemini-1.5-flash", 
            "gemini-pro",
            "gemini-1.0-pro"
        ]
        
        success_count = 0
        
        for model_name in models_to_test:
            try:
                print(f"\n🔍 測試模型: {model_name}")
                model = GenerativeModel(model_name)
                
                # 簡單測試
                response = model.generate_content("你好，請回應'測試成功'")
                
                if response and response.text:
                    print(f"✅ {model_name}: {response.text.strip()}")
                    success_count += 1
                    
                    # 第一個成功就夠了
                    print(f"\n🎉 找到可用模型: {model_name}")
                    return model_name
                    
            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg:
                    print(f"❌ {model_name}: 模型不存在")
                elif "403" in error_msg:
                    print(f"❌ {model_name}: 權限不足")
                else:
                    print(f"❌ {model_name}: {error_msg[:100]}...")
        
        if success_count == 0:
            print("\n⚠️ 所有模型測試失敗")
            print("💡 可能需要啟用額外的 API 或等待權限生效")
        
        return None
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return None
    finally:
        # 清理臨時檔案
        if 'temp_cred_file' in locals():
            try:
                os.unlink(temp_cred_file)
            except:
                pass

if __name__ == "__main__":
    working_model = test_vertex_new_api()
    if working_model:
        print(f"\n🎉 Vertex AI 企業級功能已就緒！")
        print(f"   可用模型: {working_model}")
    else:
        print("\n💡 系統仍可用 Gemini API 作為備用方案")