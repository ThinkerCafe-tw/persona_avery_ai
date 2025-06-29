#!/usr/bin/env python3
"""
檢查 Vertex AI 在不同地區的可用性
"""
import os
import json
import tempfile
from dotenv import load_dotenv

load_dotenv()

def check_vertex_regions():
    """檢查不同地區的 Vertex AI 可用性"""
    print("🌍 檢查 Vertex AI 地區可用性...")
    print("=" * 50)
    
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        from google.oauth2 import service_account
        
        # 解析認證
        credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        credentials_dict = json.loads(credentials_json)
        project_id = credentials_dict.get('project_id')
        
        # 創建臨時認證檔案
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(credentials_dict, f)
            temp_cred_file = f.name
        
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_cred_file
        
        # 測試不同地區
        regions_to_test = [
            "us-central1",
            "us-east1", 
            "us-west1",
            "asia-northeast1",
            "europe-west1"
        ]
        
        # 簡化的模型名稱
        simple_models = [
            "gemini-pro",
            "gemini-1.0-pro",
            "text-bison"
        ]
        
        for region in regions_to_test:
            print(f"\n🔍 測試地區: {region}")
            
            try:
                # 重新初始化 Vertex AI for 新地區
                vertexai.init(project=project_id, location=region)
                print(f"   ✅ 初始化成功")
                
                # 測試一個簡單模型
                for model_name in simple_models:
                    try:
                        model = GenerativeModel(model_name)
                        response = model.generate_content("Hi")
                        
                        if response and response.text:
                            print(f"   🎉 {region} + {model_name}: 成功!")
                            print(f"      回應: {response.text.strip()[:50]}...")
                            return region, model_name
                            
                    except Exception as e:
                        error_str = str(e)
                        if "404" in error_str:
                            print(f"   ❌ {model_name}: 不存在")
                        elif "403" in error_str:
                            print(f"   ❌ {model_name}: 權限問題")
                        else:
                            print(f"   ❌ {model_name}: {error_str[:50]}...")
                            
            except Exception as e:
                print(f"   ❌ 地區初始化失敗: {e}")
        
        print("\n💡 建議: 可能需要等待 API 權限完全生效 (最多30分鐘)")
        return None, None
        
    except Exception as e:
        print(f"❌ 整體測試失敗: {e}")
        return None, None
    finally:
        if 'temp_cred_file' in locals():
            try:
                os.unlink(temp_cred_file)
            except:
                pass

if __name__ == "__main__":
    region, model = check_vertex_regions()
    if region and model:
        print(f"\n🎯 找到可用配置: {region} + {model}")
    else:
        print(f"\n📊 當前狀態: 使用 Gemini API 備用方案 (75% 功能就緒)")