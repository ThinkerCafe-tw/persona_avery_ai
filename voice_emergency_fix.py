#!/usr/bin/env python3
"""
🚨 語音功能緊急修復
在 Vertex AI API 啟用前的臨時解決方案
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_emergency_voice_handler():
    """建立緊急語音處理函數"""
    
    emergency_responses = {
        "你好": "你好！我現在有點技術問題，但還是很開心聽到你的聲音！",
        "hello": "Hello! 我的語音系統在維修中，但我聽到你了！",
        "測試": "語音測試收到！我正在修復一些技術問題，請稍後再試～",
        "心情": "我知道你想聊心情，但我現在腦子有點當機，用文字跟我說會更好喔！",
        "問題": "我聽到你提問了，但現在回答功能有點故障，改用文字問我吧！",
        "謝謝": "不客氣！雖然我現在有點狀況，但還是很感謝你耐心等待～",
        "再見": "再見！希望下次見面時我已經完全康復了！",
    }
    
    def emergency_voice_response(transcribed_text):
        """基於關鍵詞的緊急回應"""
        text = transcribed_text.lower()
        
        for keyword, response in emergency_responses.items():
            if keyword in text:
                return response
        
        # 預設回應
        return f"我聽到你說「{transcribed_text}」，但我的AI大腦暫時在維修中！請用文字跟我聊，我會立即回應的～"
    
    return emergency_voice_response

def patch_main_voice_handler():
    """修補主程式的語音處理"""
    
    print("🚨 正在應用語音功能緊急修復...")
    
    # 這個函數可以在主程式中調用
    emergency_handler = create_emergency_voice_handler()
    
    patch_code = '''
# 緊急語音處理修補 - 臨時使用
def emergency_voice_fallback(transcribed_text):
    """緊急語音回應，不依賴 Vertex AI"""
    emergency_responses = {
        "你好": "你好！我現在有點技術問題，但還是很開心聽到你的聲音！",
        "hello": "Hello! 我的語音系統在維修中，但我聽到你了！",
        "測試": "語音測試收到！我正在修復一些技術問題，請稍後再試～",
        "心情": "我知道你想聊心情，但我現在腦子有點當機，用文字跟我說會更好喔！",
        "問題": "我聽到你提問了，但現在回答功能有點故障，改用文字問我吧！",
        "謝謝": "不客氣！雖然我現在有點狀況，但還是很感謝你耐心等待～",
        "再見": "再見！希望下次見面時我已經完全康復了！",
    }
    
    text = transcribed_text.lower()
    for keyword, response in emergency_responses.items():
        if keyword in text:
            return response
    
    return f"我聽到你說「{transcribed_text}」，但我的AI大腦暫時在維修中！請用文字跟我聊，我會立即回應的～"

# 修改 handle_audio_message 中的錯誤處理
# 將第1178行的 fallback_reply 替換為：
# fallback_reply = emergency_voice_fallback(transcribed_text)
'''
    
    print("📝 建議修改代碼：")
    print(patch_code)
    
    return emergency_handler

if __name__ == "__main__":
    handler = patch_main_voice_handler()
    
    # 測試緊急回應
    test_cases = ["你好", "測試語音", "我心情不好", "謝謝你"]
    
    print("\n🧪 測試緊急語音回應：")
    for test in test_cases:
        response = handler(test)
        print(f"   '{test}' → '{response}'")
    
    print("\n✅ 緊急修復方案已準備完成！")
    print("💡 請手動將 emergency_voice_fallback 函數加入 main.py 中")