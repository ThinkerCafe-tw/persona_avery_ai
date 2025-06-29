#!/usr/bin/env python3
"""
🚀 Lumi 最優語音系統 - Cruz 架構
整合 Whisper STT + Gemini AI + 11Labs TTS
"""

import os
import tempfile
import requests
from dotenv import load_dotenv
from whisper_stt import whisper_stt
from gemini_ai import gemini_ai

load_dotenv()

class LumiOptimalVoiceSystem:
    def __init__(self):
        """
        初始化最優語音系統
        """
        self.stt = whisper_stt
        self.ai = gemini_ai
        self.tts_enabled = False
        
        # 初始化 11Labs TTS
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        if self.elevenlabs_api_key:
            self.tts_enabled = True
            print("🔊 11Labs TTS 已啟用")
        else:
            print("⚠️ 未找到 11Labs API Key，TTS 功能停用")
        
        # 系統狀態報告
        self.print_system_status()
    
    def print_system_status(self):
        """
        顯示系統狀態
        """
        print("\n🚀 Lumi 最優語音系統狀態")
        print("=" * 50)
        print(f"🎤 STT (Whisper):     {'✅ 已啟用' if self.stt.enabled else '❌ 未啟用'}")
        print(f"🧠 AI (Gemini):       {'✅ 已啟用' if self.ai.enabled else '❌ 未啟用'}")
        print(f"🔊 TTS (11Labs):      {'✅ 已啟用' if self.tts_enabled else '❌ 未啟用'}")
        
        if self.ai.enabled:
            print(f"💬 AI 額度:           {self.ai.daily_usage}/{self.ai.daily_limit} 已使用")
        
        # 整體狀態
        components_ready = sum([self.stt.enabled, self.ai.enabled, self.tts_enabled])
        print(f"📊 系統就緒度:        {components_ready}/3 ({components_ready/3*100:.0f}%)")
        
        if components_ready == 3:
            print("🎉 完整語音循環已就緒！")
        else:
            print("⚠️ 部分功能需要檢查")
    
    def speech_to_text(self, audio_file_path):
        """
        語音轉文字
        """
        if not self.stt.enabled:
            return None
        
        return self.stt.transcribe_audio(audio_file_path)
    
    def get_ai_response(self, text, user_info=None):
        """
        獲取 AI 回應
        """
        if not self.ai.enabled:
            return "抱歉，AI 系統目前無法使用。"
        
        return self.ai.get_personalized_response(text, user_info)
    
    def text_to_speech(self, text, output_file=None, voice_id="ErXwobaYiN019PkySvjV"):
        """
        文字轉語音
        
        Args:
            text: 要轉換的文字
            output_file: 輸出檔案路徑 (可選)
            voice_id: 11Labs 聲音 ID
        
        Returns:
            str: 語音檔案路徑，失敗返回 None
        """
        if not self.tts_enabled:
            print("❌ TTS 系統未啟用")
            return None
        
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                # 創建輸出檔案
                if not output_file:
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                        output_file = temp_file.name
                
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                print(f"🔊 語音合成完成: {output_file}")
                return output_file
            else:
                print(f"❌ TTS 請求失敗: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 文字轉語音失敗: {e}")
            return None
    
    def complete_voice_interaction(self, audio_file_path, user_info=None):
        """
        完整語音互動流程
        
        Args:
            audio_file_path: 輸入音檔路徑
            user_info: 用戶資訊
        
        Returns:
            dict: 包含各階段結果的字典
        """
        result = {
            "input_audio": audio_file_path,
            "transcribed_text": None,
            "ai_response": None,
            "output_audio": None,
            "success": False
        }
        
        print("\n🔄 開始完整語音互動流程...")
        
        # 1. 語音轉文字
        print("1️⃣ 語音轉文字...")
        transcribed_text = self.speech_to_text(audio_file_path)
        if not transcribed_text:
            print("❌ 語音轉文字失敗")
            return result
        
        result["transcribed_text"] = transcribed_text
        print(f"✅ 轉錄結果: {transcribed_text}")
        
        # 2. AI 回應生成
        print("2️⃣ AI 回應生成...")
        ai_response = self.get_ai_response(transcribed_text, user_info)
        if not ai_response:
            print("❌ AI 回應生成失敗")
            return result
        
        result["ai_response"] = ai_response
        print(f"✅ AI 回應: {ai_response[:100]}{'...' if len(ai_response) > 100 else ''}")
        
        # 3. 文字轉語音
        print("3️⃣ 文字轉語音...")
        output_audio = self.text_to_speech(ai_response)
        if output_audio:
            result["output_audio"] = output_audio
            print(f"✅ 語音合成完成")
        else:
            print("⚠️ 語音合成失敗，但文字回應可用")
        
        result["success"] = True
        print("🎉 完整語音互動流程完成！")
        
        return result
    
    def test_system_components(self):
        """
        測試系統各組件
        """
        print("\n🧪 系統組件測試")
        print("=" * 50)
        
        # 測試 STT
        print("🎤 測試 Whisper STT...")
        if self.stt.enabled:
            print("✅ Whisper STT 正常")
        else:
            print("❌ Whisper STT 異常")
        
        # 測試 AI
        print("\n🧠 測試 Gemini AI...")
        if self.ai.enabled:
            test_response = self.ai.get_response("你好")
            if test_response:
                print(f"✅ Gemini AI 正常")
                print(f"   測試回應: {test_response[:50]}...")
            else:
                print("❌ Gemini AI 回應失敗")
        else:
            print("❌ Gemini AI 異常")
        
        # 測試 TTS
        print("\n🔊 測試 11Labs TTS...")
        if self.tts_enabled:
            print("✅ 11Labs TTS 配置正常")
        else:
            print("❌ 11Labs TTS 配置異常")

# 創建全域實例
optimal_voice_system = LumiOptimalVoiceSystem()

if __name__ == "__main__":
    # 執行系統測試
    optimal_voice_system.test_system_components()
    
    print("\n📋 系統摘要:")
    print("   架構: Whisper + Gemini + 11Labs")
    print("   成本: 幾乎免費")
    print("   限制: 50次 AI 對話/日")
    print("   優點: 簡單、穩定、經濟")