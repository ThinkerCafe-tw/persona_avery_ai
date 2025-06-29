#!/usr/bin/env python3
"""
🎉 最終 API 功能確認測試
確認所有 API 都正常工作
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

def test_all_apis():
    """測試所有 API 功能"""
    print("🎉 最終 API 功能確認測試")
    print("=" * 50)
    
    results = {}
    
    # 1. 測試 11Labs TTS
    print("🔊 測試 11Labs TTS API...")
    try:
        import requests
        api_key = os.getenv('ELEVENLABS_API_KEY')
        headers = {"xi-api-key": api_key}
        response = requests.get("https://api.elevenlabs.io/v1/user", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ 11Labs API 正常")
            results['elevenlabs'] = True
        else:
            print(f"❌ 11Labs API 失敗: {response.status_code}")
            results['elevenlabs'] = False
            
    except Exception as e:
        print(f"❌ 11Labs 測試失敗: {e}")
        results['elevenlabs'] = False
    
    # 2. 測試 STT
    print("\n🎤 測試 Speech-to-Text API...")
    try:
        from speech_to_text import stt_system
        if stt_system.enabled:
            print(f"✅ STT 系統正常 (專案: {stt_system.project_id})")
            results['stt'] = True
        else:
            print("❌ STT 系統未啟用")
            results['stt'] = False
    except Exception as e:
        print(f"❌ STT 測試失敗: {e}")
        results['stt'] = False
    
    # 3. 測試 TTS (語音輸出)
    print("\n🔊 測試 TTS 語音輸出...")
    try:
        from main import voice_system
        if voice_system and voice_system.enabled:
            print("✅ TTS 系統正常")
            results['tts'] = True
        else:
            print("❌ TTS 系統未啟用")
            results['tts'] = False
    except Exception as e:
        print(f"❌ TTS 測試失敗: {e}")
        results['tts'] = False
    
    # 4. 測試 Vertex AI
    print("\n🧠 測試 Vertex AI...")
    try:
        from lumi_ai import lumi_ai
        if hasattr(lumi_ai, 'vertex_model') and lumi_ai.vertex_model:
            print("✅ Vertex AI 正常")
            results['vertex'] = True
        else:
            print("❌ Vertex AI 未初始化")
            results['vertex'] = False
    except Exception as e:
        print(f"❌ Vertex AI 測試失敗: {e}")
        results['vertex'] = False
    
    # 總結
    print("\n" + "=" * 50)
    print("📊 測試結果總結:")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    for service, status in results.items():
        emoji = "✅" if status else "❌"
        print(f"   {emoji} {service.upper()}: {'正常' if status else '失敗'}")
    
    print(f"\n🎯 成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 所有 API 都正常工作！系統已準備就緒")
        return True
    else:
        print("⚠️ 部分 API 需要檢查")
        return False

if __name__ == "__main__":
    success = test_all_apis()
    exit(0 if success else 1)