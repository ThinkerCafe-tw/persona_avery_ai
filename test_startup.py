#!/usr/bin/env python3
"""
測試應用程式啟動
"""
import os
import sys
import time
import requests
from threading import Thread

def test_app_startup():
    """測試應用程式啟動"""
    print("=== 測試應用程式啟動 ===")
    
    # 檢查環境變數
    print(f"PORT: {os.getenv('PORT', '8080')}")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')[:50]}...")
    print(f"LINE_CHANNEL_SECRET: {'Set' if os.getenv('LINE_CHANNEL_SECRET') else 'Not set'}")
    print(f"LINE_CHANNEL_ACCESS_TOKEN: {'Set' if os.getenv('LINE_CHANNEL_ACCESS_TOKEN') else 'Not set'}")
    
    # 嘗試導入模組
    try:
        import app
        print("✅ app.py 導入成功")
    except Exception as e:
        print(f"❌ app.py 導入失敗: {e}")
        return False
    
    # 檢查 Flask app
    if hasattr(app, 'app'):
        print("✅ Flask app 存在")
    else:
        print("❌ Flask app 不存在")
        return False
    
    return True

def test_health_endpoint():
    """測試健康檢查端點"""
    print("\n=== 測試健康檢查端點 ===")
    
    port = os.getenv('PORT', '8080')
    url = f"http://localhost:{port}/health"
    
    print(f"測試 URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"✅ 健康檢查成功: {response.status_code} - {response.text}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到應用程式")
        return False
    except Exception as e:
        print(f"❌ 健康檢查失敗: {e}")
        return False

if __name__ == "__main__":
    print("開始測試...")
    
    if test_app_startup():
        print("✅ 應用程式啟動測試通過")
        
        # 等待一下讓應用程式完全啟動
        print("等待 5 秒...")
        time.sleep(5)
        
        if test_health_endpoint():
            print("✅ 健康檢查測試通過")
            sys.exit(0)
        else:
            print("❌ 健康檢查測試失敗")
            sys.exit(1)
    else:
        print("❌ 應用程式啟動測試失敗")
        sys.exit(1) 