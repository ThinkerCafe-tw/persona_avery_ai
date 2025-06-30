#!/usr/bin/env python3
"""
🧠 pgvector 連接測試
驗證 Cruz 資料庫連接和記憶功能
"""

import os
import requests
import time
from datetime import datetime

def test_deployment_with_pgvector():
    """測試部署後的 pgvector 狀態"""
    
    print("🚀 開始 pgvector 連接測試")
    print("=" * 50)
    
    # 等待 Railway 重新部署
    print("⏳ 等待 Railway 重新部署 DATABASE_URL 變更...")
    print("   這通常需要 2-3 分鐘...")
    
    base_url = "https://lumi-line-bot-production.up.railway.app"
    
    # 監控部署狀態
    for attempt in range(12):  # 最多等待 6 分鐘
        print(f"\n🔍 檢查 {attempt + 1}/12 - {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # 測試健康檢查
            response = requests.get(f"{base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 服務已上線")
                print(f"📊 狀態: {data}")
                return True
            else:
                print(f"⏳ 服務重啟中... HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("⏳ 服務重啟中... 連接中斷")
        except Exception as e:
            print(f"⏳ 服務重啟中... {e}")
        
        time.sleep(30)  # 等待 30 秒
    
    print("❌ 等待超時，請手動檢查 Railway 部署狀態")
    return False

def check_memory_system_logs():
    """檢查記憶系統日誌指示"""
    
    print("\n🧠 記憶系統狀態檢查")
    print("-" * 30)
    
    print("期待在 Railway 日誌中看到：")
    print("✅ '🎯 pgvector 記憶系統已連接 (持久化記憶)'")
    print("❌ 不應該看到：'WARNING:simple_memory:pgvector 不可用'")
    
    print("\n💡 檢查方法：")
    print("1. 打開 Railway 控制台")
    print("2. 進入 Deployments → Deploy Logs")
    print("3. 查看記憶系統初始化訊息")

def test_pgvector_memory_features():
    """測試 pgvector 記憶功能"""
    
    print("\n🧪 pgvector 記憶功能測試")
    print("-" * 30)
    
    test_messages = [
        {
            "message": "測試pgvector記憶",
            "expect": "驗證是否使用資料庫存儲"
        },
        {
            "message": "我叫 PgVector 測試員",
            "expect": "測試用戶資訊存儲到資料庫"
        },
        {
            "message": "我的工作是測試工程師",
            "expect": "測試職業資訊存儲"
        },
        {
            "message": "你還記得我的名字嗎？",
            "expect": "測試從資料庫讀取記憶"
        }
    ]
    
    print("建議在 LINE 中依序發送以下測試訊息：")
    print()
    
    for i, test in enumerate(test_messages, 1):
        print(f"{i}. 發送：「{test['message']}」")
        print(f"   目標：{test['expect']}")
        print()
    
    print("🎯 關鍵差異：")
    print("• pgvector 模式：記憶會永久保存在資料庫")
    print("• 內存模式：重啟後記憶會消失")
    print("• 你可以嘗試讓系統重啟，看記憶是否保持")

def monitor_pgvector_upgrade():
    """監控 pgvector 升級過程"""
    
    print("🔄 pgvector 升級監控指南")
    print("=" * 50)
    
    print("📋 升級檢查清單：")
    print("✅ 1. DATABASE_URL 環境變數已設定")
    print("⏳ 2. Railway 重新部署中...")
    print("⏳ 3. 等待 pgvector 連接成功")
    print("⏳ 4. 測試記憶功能")
    print("⏳ 5. 驗證持久化存儲")
    
    print("\n🚨 故障排除：")
    print("如果 pgvector 連接失敗，可能原因：")
    print("• DATABASE_URL 格式錯誤")
    print("• 資料庫權限問題")
    print("• 網路連接問題")
    print("• psycopg2 依賴問題")
    
    print("\n📊 成功指標：")
    print("• 日誌顯示：'🎯 pgvector 記憶系統已連接'")
    print("• 不再有：'WARNING: pgvector 不可用'")
    print("• 記憶功能正常工作")
    print("• 系統重啟後記憶保持")

def main():
    """主測試流程"""
    
    print("🧠 pgvector 連接升級測試")
    print("=" * 60)
    
    # 1. 監控部署
    monitor_pgvector_upgrade()
    
    # 2. 測試連接
    if test_deployment_with_pgvector():
        print("\n🎉 部署成功！現在可以測試 pgvector 功能")
        
        # 3. 檢查日誌
        check_memory_system_logs()
        
        # 4. 功能測試
        test_pgvector_memory_features()
        
    else:
        print("\n⚠️ 部署可能還在進行中")
        print("請稍後手動檢查 Railway 控制台")
    
    print("\n" + "=" * 60)
    print("🎯 下一步：")
    print("1. 檢查 Railway 部署日誌中的記憶系統訊息")
    print("2. 在 LINE 中測試記憶功能")
    print("3. 驗證 pgvector 持久化存儲")

if __name__ == "__main__":
    main()