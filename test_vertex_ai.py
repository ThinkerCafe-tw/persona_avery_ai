#!/usr/bin/env python3
"""
測試Vertex AI企業級配額是否正確設置
"""
import os
from dotenv import load_dotenv
import json
import tempfile

load_dotenv()

def test_vertex_ai_setup():
    """測試Vertex AI設定"""
    print("🔍 測試Vertex AI企業級設定...")
    
    # 檢查環境變數
    vertex_project = os.getenv('VERTEX_AI_PROJECT_ID')
    vertex_location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
    vertex_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    
    print(f"   Project ID: {vertex_project}")
    print(f"   Location: {vertex_location}")
    print(f"   Credentials: {'已設定' if vertex_credentials else '未設定'}")
    
    if vertex_project and vertex_credentials:
        try:
            # 設定認證
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write(vertex_credentials)
                credentials_path = f.name
            
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            
            # 測試導入和初始化
            import vertexai
            from vertexai.preview.generative_models import GenerativeModel as VertexModel
            
            vertexai.init(
                project=vertex_project,
                location=vertex_location
            )
            
            model = VertexModel('gemini-1.5-flash')
            print("✅ Vertex AI初始化成功！")
            
            # 測試簡單對話
            test_prompt = "你好，請用一句話介紹自己"
            response = model.generate_content(test_prompt)
            print(f"✅ 測試回應: {response.text[:50]}...")
            
            # 清理臨時文件
            os.unlink(credentials_path)
            
            return True
            
        except Exception as e:
            print(f"❌ Vertex AI測試失敗: {e}")
            return False
    else:
        print("❌ 環境變數設定不完整")
        return False

def test_backup_gemini():
    """測試備用Gemini API"""
    print("\n🔄 測試備用Gemini API...")
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    print(f"   API Key: {'已設定' if gemini_key else '未設定'}")
    
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            test_prompt = "你好，請用一句話介紹自己"
            response = model.generate_content(test_prompt)
            print(f"✅ 備用API回應: {response.text[:50]}...")
            return True
            
        except Exception as e:
            print(f"❌ 備用API測試失敗: {e}")
            return False
    else:
        print("❌ Gemini API Key未設定")
        return False

if __name__ == "__main__":
    vertex_success = test_vertex_ai_setup()
    gemini_success = test_backup_gemini()
    
    print(f"\n📊 測試結果:")
    print(f"   Vertex AI (企業級): {'✅ 成功' if vertex_success else '❌ 失敗'}")
    print(f"   Gemini API (備用): {'✅ 成功' if gemini_success else '❌ 失敗'}")
    
    if vertex_success:
        print("\n🎉 企業級Vertex AI已準備就緒！")
        print("   配額應該從50/日提升到1000+/日")
    elif gemini_success:
        print("\n⚠️ 使用備用API模式")
        print("   仍受限於50/日配額")
    else:
        print("\n❌ 所有API都無法使用")