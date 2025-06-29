#!/usr/bin/env python3
"""
🎤 Lumi Whisper STT (Speech-to-Text) 語音轉文字系統
使用 OpenAI Whisper 本地模型，免費且無限制
"""

import whisper
import tempfile
import os
import logging

class LumiWhisperSTT:
    def __init__(self, model_size="base"):
        """
        初始化 Whisper STT 系統
        
        Args:
            model_size: 模型大小 ("tiny", "base", "small", "medium", "large")
                       base 是速度和準確度的最佳平衡
        """
        self.model_size = model_size
        self.model = None
        self.enabled = False
        
        try:
            print(f"🎤 正在載入 Whisper {model_size} 模型...")
            self.model = whisper.load_model(model_size)
            self.enabled = True
            print(f"✅ Whisper STT 系統已初始化")
            print(f"   模型: {model_size}")
            print(f"   語言: 多語言 (包含中文)")
            print(f"   成本: 完全免費")
            print(f"   限制: 無限制")
            
        except Exception as e:
            print(f"❌ Whisper STT 初始化失敗: {e}")
            self.enabled = False
    
    def transcribe_audio(self, audio_file_path, language="zh"):
        """
        將音檔轉換為文字
        
        Args:
            audio_file_path: 音檔路徑
            language: 語言代碼 ("zh" 中文, "en" 英文, None 自動檢測)
        
        Returns:
            str: 轉錄的文字，失敗返回 None
        """
        if not self.enabled:
            print("❌ Whisper STT 系統未啟用")
            return None
        
        try:
            print(f"🎤 正在轉錄音檔: {os.path.basename(audio_file_path)}")
            
            # 使用 Whisper 轉錄
            result = self.model.transcribe(
                audio_file_path,
                language=language,
                fp16=False  # 確保兼容性
            )
            
            text = result["text"].strip()
            
            if text:
                print(f"✅ 轉錄完成: {text[:50]}{'...' if len(text) > 50 else ''}")
                return text
            else:
                print("⚠️ 轉錄結果為空")
                return None
                
        except Exception as e:
            print(f"❌ 音檔轉錄失敗: {e}")
            return None
    
    def transcribe_audio_content(self, audio_content, audio_format="wav", language="zh"):
        """
        將音檔內容（bytes）轉換為文字
        
        Args:
            audio_content: 音檔二進位內容
            audio_format: 音檔格式 ("wav", "mp3", "m4a", "ogg")
            language: 語言代碼
        
        Returns:
            str: 轉錄的文字，失敗返回 None
        """
        if not self.enabled:
            print("❌ Whisper STT 系統未啟用")
            return None
        
        # 創建臨時檔案
        try:
            with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as temp_file:
                temp_file.write(audio_content)
                temp_path = temp_file.name
            
            # 轉錄
            result = self.transcribe_audio(temp_path, language)
            
            # 清理臨時檔案
            os.unlink(temp_path)
            
            return result
            
        except Exception as e:
            print(f"❌ 音檔內容轉錄失敗: {e}")
            return None
    
    def get_supported_languages(self):
        """
        取得支援的語言列表
        """
        return {
            "zh": "中文 (Chinese)",
            "en": "英文 (English)", 
            "ja": "日文 (Japanese)",
            "ko": "韓文 (Korean)",
            "es": "西班牙文 (Spanish)",
            "fr": "法文 (French)",
            "de": "德文 (German)",
            "auto": "自動檢測 (Auto-detect)"
        }
    
    def get_model_info(self):
        """
        取得模型資訊
        """
        if not self.enabled:
            return None
            
        return {
            "model_size": self.model_size,
            "enabled": self.enabled,
            "cost": "免費",
            "limitations": "無限制",
            "offline": True,
            "privacy": "完全本地處理"
        }

# 創建全域實例
whisper_stt = LumiWhisperSTT()

if __name__ == "__main__":
    # 測試程式
    print("🧪 Whisper STT 系統測試")
    print("=" * 40)
    
    if whisper_stt.enabled:
        print("✅ 系統正常，可以開始使用")
        
        # 顯示支援語言
        languages = whisper_stt.get_supported_languages()
        print(f"\n📋 支援語言:")
        for code, name in languages.items():
            print(f"   {code}: {name}")
        
        # 顯示模型資訊
        info = whisper_stt.get_model_info()
        print(f"\n📊 模型資訊:")
        for key, value in info.items():
            print(f"   {key}: {value}")
    else:
        print("❌ 系統初始化失敗")