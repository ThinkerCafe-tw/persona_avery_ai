#!/usr/bin/env python3
"""
模擬真人用戶進行語音功能完整測試
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import voice_system, get_lumi_response, user_voice_preferences, analyze_emotion
import time

class VoiceUserSimulator:
    def __init__(self):
        self.test_user_id = "simulation_user_001"
        self.conversation_log = []
        
    def simulate_user_message(self, message, expect_voice=False):
        """模擬用戶發送訊息"""
        print(f"👤 用戶說: {message}")
        
        # 模擬Lumi的完整處理流程
        persona_type = analyze_emotion(message, self.test_user_id)
        lumi_response = get_lumi_response(message, self.test_user_id)
        
        print(f"🤖 Lumi回應: {lumi_response}")
        print(f"🎭 偵測人格: {persona_type}")
        
        # 檢查語音偏好
        user_wants_voice = user_voice_preferences.get(self.test_user_id, False)
        print(f"🔊 語音狀態: {'已開啟' if user_wants_voice else '已關閉'}")
        
        # 如果期望有語音，測試語音生成
        if expect_voice and user_wants_voice and voice_system and voice_system.enabled:
            print("🎤 測試語音生成...")
            audio_content = voice_system.generate_lumi_voice(lumi_response, persona_type)
            
            if audio_content:
                print(f"✅ 語音生成成功 ({len(audio_content)} bytes)")
                
                # 測試音頻上傳
                audio_url = voice_system.upload_audio_to_temp_host(audio_content)
                if audio_url:
                    print(f"🌐 語音URL: {audio_url}")
                    return True, audio_url
                else:
                    print("❌ 音頻上傳失敗")
                    return False, None
            else:
                print("❌ 語音生成失敗")
                return False, None
        
        print("-" * 50)
        return True, None
    
    def run_complete_voice_test(self):
        """運行完整的語音功能測試"""
        print("🎭 模擬真人用戶語音功能測試")
        print("=" * 60)
        
        test_scenarios = [
            {
                "message": "開啟語音",
                "expect_voice": False,
                "description": "開啟語音功能"
            },
            {
                "message": "你好嗎？",
                "expect_voice": True,
                "description": "基本對話測試"
            },
            {
                "message": "我今天心情很不好",
                "expect_voice": True,
                "description": "療癒模式語音測試"
            },
            {
                "message": "哈哈哈太好笑了",
                "expect_voice": True,
                "description": "搞笑模式語音測試"
            },
            {
                "message": "生活的意義是什麼？",
                "expect_voice": True,
                "description": "智慧模式語音測試"
            },
            {
                "message": "關閉語音",
                "expect_voice": False,
                "description": "關閉語音功能"
            },
            {
                "message": "現在還有聲音嗎？",
                "expect_voice": False,
                "description": "確認語音已關閉"
            }
        ]
        
        success_count = 0
        voice_urls = []
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n📋 測試 {i}: {scenario['description']}")
            
            success, voice_url = self.simulate_user_message(
                scenario['message'], 
                scenario['expect_voice']
            )
            
            if success:
                success_count += 1
                if voice_url:
                    voice_urls.append({
                        "scenario": scenario['description'],
                        "url": voice_url
                    })
            
            time.sleep(1)  # 避免API請求過快
        
        # 測試結果摘要
        print("\n" + "=" * 60)
        print("🎉 語音功能測試完成！")
        print(f"✅ 成功率: {success_count}/{len(test_scenarios)} ({success_count/len(test_scenarios)*100:.1f}%)")
        
        if voice_urls:
            print(f"\n🎵 生成的語音文件 ({len(voice_urls)} 個):")
            for voice in voice_urls:
                print(f"   {voice['scenario']}: {voice['url']}")
        
        print(f"\n💡 測試建議:")
        print(f"   1. 逐個試聽上述語音文件")
        print(f"   2. 檢查不同模式的語調差異")
        print(f"   3. 確認語音開關功能正常")
        print(f"   4. 測試語音品質和發音清晰度")
        
        return success_count == len(test_scenarios)

def main():
    simulator = VoiceUserSimulator()
    
    if not voice_system or not voice_system.enabled:
        print("❌ 語音系統未啟用，無法進行測試")
        print("請確認 ELEVENLABS_API_KEY 已正確設定")
        return
    
    print("🎤 語音系統已啟用，開始模擬測試...")
    success = simulator.run_complete_voice_test()
    
    if success:
        print("\n🎉 所有語音功能測試通過！")
    else:
        print("\n⚠️ 部分語音功能需要調整")

if __name__ == "__main__":
    main()