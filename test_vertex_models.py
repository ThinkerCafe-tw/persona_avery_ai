#!/usr/bin/env python3
"""
測試 Vertex AI 可用模型
"""
import os
import json
import tempfile
from dotenv import load_dotenv

load_dotenv()

def test_vertex_models():
    """測試不同的 Vertex AI 模型"""
    print("🧪 測試 Vertex AI 可用模型...")
    print("=" * 50)
    
    # 設定認證
    credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if not credentials_json:
        print("❌ 未找到認證")
        return
    
    try:
        from vertexai.generative_models import GenerativeModel
        import vertexai
        
        # 解析認證
        credentials_dict = json.loads(credentials_json)
        project_id = credentials_dict.get('project_id')
        
        # 創建臨時認證檔案
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(credentials_dict, f)
            temp_cred_file = f.name
        
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_cred_file
        
        # 初始化 Vertex AI
        vertexai.init(project=project_id, location="us-central1")
        print(f"✅ Vertex AI 已初始化 (專案: {project_id})")
        
        # 測試不同模型
        models_to_test = [
            "gemini-1.5-flash-001",
            "gemini-1.5-pro-001", 
            "gemini-pro",
            "gemini-pro-vision"
        ]
        
        for model_name in models_to_test:
            try:
                print(f"\n🔍 測試模型: {model_name}")
                model = GenerativeModel(model_name)
                
                # 簡單測試
                response = model.generate_content("你好，請回應一個字：好")
                
                if response and response.text:
                    print(f"✅ {model_name}: {response.text.strip()}")
                    return model_name  # 返回第一個成功的模型
                else:
                    print(f"❌ {model_name}: 無回應")
                    
            except Exception as e:
                print(f"❌ {model_name}: {str(e)[:100]}...")
        
        print("\n⚠️ 所有模型測試失敗")
        return None
        
    except Exception as e:
        print(f"❌ Vertex AI 測試失敗: {e}")
        return None
    finally:
        # 清理臨時檔案
        if 'temp_cred_file' in locals():
            try:
                os.unlink(temp_cred_file)
            except:
                pass

if __name__ == "__main__":
    working_model = test_vertex_models()
    if working_model:
        print(f"\n🎉 找到可用模型: {working_model}")
    else:
        print("\n💡 建議檢查專案是否已啟用 Vertex AI Generative AI API")