#!/usr/bin/env python3
"""
🎭 互動式 LINE Bot 劇本測試器
直接測試 LINE Bot 的對話功能
"""

import requests
import json
import hashlib
import hmac
import base64
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
    
    def send_text_message(self, message_text, reply_token=None):
        """發送文字訊息到 LINE Bot"""
        if not reply_token:
            reply_token = f"test_token_{int(datetime.now().timestamp())}"
        
        # 模擬 LINE Webhook 請求格式
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
            print(f"📤 發送: {message_text}")
            response = requests.post(
                f"{self.webhook_url}/callback",
                data=body,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ 成功: {response.status_code}")
                return True
            else:
                print(f"❌ 失敗: HTTP {response.status_code}")
                print(f"響應: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 錯誤: {e}")
            return False
    
    def send_audio_message(self, reply_token=None):
        """發送語音訊息到 LINE Bot"""
        if not reply_token:
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
                        "type": "audio",
                        "id": f"audio_{int(datetime.now().timestamp())}",
                        "duration": 5000
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
            print(f"🎤 發送語音訊息")
            response = requests.post(
                f"{self.webhook_url}/callback",
                data=body,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ 成功: {response.status_code}")
                return True
            else:
                print(f"❌ 失敗: HTTP {response.status_code}")
                print(f"響應: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 錯誤: {e}")
            return False

def run_conversation_scenarios(webhook_url):
    """執行所有對話場景"""
    
    tester = LineWebhookTester(webhook_url)
    
    scenarios = [
        {
            "name": "👋 初次見面",
            "messages": [
                "你好",
                "你是誰？",
                "你能做什麼？"
            ]
        },
        {
            "name": "👤 個人資訊記憶測試",
            "messages": [
                "我叫小明",
                "我是工程師",
                "你還記得我的名字嗎？"
            ]
        },
        {
            "name": "🗣️ 語音訊息測試",
            "messages": [
                {"type": "audio"},
                "什麼時候有語音功能？"
            ]
        },
        {
            "name": "🤖 AI 對話能力測試",
            "messages": [
                "今天天氣如何？",
                "告訴我一個笑話",
                "Python 怎麼寫 Hello World？"
            ]
        },
        {
            "name": "💭 記憶回憶測試",
            "messages": [
                "我們之前聊過什麼？",
                "我的工作是什麼？",
                "我心情不好"
            ]
        },
        {
            "name": "🔧 錯誤處理測試",
            "messages": [
                "!@#$%^&*()",
                "超級長的訊息" + "很長" * 50,
                ""
            ]
        }
    ]
    
    print("🎭 開始 LINE Bot 對話場景測試")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 場景 {i}: {scenario['name']}")
        print("-" * 40)
        
        for j, message in enumerate(scenario['messages'], 1):
            print(f"\n  測試 {i}.{j}:")
            
            if isinstance(message, dict) and message.get('type') == 'audio':
                success = tester.send_audio_message()
            else:
                success = tester.send_text_message(message)
            
            total_tests += 1
            if success:
                passed_tests += 1
            
            # 等待一下避免請求過快
            import time
            time.sleep(2)
    
    # 測試總結
    print("\n" + "=" * 60)
    print("📊 測試結果總結")
    print("=" * 60)
    print(f"總測試數: {total_tests}")
    print(f"成功數: {passed_tests}")
    print(f"成功率: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 所有測試通過！LINE Bot 功能正常")
    elif passed_tests > 0:
        print("⚠️ 部分測試通過，建議檢查失敗的測試")
    else:
        print("❌ 所有測試失敗，建議檢查設定和連接")

def test_basic_endpoints(base_url):
    """先測試基本端點"""
    print("🔍 測試基本端點...")
    
    endpoints = [
        ("/", "主頁"),
        ("/health", "健康檢查")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
                return True
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    return False

def main():
    """主測試流程"""
    print("🎭 LINE Bot 劇本測試器")
    print("=" * 60)
    
    # 嘗試不同的可能 URL
    possible_urls = [
        "https://lumi-line-bot-production.up.railway.app",
        "https://web-production-74e7.up.railway.app",
        input("💡 請輸入正確的 Railway URL (或按 Enter 使用預設): ").strip() or "https://lumi-line-bot-production.up.railway.app"
    ]
    
    working_url = None
    
    for url in possible_urls:
        print(f"\n🔍 測試 URL: {url}")
        if test_basic_endpoints(url):
            working_url = url
            print(f"✅ 找到可用的 URL: {url}")
            break
        else:
            print(f"❌ URL 不可用: {url}")
    
    if working_url:
        print(f"\n🚀 使用 URL: {working_url}")
        run_conversation_scenarios(working_url)
    else:
        print("\n⚠️ 無法找到可用的 URL")
        print("請檢查：")
        print("1. Railway 部署狀態")
        print("2. 正確的應用 URL")
        print("3. 網路連接")
        
        # 提供手動 URL 輸入選項
        manual_url = input("\n💡 如果你知道正確的 URL，請輸入: ").strip()
        if manual_url:
            print(f"\n🚀 使用手動輸入的 URL: {manual_url}")
            run_conversation_scenarios(manual_url)

if __name__ == "__main__":
    main()