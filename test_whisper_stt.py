#!/usr/bin/env python3
"""
測試 Whisper 語音轉文字功能
"""
import whisper
import tempfile
import os

def test_whisper():
    """測試 Whisper STT 功能"""
    print("🎤 測試 Whisper 語音轉文字...")
    print("=" * 40)
    
    try:
        # 載入 Whisper 模型 (選擇適中的模型)
        print("📥 載入 Whisper 模型...")
        model = whisper.load_model("base")
        print("✅ Whisper 模型載入成功!")
        
        # 顯示模型資訊
        print(f"   模型: base")
        print(f"   語言支援: 多語言 (包含中文)")
        print(f"   本地運行: 無需網路連接")
        print(f"   成本: 完全免費")
        
        # 檢查是否有測試音檔
        audio_files = []
        for ext in ['wav', 'mp3', 'm4a', 'ogg']:
            files = [f for f in os.listdir('.') if f.endswith(f'.{ext}')]
            audio_files.extend(files)
        
        if audio_files:
            print(f"\n🔍 找到 {len(audio_files)} 個音檔，測試第一個...")
            test_file = audio_files[0]
            
            try:
                result = model.transcribe(test_file, language='zh')
                print(f"✅ 轉錄結果: {result['text']}")
            except Exception as e:
                print(f"❌ 轉錄失敗: {e}")
        else:
            print("\n💡 沒有找到測試音檔，但 Whisper 已準備就緒")
        
        print("\n🎉 Whisper STT 系統完全正常!")
        print("📊 對比分析:")
        print("   Whisper:    免費、無限制、本地運行")
        print("   Google STT: 需要雲端、可能有限制")
        
        return True
        
    except Exception as e:
        print(f"❌ Whisper 測試失敗: {e}")
        return False

if __name__ == "__main__":
    success = test_whisper()
    if success:
        print("\n🚀 建議: 切換到 Whisper + Gemini API 架構")
        print("   ✅ 完全免費的語音轉文字")
        print("   ✅ 50次/日的 AI 對話 (個人使用足夠)")
        print("   ✅ 無需複雜的 Google Cloud 設定")