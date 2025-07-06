#!/usr/bin/env python3
"""
簡單的啟動測試
"""
import os
import sys

def test_imports():
    """測試所有必要的模組是否能正常導入"""
    try:
        import flask
        print("✅ Flask 導入成功")
        
        from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
        print("✅ LINE Bot SDK v3 導入成功")
        
        import ai_logic
        print("✅ AI 邏輯模組導入成功")
        
        import simple_memory
        print("✅ 記憶系統模組導入成功")
        
        return True
    except Exception as e:
        print(f"❌ 導入失敗: {e}")
        return False

def test_line_bot_init():
    """測試 LINE Bot 初始化"""
    try:
        from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
        
        # 模擬初始化（不需要真實的 token）
        test_token = "test_token"
        configuration = Configuration(access_token=test_token)
        api_client = ApiClient(configuration)
        line_bot_api = MessagingApi(api_client)
        
        print("✅ LINE Bot SDK v3 初始化成功")
        return True
    except Exception as e:
        print(f"❌ LINE Bot 初始化失敗: {e}")
        return False

if __name__ == "__main__":
    print("=== 啟動測試開始 ===")
    
    if test_imports() and test_line_bot_init():
        print("✅ 所有測試通過，應用程式應該能正常啟動")
    else:
        print("❌ 測試失敗，請檢查錯誤")
    
    print("=== 啟動測試結束 ===") 