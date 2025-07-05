#!/usr/bin/env python3
"""
記憶系統測試腳本
驗證記憶存儲和檢索功能
"""

import os
from dotenv import load_dotenv
from ai_logic import get_lumi_response

def test_memory_system():
    """測試記憶系統功能"""
    print("🧠 記憶系統測試開始\n")
    
    # 測試用戶ID
    test_user_id = "test_user_123"
    
    # 測試對話
    test_conversations = [
        "你好，我是莫莫",
        "我喜歡看電影",
        "我今天心情不太好",
        "你記得我是誰嗎？"
    ]
    
    print("📝 開始測試對話...")
    
    for i, message in enumerate(test_conversations, 1):
        print(f"\n--- 對話 {i} ---")
        print(f"用戶: {message}")
        
        # 獲取回應
        response = get_lumi_response(message, test_user_id)
        print(f"Lumi: {response}")
        
        print(f"✅ 對話 {i} 完成")
    
    print("\n🎯 記憶系統測試完成！")
    print("請檢查 Railway 日誌中是否有記憶存儲的訊息")

if __name__ == "__main__":
    load_dotenv()
    test_memory_system() 