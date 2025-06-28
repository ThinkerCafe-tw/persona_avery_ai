#!/usr/bin/env python3
"""
11Labs語音合成測試程式
測試露米的語音功能可行性
"""
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

class ElevenLabsTest:
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')  # 需要在.env添加
        self.base_url = "https://api.elevenlabs.io/v1"
        
        if not self.api_key:
            print("⚠️ 請在.env文件中添加 ELEVENLABS_API_KEY")
            print("格式: ELEVENLABS_API_KEY=your_api_key_here")
    
    def get_available_voices(self):
        """獲取可用的聲音列表"""
        url = f"{self.base_url}/voices"
        headers = {
            "Accept": "application/json",
            "xi-api-key": self.api_key
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                voices = response.json()['voices']
                print("🎤 可用的聲音:")
                for voice in voices:
                    print(f"   {voice['name']} (ID: {voice['voice_id']})")
                    print(f"   描述: {voice.get('description', 'N/A')}")
                    print()
                return voices
            else:
                print(f"❌ 獲取聲音列表失敗: {response.status_code}")
                print(response.text)
                return None
        except Exception as e:
            print(f"❌ API調用錯誤: {e}")
            return None
    
    def text_to_speech(self, text, voice_id, voice_name="Unknown"):
        """文字轉語音測試"""
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.7
            }
        }
        
        try:
            print(f"🎵 生成 {voice_name} 的語音...")
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                # 保存音頻文件
                filename = f"test_{voice_name.lower().replace(' ', '_')}.mp3"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ 語音文件已保存: {filename}")
                return filename
            else:
                print(f"❌ 語音生成失敗: {response.status_code}")
                print(response.text)
                return None
                
        except Exception as e:
            print(f"❌ 語音生成錯誤: {e}")
            return None
    
    def test_lumi_personas(self):
        """測試露米的人格聲音"""
        
        # 測試文案
        test_texts = {
            "healing": "我能感受到你內心的痛苦...這一定很不容易吧。這裡很安全，你可以慢慢說。我會一直陪著你。",
            "friend": "哎呀～別這樣想啦！你很可愛欸～我們一起想想解決辦法，好不好？放心，我會陪著你的！",
            "funny": "哈哈哈～你太好笑了吧！真的假的～我們來想個更有趣的解決方法吧！保證讓你開心起來！"
        }
        
        # 推薦的女性聲音ID（常見的高品質聲音）
        recommended_voices = [
            {"name": "Rachel", "id": "21m00Tcm4TlvDq8ikWAM"},
            {"name": "Domi", "id": "AZnzlk1XvdvUeBnXmlld"},
            {"name": "Bella", "id": "EXAVITQu4vr4xnSDxMaL"},
            {"name": "Elli", "id": "MF3mGyEYCl7XYWbV9V6O"}
        ]
        
        print("🎭 開始測試露米的人格聲音...")
        print("=" * 50)
        
        for persona, text in test_texts.items():
            print(f"\n🎪 測試 {persona.upper()} 模式:")
            print(f"文案: {text[:50]}...")
            
            for voice in recommended_voices:
                print(f"\n🎤 使用 {voice['name']} 聲音:")
                filename = self.text_to_speech(
                    text, 
                    voice['id'], 
                    f"{voice['name']}_{persona}"
                )
                if filename:
                    print(f"   📁 檔案: {filename}")
        
        print("\n🎉 測試完成！")
        print("請聽聽看音頻文件，選出最適合的聲音組合！")

def main():
    print("🤖 露米語音測試程式")
    print("=" * 30)
    
    tester = ElevenLabsTest()
    
    if not tester.api_key:
        return
    
    # 獲取可用聲音列表
    voices = tester.get_available_voices()
    
    if voices:
        print("\n" + "=" * 50)
        # 測試露米人格聲音
        tester.test_lumi_personas()
    
    print("\n💡 下一步:")
    print("1. 聽聽看生成的音頻文件")
    print("2. 選擇最適合露米的聲音")
    print("3. 測試LINE語音訊息整合")

if __name__ == "__main__":
    main()