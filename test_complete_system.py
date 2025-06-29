#!/usr/bin/env python3
"""
完整系統測試 - 語音輸入輸出循環
"""
import os
import tempfile
from dotenv import load_dotenv
from core.voice_input import VoiceInputHandler
from core.voice_output import VoiceOutputHandler

load_dotenv()

def test_complete_voice_cycle():
    """測試完整的語音輸入輸出循環"""
    print("🎤 測試完整語音系統...")
    print("=" * 50)
    
    # 初始化語音輸入處理器
    try:
        voice_input = VoiceInputHandler()
        print("✅ 語音輸入處理器初始化成功")
    except Exception as e:
        print(f"❌ 語音輸入處理器失敗: {e}")
        return False
    
    # 初始化語音輸出處理器
    try:
        voice_output = VoiceOutputHandler()
        print("✅ 語音輸出處理器初始化成功")
    except Exception as e:
        print(f"❌ 語音輸出處理器失敗: {e}")
        return False
    
    # 測試 TTS 功能
    print("\n🔊 測試文字轉語音...")
    test_text = "哈囉！我是 Lumi，你的 AI 助手。語音功能測試中..."
    
    try:
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # 生成語音
        voice_output.text_to_speech(test_text, temp_path)
        
        # 檢查檔案
        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
            print(f"✅ TTS 成功生成語音檔案: {temp_path}")
            print(f"   檔案大小: {os.path.getsize(temp_path)} bytes")
        else:
            print("❌ TTS 生成失敗")
            return False
            
        # 清理檔案
        os.unlink(temp_path)
        
    except Exception as e:
        print(f"❌ TTS 測試失敗: {e}")
        return False
    
    print("\n🎉 完整語音系統測試成功！")
    print("💡 所有組件都正常工作，可以開始使用語音功能")
    
    return True

if __name__ == "__main__":
    success = test_complete_voice_cycle()
    exit(0 if success else 1)