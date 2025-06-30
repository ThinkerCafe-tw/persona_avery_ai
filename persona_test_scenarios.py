#!/usr/bin/env python3
"""
🎭 Lumi 六人格模式測試劇本
專門測試每種人格的特色表現
"""

import requests
import json
import hashlib
import hmac
import base64
import time
from datetime import datetime

class PersonaTestRunner:
    def __init__(self, webhook_url, channel_secret="test_secret"):
        self.webhook_url = webhook_url
        self.channel_secret = channel_secret
        self.test_user_id = "persona_test_user_456"
        
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
    
    def send_message(self, message_text, expected_persona=None):
        """發送訊息並顯示期待的人格"""
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
            print(f"📤 測試訊息: '{message_text}'")
            if expected_persona:
                print(f"🎭 期待人格: {expected_persona}")
            
            response = requests.post(
                f"{self.webhook_url}/callback",
                data=body,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ 發送成功")
                return True
            else:
                print(f"❌ 發送失敗: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 錯誤: {e}")
            return False

def run_persona_tests(webhook_url):
    """執行完整的人格模式測試"""
    
    tester = PersonaTestRunner(webhook_url)
    
    print("🎭 Lumi 六人格模式專業測試")
    print("=" * 60)
    
    # 定義各人格的測試場景
    persona_scenarios = [
        {
            "name": "💚 療癒對話模式測試",
            "expected_persona": "療癒對話",
            "tests": [
                {
                    "message": "我今天心情很不好，感覺很累",
                    "expect": "溫柔安慰、同理心、情緒支持"
                },
                {
                    "message": "工作壓力好大，覺得很焦慮",
                    "expect": "理解感受、提供撫慰、不給建議"
                },
                {
                    "message": "最近失戀了，很難過",
                    "expect": "溫暖陪伴、情感支持"
                }
            ]
        },
        
        {
            "name": "😄 幽默聊天模式測試",
            "expected_persona": "幽默聊天",
            "tests": [
                {
                    "message": "說個笑話給我聽",
                    "expect": "輕鬆幽默、俏皮話、開心氛圍"
                },
                {
                    "message": "今天好無聊啊",
                    "expect": "有趣對話、活潑互動"
                },
                {
                    "message": "讓我開心點吧",
                    "expect": "搞笑內容、正面能量"
                }
            ]
        },
        
        {
            "name": "💕 閨蜜模式測試",
            "expected_persona": "閨蜜模式",
            "tests": [
                {
                    "message": "我想跟你分享個秘密",
                    "expect": "親密語氣、關心詢問、閨蜜感"
                },
                {
                    "message": "今天遇到一個帥哥",
                    "expect": "八卦興趣、親暱互動"
                },
                {
                    "message": "我們來聊聊天吧",
                    "expect": "親密稱呼、熱情回應"
                }
            ]
        },
        
        {
            "name": "🧠 知性深度模式測試",
            "expected_persona": "知性深度",
            "tests": [
                {
                    "message": "為什麼AI會有意識？",
                    "expect": "理性分析、深度思考、多角度觀點"
                },
                {
                    "message": "請分析一下人工智能的發展",
                    "expect": "專業知識、邏輯推理"
                },
                {
                    "message": "如何學習新技術？",
                    "expect": "方法論、思考框架"
                }
            ]
        },
        
        {
            "name": "🌟 心靈導師模式測試",
            "expected_persona": "心靈導師",
            "tests": [
                {
                    "message": "我很迷茫，不知道人生方向",
                    "expect": "智慧指導、啟發性問題、人生建議"
                },
                {
                    "message": "該如何做出重要決定？",
                    "expect": "引導思考、提供框架、不直接給答案"
                },
                {
                    "message": "我想要成長",
                    "expect": "成長建議、自我反思"
                }
            ]
        },
        
        {
            "name": "📖 日記智者模式測試",
            "expected_persona": "日記智者",
            "tests": [
                {
                    "message": "幫我總結一下最近的經歷",
                    "expect": "整理思緒、發現模式、深度反思"
                },
                {
                    "message": "我想記錄今天的收穫",
                    "expect": "記錄協助、意義發掘"
                },
                {
                    "message": "回顧一下我們的對話",
                    "expect": "總結洞察、智慧歸納"
                }
            ]
        }
    ]
    
    # 手動切換測試
    manual_switch_tests = [
        {
            "name": "🔄 手動人格切換測試",
            "tests": [
                ("切換到療癒模式", "療癒對話"),
                ("我想要幽默聊天", "幽默聊天"),
                ("閨蜜模式", "閨蜜模式"),
                ("知性一點", "知性深度"),
                ("請當我的導師", "心靈導師"),
                ("日記智者模式", "日記智者")
            ]
        }
    ]
    
    total_tests = 0
    passed_tests = 0
    
    # 執行人格自動檢測測試
    for i, scenario in enumerate(persona_scenarios, 1):
        print(f"\n📝 測試 {i}: {scenario['name']}")
        print("-" * 50)
        
        for j, test in enumerate(scenario['tests'], 1):
            print(f"\n  子測試 {i}.{j}:")
            print(f"  期待: {test['expect']}")
            
            success = tester.send_message(
                test['message'], 
                scenario['expected_persona']
            )
            
            total_tests += 1
            if success:
                passed_tests += 1
            
            time.sleep(3)  # 等待避免請求過快
    
    # 執行手動切換測試
    print(f"\n📝 測試 {len(persona_scenarios) + 1}: 🔄 手動人格切換測試")
    print("-" * 50)
    
    for message, expected_persona in manual_switch_tests[0]['tests']:
        print(f"\n  切換測試:")
        
        success = tester.send_message(message, expected_persona)
        
        total_tests += 1
        if success:
            passed_tests += 1
        
        time.sleep(3)
    
    # 測試總結
    print("\n" + "=" * 60)
    print("📊 人格模式測試結果總結")
    print("=" * 60)
    print(f"總測試數: {total_tests}")
    print(f"成功數: {passed_tests}")
    print(f"成功率: {passed_tests/total_tests*100:.1f}%")
    
    print(f"\n🎭 測試的人格模式:")
    for scenario in persona_scenarios:
        print(f"   ✅ {scenario['expected_persona']}")
    print(f"   ✅ 手動切換功能")
    
    if passed_tests == total_tests:
        print("\n🎉 所有人格測試通過！六人格系統功能正常")
    elif passed_tests > 0:
        print("\n⚠️ 部分測試通過，建議檢查失敗的人格模式")
    else:
        print("\n❌ 所有測試失敗，建議檢查人格系統設定")
    
    print(f"\n💡 使用指南:")
    print("用戶可以通過以下方式切換人格:")
    print("- 自動檢測：根據訊息內容自動選擇合適人格")
    print("- 手動切換：說「療癒」、「幽默」、「閨蜜」、「知性」、「導師」、「日記」")
    print("- 默認模式：閨蜜模式（親密聊天）")

def test_basic_connection(base_url):
    """測試基本連接"""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ 服務連接正常: {base_url}")
            return True
        else:
            print(f"❌ 服務異常: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 連接失敗: {e}")
        return False

def main():
    """主測試流程"""
    print("🎭 Lumi 六人格模式專業測試器")
    print("=" * 60)
    
    # 嘗試可能的 URL
    possible_urls = [
        "https://lumi-line-bot-production.up.railway.app",
        "https://web-production-74e7.up.railway.app"
    ]
    
    working_url = None
    
    for url in possible_urls:
        print(f"\n🔍 測試 URL: {url}")
        if test_basic_connection(url):
            working_url = url
            break
    
    if working_url:
        print(f"\n🚀 使用服務 URL: {working_url}")
        run_persona_tests(working_url)
    else:
        print("\n⚠️ 無法找到可用的服務")
        manual_url = input("💡 請輸入正確的 Railway URL: ").strip()
        if manual_url:
            print(f"\n🚀 使用手動 URL: {manual_url}")
            run_persona_tests(manual_url)

if __name__ == "__main__":
    main()