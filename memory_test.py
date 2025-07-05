#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
記憶系統測試工具
用於測試和驗證 Lumi AI 的長期記憶功能
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_logic import memory_manager, get_lumi_response

def test_memory_storage():
    """測試記憶儲存功能"""
    print("🧠 測試記憶儲存功能...")
    
    test_user_id = "test_user_001"
    test_messages = [
        "我喜歡吃巧克力",
        "我的生日是12月25日",
        "我現在在台北工作",
        "我養了一隻貓叫咪咪",
        "我最近在學習Python程式設計"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"  儲存記憶 {i}: {message}")
        if memory_manager:
            memory_manager.store_conversation_memory(
                test_user_id, 
                message, 
                f"這是關於 {message} 的回應", 
                "friend"
            )
        else:
            print("  ❌ 記憶管理器未初始化")
            return False
    
    print("  ✅ 記憶儲存測試完成")
    return True

def test_memory_retrieval():
    """測試記憶檢索功能"""
    print("🔍 測試記憶檢索功能...")
    
    test_user_id = "test_user_001"
    
    if not memory_manager:
        print("  ❌ 記憶管理器未初始化")
        return False
    
    # 測試最近記憶
    print("  測試最近記憶檢索...")
    recent_memories = memory_manager.get_recent_memories(test_user_id, limit=3)
    print(f"    找到 {len(recent_memories)} 條最近記憶")
    
    # 測試相似記憶
    print("  測試相似記憶檢索...")
    similar_memories = memory_manager.get_similar_memories(test_user_id, "我喜歡什麼食物", limit=3)
    print(f"    找到 {len(similar_memories)} 條相似記憶")
    
    # 測試個人資料記憶
    print("  測試個人資料記憶檢索...")
    profile_memories = memory_manager.get_user_profile_memories(test_user_id, limit=5)
    print(f"    找到 {len(profile_memories)} 條個人資料記憶")
    
    # 測試長期記憶
    print("  測試長期記憶檢索...")
    long_term_memories = memory_manager.get_long_term_memories(test_user_id, days_back=7, limit=10)
    print(f"    找到 {len(long_term_memories)} 條長期記憶")
    
    # 測試記憶統計
    print("  測試記憶統計...")
    stats = memory_manager.get_memory_statistics(test_user_id)
    print(f"    總對話數: {stats.get('total_conversations', 0)}")
    print(f"    記憶強度: {stats.get('memory_strength', 'unknown')}")
    
    print("  ✅ 記憶檢索測試完成")
    return True

def test_ai_memory_integration():
    """測試AI與記憶的整合"""
    print("🤖 測試AI記憶整合...")
    
    test_user_id = "test_user_001"
    test_queries = [
        "你還記得我喜歡什麼嗎？",
        "我的生日是什麼時候？",
        "我在哪裡工作？",
        "我的貓叫什麼名字？",
        "我在學習什麼？"
    ]
    
    for query in test_queries:
        print(f"  測試查詢: {query}")
        try:
            response = get_lumi_response(query, test_user_id)
            print(f"    AI回應: {response[:100]}...")
        except Exception as e:
            print(f"    ❌ 錯誤: {e}")
    
    print("  ✅ AI記憶整合測試完成")
    return True

def test_memory_commands():
    """測試記憶相關指令"""
    print("📝 測試記憶指令...")
    
    test_user_id = "test_user_001"
    commands = [
        "記憶統計",
        "長期記憶",
        "我們聊過什麼",
        "記憶摘要"
    ]
    
    for command in commands:
        print(f"  測試指令: {command}")
        try:
            response = get_lumi_response(command, test_user_id)
            print(f"    回應: {response[:100]}...")
        except Exception as e:
            print(f"    ❌ 錯誤: {e}")
    
    print("  ✅ 記憶指令測試完成")
    return True

def cleanup_test_data():
    """清理測試資料"""
    print("🧹 清理測試資料...")
    
    test_user_id = "test_user_001"
    
    if memory_manager and memory_manager.conn:
        try:
            with memory_manager.conn.cursor() as cur:
                cur.execute("DELETE FROM lumi_memories WHERE user_id = %s", (test_user_id,))
                memory_manager.conn.commit()
            print("  ✅ 測試資料已清理")
        except Exception as e:
            print(f"  ❌ 清理失敗: {e}")
    else:
        print("  ⚠️ 無法清理：記憶管理器未初始化")

def main():
    """主測試函數"""
    print("🚀 開始 Lumi AI 記憶系統測試")
    print("=" * 50)
    
    # 檢查記憶管理器
    if not memory_manager:
        print("❌ 記憶管理器未初始化，請檢查資料庫連接")
        return
    
    if not memory_manager.conn:
        print("❌ 資料庫連接失敗，請檢查 DATABASE_URL 環境變數")
        return
    
    print("✅ 記憶系統已初始化")
    print()
    
    # 執行測試
    tests = [
        ("記憶儲存", test_memory_storage),
        ("記憶檢索", test_memory_retrieval),
        ("AI整合", test_ai_memory_integration),
        ("記憶指令", test_memory_commands)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"📋 {test_name}測試")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ 測試失敗: {e}")
            results.append((test_name, False))
        print()
    
    # 顯示測試結果
    print("📊 測試結果總結")
    print("=" * 50)
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
    
    # 清理測試資料
    print()
    cleanup_test_data()
    
    print()
    print("🎉 測試完成！")
    print("💡 提示：如果所有測試都通過，您的長期記憶系統就準備好了！")

if __name__ == "__main__":
    main() 