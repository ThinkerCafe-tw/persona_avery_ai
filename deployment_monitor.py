#!/usr/bin/env python3
"""
🚀 部署監控工具
監控 Railway 部署狀態和健康狀況
"""

import requests
import time
import json
from datetime import datetime

class DeploymentMonitor:
    def __init__(self, service_url="https://lumi-line-bot-production.up.railway.app"):
        self.service_url = service_url
        self.health_endpoint = f"{service_url}/health"
        self.status_endpoint = f"{service_url}/"
    
    def check_service_health(self):
        """檢查服務健康狀態"""
        try:
            response = requests.get(self.health_endpoint, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 服務健康: {data}")
                return True
            else:
                print(f"❌ 健康檢查失敗: HTTP {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ 無法連接到服務（可能正在部署中）")
            return False
        except requests.exceptions.Timeout:
            print("❌ 請求超時")
            return False
        except Exception as e:
            print(f"❌ 健康檢查錯誤: {e}")
            return False
    
    def check_service_status(self):
        """檢查服務詳細狀態"""
        try:
            response = requests.get(self.status_endpoint, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("📊 服務狀態:")
                print(f"  版本: {data.get('version', 'Unknown')}")
                print(f"  架構: {data.get('architecture', 'Unknown')}")
                
                features = data.get('features', {})
                print("  功能狀態:")
                for feature, status in features.items():
                    icon = "✅" if status else "❌"
                    print(f"    {icon} {feature}: {status}")
                
                deployment = data.get('deployment', {})
                if deployment:
                    print("  部署資訊:")
                    for key, value in deployment.items():
                        print(f"    {key}: {value}")
                
                return True
            else:
                print(f"❌ 狀態檢查失敗: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 狀態檢查錯誤: {e}")
            return False
    
    def wait_for_deployment(self, max_wait_minutes=10):
        """等待部署完成"""
        print(f"⏳ 等待部署完成（最多 {max_wait_minutes} 分鐘）...")
        
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        
        while time.time() - start_time < max_wait_seconds:
            print(f"\n🔍 檢查時間: {datetime.now().strftime('%H:%M:%S')}")
            
            if self.check_service_health():
                print("🎉 部署成功！服務已上線")
                self.check_service_status()
                return True
            
            print("⏳ 等待 30 秒後重試...")
            time.sleep(30)
        
        print(f"⏰ 等待超時（{max_wait_minutes} 分鐘），部署可能失敗")
        return False
    
    def test_endpoints(self):
        """測試所有端點"""
        endpoints = [
            ("/", "主頁"),
            ("/health", "健康檢查"),
        ]
        
        print("\n🧪 測試所有端點...")
        all_good = True
        
        for endpoint, name in endpoints:
            url = f"{self.service_url}{endpoint}"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {name} ({endpoint}): OK")
                else:
                    print(f"❌ {name} ({endpoint}): HTTP {response.status_code}")
                    all_good = False
            except Exception as e:
                print(f"❌ {name} ({endpoint}): {e}")
                all_good = False
        
        return all_good

def main():
    print("🚀 Railway 部署監控")
    print("=" * 40)
    
    monitor = DeploymentMonitor()
    
    # 檢查當前狀態
    print("1. 檢查當前服務狀態...")
    if monitor.check_service_health():
        monitor.check_service_status()
        monitor.test_endpoints()
        print("\n✅ 服務已正常運行")
    else:
        print("\n⏳ 服務似乎不可用，等待部署完成...")
        success = monitor.wait_for_deployment()
        
        if success:
            print("\n🎉 部署成功！進行最終測試...")
            monitor.test_endpoints()
        else:
            print("\n❌ 部署監控超時，請手動檢查 Railway 控制台")
            print("   URL: https://railway.app/project/...")

if __name__ == "__main__":
    main()