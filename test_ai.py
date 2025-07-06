#!/usr/bin/env python3
import os
import sys
sys.path.append('.')

# 測試 AI 邏輯
try:
    import ai_logic
    print("✅ ai_logic 模組導入成功")
    
    # 測試方法是否存在
    if hasattr(ai_logic, 'get_lumi_response'):
        print("✅ get_lumi_response 方法存在")
        
        # 測試簡單回應
        try:
            response = ai_logic.get_lumi_response("嗨", "test_user")
            print(f"✅ AI 回應測試成功: {response}")
        except Exception as e:
            print(f"❌ AI 回應測試失敗: {e}")
    else:
        print("❌ get_lumi_response 方法不存在")
        
except Exception as e:
    print(f"❌ ai_logic 模組導入失敗: {e}")

# 測試記憶系統
try:
    import simple_memory
    print("✅ simple_memory 模組導入成功")
    
    memory = simple_memory.SimpleLumiMemory()
    print("✅ 記憶系統初始化成功")
    
except Exception as e:
    print(f"❌ 記憶系統測試失敗: {e}") 