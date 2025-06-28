#!/usr/bin/env python3
"""
🧪 STT (Speech-to-Text) 系統測試
測試語音轉文字功能是否正常運作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from speech_to_text import stt_system, test_stt_system

def main():
    print("🎤 開始測試 STT 系統...")
    print("=" * 50)
    
    # 測試系統初始化
    print("📋 測試 1: 系統初始化檢查")
    if test_stt_system():
        print("✅ STT 系統初始化成功")
    else:
        print("❌ STT 系統初始化失敗")
        print("   請檢查 GOOGLE_APPLICATION_CREDENTIALS_JSON 環境變數")
        return
    
    print("\n📋 測試 2: 系統狀態檢查")
    print(f"   啟用狀態: {stt_system.enabled}")
    print(f"   Project ID: {stt_system.project_id}")
    print(f"   Client: {'已初始化' if stt_system.client else '未初始化'}")
    
    print("\n📋 測試 3: 錯誤訊息檢查")
    error_msg = stt_system.get_friendly_error_message()
    print(f"   錯誤訊息: {error_msg}")
    
    print("\n" + "=" * 50)
    print("🎉 STT 系統測試完成！")
    
    if stt_system.enabled:
        print("\n💡 下一步測試建議:")
        print("   1. 在 LINE 中發送語音訊息測試實際轉換")
        print("   2. 測試不同語言和方言的識別準確度")
        print("   3. 測試背景噪音環境下的識別能力")
        print("   4. 監控語音轉換的處理時間和成功率")
    else:
        print("\n⚠️ 需要設定環境變數才能進行實際測試")

if __name__ == "__main__":
    main()