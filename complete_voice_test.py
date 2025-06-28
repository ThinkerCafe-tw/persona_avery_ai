#!/usr/bin/env python3
"""
🎤🔊 完整語音交互測試
模擬 STT + TTS 完整語音對話流程
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from speech_to_text import stt_system
from main import voice_system, get_lumi_response, analyze_emotion, user_voice_preferences

class CompleteVoiceTestSimulator:
    def __init__(self):
        self.test_user_id = "voice_test_user_001"
        
    def simulate_voice_conversation(self):
        """模擬完整的語音對話流程"""
        print("🎭 完整語音交互功能測試")
        print("=" * 60)
        
        # 檢查系統狀態
        print("📋 系統狀態檢查:")
        print(f"   STT 系統: {'✅ 已啟用' if stt_system.enabled else '❌ 未啟用'}")
        print(f"   TTS 系統: {'✅ 已啟用' if voice_system and voice_system.enabled else '❌ 未啟用'}")
        
        if not (stt_system.enabled and voice_system and voice_system.enabled):
            print("⚠️ 語音系統未完全啟用，無法進行完整測試")
            return False
        
        # 模擬語音對話場景
        test_scenarios = [
            {
                "description": "開啟語音功能",
                "simulated_user_speech": "開啟語音",
                "expect_voice_output": False
            },
            {
                "description": "基本語音對話",
                "simulated_user_speech": "你好，今天天氣真好",
                "expect_voice_output": True
            },
            {
                "description": "情緒語音交流",
                "simulated_user_speech": "我今天心情很不好，感覺很失落",
                "expect_voice_output": True
            },
            {
                "description": "深度語音對話",
                "simulated_user_speech": "生命的意義是什麼？為什麼我們要活著？",
                "expect_voice_output": True
            },
            {
                "description": "搞笑語音互動",
                "simulated_user_speech": "講個笑話給我聽",
                "expect_voice_output": True
            }
        ]
        
        success_count = 0
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n📋 測試 {i}: {scenario['description']}")
            print(f"👤 模擬用戶語音: \"{scenario['simulated_user_speech']}\"")
            
            success = self.simulate_single_voice_interaction(
                scenario['simulated_user_speech'],
                scenario['expect_voice_output']
            )
            
            if success:
                success_count += 1
                print(f"✅ 測試 {i} 成功")
            else:
                print(f"❌ 測試 {i} 失敗")
            
            print("-" * 40)
        
        # 測試結果摘要
        print(f"\n🎉 完整語音交互測試完成！")
        print(f"✅ 成功率: {success_count}/{len(test_scenarios)} ({success_count/len(test_scenarios)*100:.1f}%)")
        
        return success_count == len(test_scenarios)
    
    def simulate_single_voice_interaction(self, user_speech_text, expect_voice_output):
        """模擬單次語音交互"""
        try:
            # 步驟 1: 模擬 STT - 語音轉文字
            print(f"🎤 [STT] 模擬語音轉文字: {user_speech_text}")
            
            # 步驟 2: 分析情緒和生成回應
            persona_type = analyze_emotion(user_speech_text, self.test_user_id)
            lumi_response = get_lumi_response(user_speech_text, self.test_user_id)
            
            print(f"🎭 [AI] 偵測人格: {persona_type}")
            print(f"💬 [AI] Lumi回應: {lumi_response[:50]}...")
            
            # 步驟 3: 檢查語音偏好和生成語音
            user_wants_voice = user_voice_preferences.get(self.test_user_id, False)
            
            if expect_voice_output and user_wants_voice:
                print(f"🔊 [TTS] 生成語音回應...")
                
                # 生成語音
                audio_content = voice_system.generate_lumi_voice(lumi_response, persona_type)
                
                if audio_content:
                    print(f"✅ [TTS] 語音生成成功 ({len(audio_content)} bytes)")
                    
                    # 測試上傳
                    audio_url = voice_system.upload_audio_to_temp_host(audio_content)
                    if audio_url:
                        print(f"🌐 [TTS] 語音URL: {audio_url[:50]}...")
                        return True
                    else:
                        print(f"❌ [TTS] 音頻上傳失敗")
                        return False
                else:
                    print(f"❌ [TTS] 語音生成失敗")
                    return False
            else:
                print(f"📝 [TEXT] 僅文字回應（語音{'已關閉' if not user_wants_voice else '未預期'}）")
                return True
                
        except Exception as e:
            print(f"❌ 語音交互模擬錯誤: {e}")
            return False
    
    def setup_voice_preferences(self):
        """設置測試用戶的語音偏好"""
        user_voice_preferences[self.test_user_id] = True
        print(f"✅ 已為測試用戶開啟語音功能")

def main():
    simulator = CompleteVoiceTestSimulator()
    
    # 設置語音偏好
    simulator.setup_voice_preferences()
    
    # 執行完整測試
    success = simulator.simulate_voice_conversation()
    
    if success:
        print("\n🎉 所有語音交互功能測試通過！")
        print("💡 可以在 LINE 中測試實際語音功能了")
    else:
        print("\n⚠️ 部分語音功能需要調整")
        print("🔧 請檢查 STT 和 TTS 系統設定")

if __name__ == "__main__":
    main()