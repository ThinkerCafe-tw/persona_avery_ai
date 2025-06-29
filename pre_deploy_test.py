#!/usr/bin/env python3
"""
🧪 部署前完整測試套件
確保系統在部署前所有組件都正常工作
"""

import os
import sys
import traceback
from datetime import datetime

def test_imports():
    """測試所有關鍵模組導入"""
    print("🔍 測試模組導入...")
    
    try:
        # 測試 Flask 相關
        from flask import Flask
        print("✅ Flask 導入成功")
        
        # 測試 LINE Bot SDK
        from linebot.v3 import WebhookHandler
        from linebot.v3.messaging import MessagingApi
        print("✅ LINE Bot SDK 導入成功")
        
        # 測試 Gemini AI
        import google.generativeai as genai
        print("✅ Google Generative AI 導入成功")
        
        # 測試記憶系統
        from simple_memory import SimpleLumiMemory
        print("✅ 記憶系統導入成功")
        
        # 測試 pgvector 依賴（可選）
        try:
            import psycopg2
            from psycopg2.pool import SimpleConnectionPool
            print("✅ pgvector 依賴可用")
        except ImportError:
            print("⚠️ pgvector 依賴不可用（會降級到內存模式）")
        
        return True
    except Exception as e:
        print(f"❌ 模組導入失敗: {e}")
        return False

def test_environment_variables():
    """測試環境變數配置"""
    print("\n🔍 測試環境變數...")
    
    required_vars = [
        'LINE_CHANNEL_ACCESS_TOKEN',
        'LINE_CHANNEL_SECRET', 
        'GEMINI_API_KEY'
    ]
    
    optional_vars = [
        'DATABASE_URL',
        'PORT'
    ]
    
    all_good = True
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} 已設定")
        else:
            print(f"❌ {var} 未設定（必需）")
            all_good = False
    
    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ {var} 已設定")
        else:
            print(f"⚠️ {var} 未設定（可選）")
    
    return all_good

def test_memory_system():
    """測試記憶系統功能"""
    print("\n🔍 測試記憶系統...")
    
    try:
        from simple_memory import SimpleLumiMemory
        
        # 初始化記憶系統
        memory = SimpleLumiMemory()
        print("✅ 記憶系統初始化成功")
        
        # 測試連接
        if memory.test_connection():
            print("✅ 記憶系統連接測試通過")
        else:
            print("❌ 記憶系統連接測試失敗")
            return False
        
        # 測試基本功能
        test_user_id = "test_deploy_user"
        
        # 測試添加對話
        memory.add_interaction(
            test_user_id, 
            "我叫測試用戶", 
            "你好測試用戶！", 
            "friend"
        )
        print("✅ 對話記錄功能正常")
        
        # 測試獲取用戶資訊
        user_info = memory.get_user_info(test_user_id)
        if user_info.get('name') == '測試用戶':
            print("✅ 用戶資訊提取功能正常")
        else:
            print("⚠️ 用戶資訊提取可能有問題")
        
        # 測試獲取記憶
        recent_memories = memory.get_recent_memories(test_user_id)
        if len(recent_memories) > 0:
            print("✅ 記憶檢索功能正常")
        else:
            print("❌ 記憶檢索功能異常")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 記憶系統測試失敗: {e}")
        traceback.print_exc()
        return False

def test_gemini_api():
    """測試 Gemini API 連接"""
    print("\n🔍 測試 Gemini AI...")
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY 未設定")
            return False
        
        # 配置 API
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini API 配置成功")
        
        # 測試簡單請求
        try:
            response = model.generate_content("Hello, this is a test. Please respond with 'Test successful'.")
            if response and response.text:
                print(f"✅ Gemini API 回應測試成功: {response.text[:50]}...")
                return True
            else:
                print("❌ Gemini API 回應為空")
                return False
        except Exception as e:
            print(f"❌ Gemini API 請求失敗: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Gemini AI 測試失敗: {e}")
        return False

def test_flask_app():
    """測試 Flask 應用基本功能"""
    print("\n🔍 測試 Flask 應用...")
    
    try:
        # 動態導入主應用
        sys.path.insert(0, '.')
        from main import app
        
        with app.test_client() as client:
            # 測試健康檢查端點
            response = client.get('/')
            if response.status_code == 200:
                print("✅ 主頁端點正常")
            else:
                print(f"❌ 主頁端點異常: {response.status_code}")
                return False
            
            # 測試健康檢查端點
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ 健康檢查端點正常")
            else:
                print(f"❌ 健康檢查端點異常: {response.status_code}")
                return False
        
        print("✅ Flask 應用基本功能正常")
        return True
        
    except Exception as e:
        print(f"❌ Flask 應用測試失敗: {e}")
        traceback.print_exc()
        return False

def test_dependencies():
    """測試 requirements.txt 中的依賴"""
    print("\n🔍 測試關鍵依賴版本...")
    
    try:
        # 測試版本相容性
        import flask
        print(f"✅ Flask: {flask.__version__}")
        
        import google.generativeai
        print("✅ Google Generative AI 可用")
        
        try:
            import psycopg2
            print(f"✅ psycopg2: {psycopg2.__version__}")
        except ImportError:
            print("⚠️ psycopg2 不可用（會使用內存模式）")
        
        import requests
        print(f"✅ requests: {requests.__version__}")
        
        return True
        
    except Exception as e:
        print(f"❌ 依賴測試失敗: {e}")
        return False

def run_all_tests():
    """執行所有測試"""
    print("🚀 開始部署前測試...")
    print("=" * 50)
    
    tests = [
        ("模組導入", test_imports),
        ("環境變數", test_environment_variables),
        ("依賴版本", test_dependencies),
        ("記憶系統", test_memory_system),
        ("Gemini AI", test_gemini_api),
        ("Flask 應用", test_flask_app),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} 測試發生異常: {e}")
            results[test_name] = False
    
    # 總結報告
    print("\n" + "=" * 50)
    print("📊 測試結果總結:")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 通過率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有測試通過！可以安全部署")
        return True
    else:
        print("⚠️ 部分測試失敗，建議修復後再部署")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)