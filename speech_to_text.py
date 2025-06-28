#!/usr/bin/env python3
"""
🎤 Lumi STT (Speech-to-Text) 語音轉文字系統
支援 LINE 語音訊息處理與 Google Speech-to-Text API
"""

import os
import json
import tempfile
from google.cloud import speech
from google.oauth2 import service_account

class LumiSTTSystem:
    def __init__(self):
        self.enabled = False
        self.client = None
        self.project_id = None
        
        # 嘗試初始化 Google Speech-to-Text
        try:
            # 使用與 Vertex AI 相同的認證設定
            credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
            
            if credentials_json:
                # 解析認證資訊
                credentials_dict = json.loads(credentials_json)
                self.project_id = credentials_dict.get('project_id')
                
                # 建立認證
                credentials = service_account.Credentials.from_service_account_info(credentials_dict)
                
                # 初始化 Speech-to-Text 客戶端
                self.client = speech.SpeechClient(credentials=credentials)
                self.enabled = True
                
                print(f"🎤 Lumi STT系統已初始化")
                print(f"   Project: {self.project_id}")
                
            else:
                print("⚠️ 未找到Google認證，STT功能將停用")
                
        except Exception as e:
            print(f"❌ STT系統初始化失敗: {e}")
            self.enabled = False
    
    def transcribe_audio(self, audio_content, language_code="zh-TW"):
        """
        將音頻內容轉換為文字
        
        Args:
            audio_content: 音頻二進制資料
            language_code: 語言代碼 (預設台灣中文)
            
        Returns:
            str: 轉換後的文字，如果失敗則返回 None
        """
        if not self.enabled:
            print("❌ STT系統未啟用")
            return None
            
        try:
            # 配置語音識別設定
            audio = speech.RecognitionAudio(content=audio_content)
            config = speech.RecognitionConfig(
                # LINE 語音訊息通常是 M4A 格式，但我們先嘗試 OGG_OPUS
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=16000,  # 標準採樣率
                language_code=language_code,
                alternative_language_codes=["zh-CN", "zh-HK"],  # 備用語言
                enable_automatic_punctuation=True,  # 自動標點符號
                model="latest_long",  # 使用最新的長音頻模型
                use_enhanced=True,  # 使用增強模型
                audio_channel_count=1,  # 單聲道
            )
            
            print(f"🔄 開始語音識別...")
            
            # 執行語音識別
            response = self.client.recognize(config=config, audio=audio)
            
            # 處理識別結果
            if response.results:
                # 取得最佳識別結果
                transcript = response.results[0].alternatives[0].transcript
                confidence = response.results[0].alternatives[0].confidence
                
                print(f"✅ 語音識別成功")
                print(f"   文字: {transcript}")
                print(f"   信心度: {confidence:.2%}")
                
                return transcript.strip()
            else:
                print("⚠️ 無法識別語音內容")
                return None
                
        except Exception as e:
            print(f"❌ 語音識別錯誤: {e}")
            
            # 如果是編碼問題，嘗試其他格式
            if "encoding" in str(e).lower():
                print("🔄 嘗試備用音頻格式...")
                return self._try_alternative_formats(audio_content, language_code)
            
            return None
    
    def _try_alternative_formats(self, audio_content, language_code):
        """嘗試不同的音頻編碼格式"""
        alternative_encodings = [
            speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            speech.RecognitionConfig.AudioEncoding.MP3,
            speech.RecognitionConfig.AudioEncoding.LINEAR16,
            speech.RecognitionConfig.AudioEncoding.MULAW,
            speech.RecognitionConfig.AudioEncoding.AMR,
            speech.RecognitionConfig.AudioEncoding.AMR_WB,
        ]
        
        for encoding in alternative_encodings:
            try:
                print(f"🔄 嘗試編碼格式: {encoding}")
                
                audio = speech.RecognitionAudio(content=audio_content)
                config = speech.RecognitionConfig(
                    encoding=encoding,
                    sample_rate_hertz=16000,
                    language_code=language_code,
                    alternative_language_codes=["zh-CN", "zh-HK"],
                    enable_automatic_punctuation=True,
                    model="latest_short" if encoding in [
                        speech.RecognitionConfig.AudioEncoding.AMR,
                        speech.RecognitionConfig.AudioEncoding.AMR_WB
                    ] else "latest_long"
                )
                
                response = self.client.recognize(config=config, audio=audio)
                
                if response.results:
                    transcript = response.results[0].alternatives[0].transcript
                    print(f"✅ 備用格式識別成功: {transcript}")
                    return transcript.strip()
                    
            except Exception as e:
                print(f"   格式 {encoding} 失敗: {e}")
                continue
        
        print("❌ 所有音頻格式都無法識別")
        return None
    
    def process_line_audio_message(self, message_content):
        """
        處理 LINE 語音訊息
        
        Args:
            message_content: LINE 語音訊息內容
            
        Returns:
            str: 轉換後的文字
        """
        if not self.enabled:
            return None
            
        try:
            # 取得音頻資料
            audio_data = message_content.content
            
            print(f"📥 收到語音訊息 ({len(audio_data)} bytes)")
            
            # 執行語音轉文字
            transcript = self.transcribe_audio(audio_data)
            
            if transcript:
                print(f"🎤➡️📝 語音轉文字成功: {transcript}")
                return transcript
            else:
                print("❌ 語音轉文字失敗")
                return None
                
        except Exception as e:
            print(f"❌ 處理LINE語音訊息錯誤: {e}")
            return None
    
    def get_friendly_error_message(self):
        """取得用戶友好的錯誤訊息"""
        return "不好意思，我沒聽清楚你說什麼，可以再說一次嗎？或者用文字跟我說～"

# 全域 STT 系統實例
stt_system = LumiSTTSystem()

def test_stt_system():
    """測試 STT 系統"""
    print("🧪 測試 STT 系統...")
    
    if stt_system.enabled:
        print("✅ STT 系統已啟用，可以處理語音訊息")
        return True
    else:
        print("❌ STT 系統未啟用")
        return False

if __name__ == "__main__":
    test_stt_system()