#!/usr/bin/env python3
"""
測試不同中文女聲
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import voice_system
import requests

def test_voice_with_id(voice_id, voice_name, text="你好！我是Lumi～"):
    """測試指定聲音ID"""
    
    # 臨時改變voice_system的ID
    original_id = voice_system.chinese_voice_id
    voice_system.chinese_voice_id = voice_id
    
    print(f"🎤 測試 {voice_name}")
    print(f"💬 文字: {text}")
    
    audio_content = voice_system.generate_lumi_voice(text, "friend")
    
    if audio_content:
        print(f"✅ 語音生成成功 ({len(audio_content):,} bytes)")
        
        # 上傳測試
        url = voice_system.upload_audio_to_temp_host(audio_content)
        if url:
            print(f"🌐 試聽: {url}")
        else:
            print("⚠️ 上傳失敗")
    else:
        print("❌ 語音生成失敗")
    
    # 恢復原ID
    voice_system.chinese_voice_id = original_id
    print("-" * 50)

def main():
    print("🎭 中文女聲大比拼")
    print("=" * 50)
    
    if not voice_system or not voice_system.enabled:
        print("❌ 語音系統未啟用")
        return
    
    voices_to_test = [
        ("hkfHEbBvdQFNX4uWHqRF", "Stacy (中國大陸口音)"),
        ("kGjJqO6wdwRN9iJsoeIC", "Yui (台灣口音 - 優雅舒緩)"), 
        ("9lHjugDhwqoxA5MhX0az", "Anna Su (台灣口音 - 輕鬆友善)")
    ]
    
    test_text = "你好！我是Lumi～很高興認識你！"
    
    for voice_id, voice_name in voices_to_test:
        test_voice_with_id(voice_id, voice_name, test_text)
    
    print("🎉 測試完成！")
    print("💡 選擇你喜歡的聲音，我就改成那個！")

if __name__ == "__main__":
    main()