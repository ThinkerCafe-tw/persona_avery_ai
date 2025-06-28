#!/usr/bin/env python3
"""
簡單測試音頻上傳功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import voice_system

def test_audio_upload():
    if not voice_system or not voice_system.enabled:
        print("❌ 語音系統未啟用")
        return
    
    # 生成測試語音
    test_text = "你好，我是Lumi！這是語音測試。"
    print(f"🎤 生成測試語音: {test_text}")
    
    audio_content = voice_system.generate_lumi_voice(test_text, "friend")
    
    if audio_content:
        print(f"✅ 語音生成成功 ({len(audio_content)} bytes)")
        
        # 測試上傳
        print("🌐 測試音頻上傳...")
        audio_url = voice_system.upload_audio_to_temp_host(audio_content)
        
        if audio_url:
            print(f"🎉 測試成功！音頻URL: {audio_url}")
        else:
            print("❌ 上傳失敗")
    else:
        print("❌ 語音生成失敗")

if __name__ == "__main__":
    test_audio_upload()