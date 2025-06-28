#!/usr/bin/env python3
"""
露米語音整合測試
測試11Labs中文語音 + LINE Bot語音訊息
"""
import os
import requests
import tempfile
from dotenv import load_dotenv

load_dotenv()

class LumiVoiceTest:
    def __init__(self):
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # Stacy - Sweet and Cute Chinese 女聲
        self.chinese_voice_id = "pqHfZKP75CvOlQylNhV4"  # Stacy的voice_id
        
    def generate_lumi_voice(self, text, persona_type="friend"):
        """為露米生成語音，根據人格調整參數"""
        
        # 針對Stacy (Sweet & Cute) 優化的語音參數
        voice_settings = {
            "healing": {
                "stability": 0.8,  # 提高穩定性，減少可愛感
                "similarity_boost": 0.9,  # 保持聲音清晰
                "style": 0.2  # 降低風格化，更自然溫柔
            },
            "friend": {
                "stability": 0.5,  # 適度活潑
                "similarity_boost": 0.7,  # 保持Stacy特色
                "style": 0.6  # 發揮Sweet & Cute特質
            },
            "funny": {
                "stability": 0.3,  # 更活潑多變
                "similarity_boost": 0.8,  # 保持清晰
                "style": 0.8  # 充分發揮俏皮可愛
            },
            "knowledge": {
                "stability": 0.7,  # 穩重一些
                "similarity_boost": 0.8,  # 清晰表達
                "style": 0.3  # 降低可愛感，增加專業感
            },
            "wisdom": {
                "stability": 0.9,  # 最穩定
                "similarity_boost": 0.9,  # 最清晰
                "style": 0.1  # 最低風格化，追求深沉感
            },
            "soul": {
                "stability": 0.6,  # 適中
                "similarity_boost": 0.8,  # 清晰
                "style": 0.4  # 溫柔感性
            }
        }
        
        settings = voice_settings.get(persona_type, voice_settings["friend"])
        
        url = f"{self.base_url}/text-to-speech/{self.chinese_voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": settings
        }
        
        try:
            print(f"🎤 生成 {persona_type} 模式語音: {text[:30]}...")
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                # 創建臨時音頻文件
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                    temp_file.write(response.content)
                    temp_file.flush()
                    
                    print(f"✅ 語音文件已生成: {temp_file.name}")
                    return temp_file.name
            else:
                print(f"❌ 語音生成失敗: {response.status_code}")
                print(response.text)
                return None
                
        except Exception as e:
            print(f"❌ 語音生成錯誤: {e}")
            return None
    
    def test_lumi_personas_chinese(self):
        """測試露米各人格的中文語音"""
        
        test_cases = [
            {
                "persona": "healing",
                "text": "我能感受到你內心的痛苦。這一定很不容易吧？這裡很安全，你可以慢慢說。我是Lumi，會陪著你的。"
            },
            {
                "persona": "friend", 
                "text": "哎呀～別這樣想啦！你很可愛欸～我們一起想想解決辦法，好不好？我是Lumi唷！"
            },
            {
                "persona": "funny",
                "text": "哈哈哈～你太好笑了吧！真的假的～我們來想個更有趣的方法！Lumi來幫你想想～"
            },
            {
                "persona": "knowledge",
                "text": "我來跟你說說這個問題。有個有趣的解決方法，你知道嗎？試試看吧！我是Lumi。"
            },
            {
                "persona": "wisdom",
                "text": "生活就像一條河流，有時平靜，有時湍急。也許這就是成長的意義。Lumi與你同行。"
            },
            {
                "persona": "soul",
                "text": "嗯...這個話題很有深度。我懂你想探索的感覺。我們可以一起好起來。我是Lumi。"
            }
        ]
        
        print("🎭 開始測試露米中文語音人格...")
        print("=" * 50)
        
        results = []
        
        for case in test_cases:
            persona = case["persona"]
            text = case["text"]
            
            print(f"\n🎪 測試 {persona.upper()} 模式:")
            print(f"📝 文案: {text}")
            
            audio_file = self.generate_lumi_voice(text, persona)
            
            if audio_file:
                results.append({
                    "persona": persona,
                    "text": text,
                    "audio_file": audio_file,
                    "success": True
                })
                print(f"🎵 音頻: {audio_file}")
            else:
                results.append({
                    "persona": persona,
                    "text": text,
                    "audio_file": None,
                    "success": False
                })
        
        print("\n" + "=" * 50)
        print("🎉 測試完成！")
        print(f"✅ 成功: {sum(1 for r in results if r['success'])}/{len(results)}")
        
        return results
    
    def test_pronunciation_fixes(self):
        """測試發音問題的修復方法"""
        
        print("🔧 測試發音修復技巧...")
        
        # 原始文案 vs 修復文案
        test_pairs = [
            {
                "original": "我會陪伴你進行心理療癒",
                "fixed": "我會陪伴你，進行心理治療"
            },
            {
                "original": "這個感受很複雜",
                "fixed": "這個感受...很複雜"
            },
            {
                "original": "你的想法很重要",
                "fixed": "你的想法，很重要！"
            }
        ]
        
        for pair in test_pairs:
            print(f"\n📝 原始: {pair['original']}")
            print(f"🔧 修復: {pair['fixed']}")
            
            # 生成兩個版本比較
            original_audio = self.generate_lumi_voice(pair['original'], "healing")
            fixed_audio = self.generate_lumi_voice(pair['fixed'], "healing")
            
            if original_audio and fixed_audio:
                print(f"🎵 原始音頻: {original_audio}")
                print(f"🎵 修復音頻: {fixed_audio}")

def main():
    print("🤖 露米語音整合測試")
    print("=" * 30)
    
    tester = LumiVoiceTest()
    
    if not tester.elevenlabs_api_key:
        print("⚠️ 請設定 ELEVENLABS_API_KEY")
        return
    
    if tester.chinese_voice_id == "YOUR_CHINESE_VOICE_ID":
        print("⚠️ 請更新 chinese_voice_id 為你找到的中文女聲ID")
        return
    
    # 測試露米人格語音
    results = tester.test_lumi_personas_chinese()
    
    print("\n" + "=" * 50)
    print("🔧 測試發音修復...")
    tester.test_pronunciation_fixes()
    
    print("\n💡 下一步:")
    print("1. 聽聽看生成的音頻文件")
    print("2. 找出發音問題的規律")
    print("3. 調整文案或使用SSML標記")
    print("4. 整合到LINE Bot系統")

if __name__ == "__main__":
    main()