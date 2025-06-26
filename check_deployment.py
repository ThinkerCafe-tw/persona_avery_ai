#!/usr/bin/env python3
"""
檢查Railway部署狀態和Vertex AI配置
"""
import requests
import json
from datetime import datetime

def check_railway_deployment():
    """檢查Railway部署狀態"""
    print("🚀 檢查Railway部署狀態...")
    
    urls = [
        "https://persona-avery-ai-production.up.railway.app/",
        "https://persona-avery-ai-production.up.railway.app/webhook"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"   {url}")
            print(f"   狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text[:100].strip()
                print(f"   內容: {content}...")
                return True
            else:
                print(f"   錯誤: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"   連線失敗: {e}")
    
    return False

def check_webhook_endpoint():
    """測試Webhook端點"""
    print("\n🔗 測試Webhook端點...")
    
    url = "https://persona-avery-ai-production.up.railway.app/webhook"
    
    # 模擬LINE Webhook請求（但不會有有效簽名）
    test_data = {
        "events": [{
            "type": "message",
            "message": {
                "type": "text",
                "text": "測試"
            },
            "source": {
                "userId": "test_user_id",
                "type": "user"
            },
            "timestamp": int(datetime.now().timestamp() * 1000),
            "replyToken": "test_reply_token"
        }]
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-Line-Signature': 'test_signature'  # 這會導致400錯誤，但能確認端點存在
    }
    
    try:
        response = requests.post(url, json=test_data, headers=headers, timeout=10)
        print(f"   狀態碼: {response.status_code}")
        
        if response.status_code == 400:
            print("   ✅ Webhook端點存在且正常響應（簽名驗證失敗是預期的）")
            return True
        else:
            print(f"   ⚠️ 意外狀態碼: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 連線失敗: {e}")
        return False

def check_environment_variables():
    """檢查部署中的環境變數設定（透過錯誤訊息推斷）"""
    print("\n🔍 推斷環境變數設定狀況...")
    
    # 這個無法直接檢查，但可以通過部署日誌或錯誤回應推斷
    print("   ℹ️ 無法直接檢查Railway環境變數")
    print("   💡 需要檢查Railway部署日誌中的以下訊息:")
    print("      - '✅ 企業級Vertex AI已初始化' = 成功")
    print("      - '⚠️ Vertex AI初始化失敗，使用備用API' = 失敗")
    print("      - 'Project ID: None' = VERTEX_AI_PROJECT_ID未設定")
    print("      - 'Credentials: 未設定' = GOOGLE_APPLICATION_CREDENTIALS_JSON未設定")
    
    return None

def main():
    """主要檢查流程"""
    print("=" * 60)
    print("🤖 Lumi 3.0 部署狀態檢查")
    print("=" * 60)
    
    # 檢查基本部署
    deployment_ok = check_railway_deployment()
    
    # 檢查Webhook
    webhook_ok = check_webhook_endpoint()
    
    # 環境變數提示
    check_environment_variables()
    
    print("\n" + "=" * 60)
    print("📊 檢查結果摘要")
    print("=" * 60)
    print(f"🚀 Railway部署: {'✅ 正常' if deployment_ok else '❌ 失敗'}")
    print(f"🔗 Webhook端點: {'✅ 正常' if webhook_ok else '❌ 失敗'}")
    print(f"🔐 環境變數: ❓ 需檢查部署日誌")
    
    if deployment_ok and webhook_ok:
        print("\n🎉 基本部署正常！")
        print("📝 接下來請檢查Railway部署日誌:")
        print("   1. 登入Railway控制台")
        print("   2. 點擊persona-avery-ai專案")
        print("   3. 查看Deploy logs")
        print("   4. 尋找Vertex AI初始化訊息")
        
        print("\n💡 如果看到'⚠️ Vertex AI初始化失敗':")
        print("   - 檢查VERTEX_AI_PROJECT_ID是否設為: probable-axon-451311-e1")
        print("   - 檢查VERTEX_AI_LOCATION是否設為: us-central1")  
        print("   - 確認GOOGLE_APPLICATION_CREDENTIALS_JSON包含完整的服務帳戶JSON")
        
    else:
        print("\n❌ 部署存在問題，需要重新部署")
        
    print("\n🔄 要觸發重新部署，請運行:")
    print("   git push origin master")

if __name__ == "__main__":
    main()