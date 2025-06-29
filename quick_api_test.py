import requests
import json

# 測試新的 11Labs API Key
api_key = "sk_744d84792233e9631afbc85874f8f4699a8631cc7932c9b1"

try:
    response = requests.get(
        "https://api.elevenlabs.io/v1/user",
        headers={"xi-api-key": api_key},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ 11Labs API Key 有效!")
        print(f"用戶: {data.get('email', 'Unknown')}")
        
        # 測試語音列表
        voices_response = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": api_key},
            timeout=10
        )
        
        if voices_response.status_code == 200:
            voices = voices_response.json()
            print(f"可用語音數量: {len(voices.get('voices', []))}")
            
            # 檢查是否有 Stacy 語音
            stacy_voice = None
            for voice in voices.get('voices', []):
                if voice.get('voice_id') == 'hkfHEbBvdQFNX4uWHqRF':
                    stacy_voice = voice
                    break
            
            if stacy_voice:
                print(f"✅ Stacy 語音可用: {stacy_voice.get('name')}")
            else:
                print("⚠️ 未找到 Stacy 語音 (ID: hkfHEbBvdQFNX4uWHqRF)")
        
    else:
        print(f"❌ API Key 測試失敗: {response.status_code}")
        print(f"回應: {response.text}")
        
except Exception as e:
    print(f"❌ 連接錯誤: {e}")