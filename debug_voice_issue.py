#!/usr/bin/env python3
"""
診斷語音問題
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import voice_system, get_lumi_response, user_voice_preferences

def debug_voice_issue():
    print("🔍 診斷語音問題")
    print("=" * 40)
    
    # 1. 檢查語音系統狀態
    print("1️⃣ 語音系統狀態:")
    if voice_system:
        print(f"   ✅ 語音系統已初始化")
        print(f"   🎤 啟用狀態: {voice_system.enabled}")
        print(f"   🔑 API Key: {'已設定' if voice_system.elevenlabs_api_key and voice_system.elevenlabs_api_key != 'YOUR_ACTUAL_API_KEY_HERE' else '未設定'}")
        print(f"   🎭 聲音ID: {voice_system.chinese_voice_id}")
    else:
        print("   ❌ 語音系統未初始化")
        return
    
    print()
    
    # 2. 模擬用戶開啟語音
    test_user_id = "test_user_debug"
    print("2️⃣ 模擬用戶開啟語音:")
    print("   💬 用戶說: '開啟語音'")
    
    response = get_lumi_response("開啟語音", test_user_id)
    print(f"   📝 Lumi回應: {response[:50]}...")
    print(f"   🔄 用戶語音偏好: {user_voice_preferences.get(test_user_id, '未設定')}")
    
    print()
    
    # 3. 模擬正常對話測試語音
    print("3️⃣ 模擬正常對話:")
    print("   💬 用戶說: '你好'")
    
    # 檢查用戶語音偏好
    user_wants_voice = user_voice_preferences.get(test_user_id, False)
    print(f"   🔊 用戶要語音嗎: {user_wants_voice}")
    
    if user_wants_voice and voice_system.enabled:
        print("   🎤 應該生成語音...")
        
        # 測試語音生成
        test_text = "你好！我是Lumi～"
        audio_content = voice_system.generate_lumi_voice(test_text, "friend")
        
        if audio_content:
            print(f"   ✅ 語音生成成功 ({len(audio_content)} bytes)")
            
            # 測試上傳
            url = voice_system.upload_audio_to_temp_host(audio_content)
            if url:
                print(f"   🌐 音頻上傳成功: {url}")
            else:
                print("   ❌ 音頻上傳失敗")
        else:
            print("   ❌ 語音生成失敗")
    else:
        print("   ⚠️ 不會生成語音的原因:")
        if not user_wants_voice:
            print("     - 用戶未開啟語音偏好")
        if not voice_system.enabled:
            print("     - 語音系統未啟用")
    
    print()
    
    # 4. 檢查LINE Bot的語音整合邏輯
    print("4️⃣ LINE Bot語音整合邏輯檢查:")
    print("   📋 理論流程:")
    print("     1. 用戶發送訊息到LINE")
    print("     2. handle_message函數處理")
    print("     3. 檢查 user_voice_preferences[user_id]")
    print("     4. 如果為True且voice_system.enabled，則生成語音")
    print("     5. 上傳音頻到托管服務")
    print("     6. 創建AudioMessage")
    print("     7. 發送TextMessage + AudioMessage")
    
    print()
    print("🎯 可能的問題:")
    print("   1. Railway部署失敗 -> LINE Bot根本沒運作")
    print("   2. 用戶沒說'開啟語音' -> 語音偏好為False")
    print("   3. 11Labs API Key在Railway上沒設定")
    print("   4. 音頻上傳服務在Railway環境失敗")
    print("   5. LINE AudioMessage格式或權限問題")

if __name__ == "__main__":
    debug_voice_issue()