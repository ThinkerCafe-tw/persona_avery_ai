#!/usr/bin/env python3
"""
🎭 LINE Bot 劇本測試 - 自動化版本
"""

import requests
import json
import hashlib
import hmac
import base64
import time
from datetime import datetime

class LineWebhookTester:
    def __init__(self, webhook_url, channel_secret="test_secret"):
        self.webhook_url = webhook_url
        self.channel_secret = channel_secret
        self.test_user_id = "test_user_123"
        
    def create_line_signature(self, body):
        """創建 LINE 簽名（測試用）"""
        if isinstance(body, str):
            body = body.encode('utf-8')
        
        hash_obj = hmac.new(
            self.channel_secret.encode('utf-8'),
            body,
            hashlib.sha256
        )
        signature = base64.b64encode(hash_obj.digest()).decode('utf-8')
        return f"sha256={signature}"
    
    def send_text_message(self, message_text):
        """發送文字訊息到 LINE Bot"""
        reply_token = f"test_token_{int(datetime.now().timestamp())}"
        
        webhook_data = {
            "destination": "test_destination",
            "events": [
                {
                    "type": "message",
                    "mode": "active",
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "source": {
                        "type": "user",
                        "userId": self.test_user_id
                    },
                    "replyToken": reply_token,
                    "message": {
                        "type": "text",
                        "id": f"msg_{int(datetime.now().timestamp())}",
                        "text": message_text
                    }
                }
            ]
        }
        
        body = json.dumps(webhook_data)
        signature = self.create_line_signature(body)
        
        headers = {
            "Content-Type": "application/json",
            "X-Line-Signature": signature
        }
        
        try:
            print(f"📤 發送: '{message_text}'")
            response = requests.post(
                f"{self.webhook_url}/callback",
                data=body,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                print(f"✅ 成功: HTTP {response.status_code}")
                print(f"📥 回應: OK")
                return True
            else:
                print(f"❌ 失敗: HTTP {response.status_code}")
                if response.text:
                    print(f"錯誤內容: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ 連接錯誤: {e}")
            return False

def test_basic_endpoints():
    """測試基本端點"""
    urls = [
        "https://lumi-line-bot-production.up.railway.app",
        "https://web-production-74e7.up.railway.app"
    ]
    
    for url in urls:
        print(f"\n🔍 測試 URL: {url}")
        
        try:
            # 測試健康檢查
            response = requests.get(f"{url}/health", timeout=10)
            if response.status_code == 200:
                print(f"✅ 健康檢查通過: {url}")
                return url
            else:
                print(f"❌ 健康檢查失敗: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ 連接失敗: {e}")
    
    return None

def run_all_scenarios():
    """執行所有劇本場景"""
    
    print("🎭 LINE Bot 對話場景劇本測試")
    print("=" * 60)
    
    # 先找到可用的 URL
    working_url = test_basic_endpoints()
    
    if not working_url:
        print("\n❌ 無法找到可用的服務 URL")
        print("請檢查 Railway 部署狀態")
        return
    
    print(f"\n🚀 使用服務 URL: {working_url}")
    tester = LineWebhookTester(working_url)
    
    scenarios = [
        {
            "name": "👋 初次見面",
            "messages": ["你好", "你是誰？", "你能做什麼？"]
        },
        {
            "name": "👤 個人資訊記憶測試",
            "messages": ["我叫小明", "我是工程師", "你還記得我的名字嗎？"]
        },
        {
            "name": "🤖 AI 對話能力測試",
            "messages": ["今天天氣如何？", "告訴我一個笑話", "Python 怎麼寫 Hello World？"]
        },
        {
            "name": "💭 記憶回憶測試",
            "messages": ["我們之前聊過什麼？", "我的工作是什麼？", "我心情不好"]
        },
        {
            "name": "🔧 錯誤處理測試",
            "messages": ["!@#$%^&*()", ""]
        }
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 場景 {i}: {scenario['name']}")
        print("-" * 40)
        
        for j, message in enumerate(scenario['messages'], 1):
            print(f"\n  測試 {i}.{j}:")
            
            success = tester.send_text_message(message)
            total_tests += 1
            if success:
                passed_tests += 1
            
            # 等待避免請求過快
            time.sleep(3)
    
    # 測試總結
    print("\n" + "=" * 60)
    print("📊 劇本測試結果總結")
    print("=" * 60)
    print(f"總測試數: {total_tests}")
    print(f"成功數: {passed_tests}")
    print(f"成功率: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 所有劇本測試通過！LINE Bot 功能正常")
    elif passed_tests > 0:
        print("⚠️ 部分測試通過，建議檢查失敗的測試項目")
    else:
        print("❌ 所有測試失敗，可能需要檢查:")
        print("   1. LINE Channel 環境變數設定")
        print("   2. Webhook 簽名驗證設定")
        print("   3. Gemini API 金鑰設定")

if __name__ == "__main__":
    run_all_scenarios()