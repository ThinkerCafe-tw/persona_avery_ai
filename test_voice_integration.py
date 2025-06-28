#!/usr/bin/env python3
"""
測試Lumi語音整合功能
模擬LINE Bot的語音訊息生成
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import voice_system, get_lumi_response, analyze_emotion

def test_voice_integration():
    """測試語音整合功能"""
    print("🤖 測試Lumi語音整合功能")
    print("=" * 50)
    
    # 測試用戶ID
    test_user_id = "test_user_123"
    
    # 測試案例
    test_cases = [
        {
            "message": "開啟語音",
            "expected_voice": False,  # 這個訊息本身不會有語音
            "description": "開啟語音功能"
        },
        {
            "message": "我今天心情不好",
            "expected_voice": True,  # 開啟後應該有語音
            "description": "情緒訊息測試"
        },
        {
            "message": "關閉語音", 
            "expected_voice": False,  # 關閉語音
            "description": "關閉語音功能"
        },
        {
            "message": "你好嗎？",
            "expected_voice": False,  # 關閉後不應該有語音
            "description": "關閉後測試"
        }
    ]
    
    print(f"🔍 語音系統狀態: {'啟用' if voice_system and voice_system.enabled else '停用'}")
    print()
    
    for i, case in enumerate(test_cases, 1):
        print(f"📋 測試 {i}: {case['description']}")
        print(f"💬 用戶訊息: {case['message']}")
        
        # 獲取回應
        response = get_lumi_response(case['message'], test_user_id)
        print(f"📝 文字回應: {response[:50]}...")
        
        # 檢測人格類型
        persona_type = analyze_emotion(case['message'], test_user_id)
        print(f"🎭 人格類型: {persona_type}")
        
        # 測試語音生成
        if voice_system and voice_system.enabled and case['expected_voice']:
            print("🎤 測試語音生成...")
            audio_content = voice_system.generate_lumi_voice(response, persona_type)
            
            if audio_content:
                print(f"✅ 語音生成成功 ({len(audio_content)} bytes)")
                
                # 測試音頻上傳
                print("🌐 測試音頻上傳...")
                audio_url = voice_system.upload_audio_to_temp_host(audio_content)
                
                if audio_url:
                    print(f"✅ 音頻上傳成功: {audio_url}")
                else:
                    print("❌ 音頻上傳失敗")
            else:
                print("❌ 語音生成失敗")
        else:
            expected_reason = "語音系統停用" if not (voice_system and voice_system.enabled) else "用戶未開啟語音"
            print(f"⏸️ 跳過語音生成 ({expected_reason})")
        
        print("-" * 30)
    
    print("🎉 語音整合測試完成！")

if __name__ == "__main__":
    test_voice_integration()