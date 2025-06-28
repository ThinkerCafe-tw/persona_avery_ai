#!/usr/bin/env python3
"""
超簡單的露米語音測試
不依賴LINE Bot，直接測試語音生成
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import voice_system

def simple_test():
    print("🤖 露米語音快速測試")
    print("=" * 30)
    
    if not voice_system or not voice_system.enabled:
        print("❌ 語音系統未啟用")
        print("   請檢查 ELEVENLABS_API_KEY 是否正確設定")
        return
    
    print("✅ 語音系統已啟用！")
    print()
    
    # 測試不同心情的露米
    test_cases = [
        ("你好！我是Lumi～", "friend", "開心模式"),
        ("我能感受到你的心情。", "healing", "療癒模式"),
        ("生活就像一條河流...", "wisdom", "智慧模式")
    ]
    
    for text, mode, description in test_cases:
        print(f"🎭 測試 {description}")
        print(f"💬 文字: {text}")
        
        # 生成語音
        audio_content = voice_system.generate_lumi_voice(text, mode)
        
        if audio_content:
            print(f"✅ 語音生成成功！({len(audio_content):,} bytes)")
            
            # 上傳測試
            url = voice_system.upload_audio_to_temp_host(audio_content)
            if url:
                print(f"🌐 可以播放: {url}")
                print("   ↑ 複製這個網址到瀏覽器就能聽到露米的聲音！")
            else:
                print("⚠️ 上傳失敗，但語音生成正常")
        else:
            print("❌ 語音生成失敗")
        
        print("-" * 30)
    
    print("🎉 測試完成！")
    print("💡 如果看到網址，複製到瀏覽器就能聽到露米說話了！")

if __name__ == "__main__":
    simple_test()