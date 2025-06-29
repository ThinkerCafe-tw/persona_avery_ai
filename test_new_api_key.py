#!/usr/bin/env python3
"""
🔑 測試新的 11Labs API Key
"""

import requests

def test_elevenlabs_api(api_key):
    """測試 11Labs API Key"""
    try:
        headers = {
            "Accept": "application/json",
            "xi-api-key": api_key
        }
        
        response = requests.get("https://api.elevenlabs.io/v1/user", headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ 11Labs API Key 有效!")
            print(f"   用戶: {user_data.get('email', 'Unknown')}")
            print(f"   角色數量: {len(user_data.get('available_voices', []))}")
            return True
        elif response.status_code == 401:
            print(f"❌ 11Labs API Key 無效或權限不足")
            return False
        else:
            print(f"❌ 11Labs API 錯誤: {response.status_code}")
            print(f"   回應: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API 連接錯誤: {e}")
        return False

def main():
    new_api_key = "sk_744d84792233e9631afbc85874f8f4699a8631cc7932c9b1"
    
    print("🔑 測試新的 11Labs API Key...")
    print("=" * 50)
    
    success = test_elevenlabs_api(new_api_key)
    
    if success:
        print("\n🎉 API Key 測試成功！")
        print("💡 下一步：更新 Railway 環境變數")
        print(f"   ELEVENLABS_API_KEY = {new_api_key}")
    else:
        print("\n⚠️ API Key 有問題，請檢查")

if __name__ == "__main__":
    main()