#!/usr/bin/env python3
"""
🧠 簡單 pgvector 記憶系統 - 使用 Cruz 的資料庫
先測試基本功能，不搞複雜的
"""

import os
import json
import psycopg2
from datetime import datetime
from typing import List, Dict, Optional

class SimplePgVectorMemory:
    """簡單的 pgvector 記憶系統"""
    
    def __init__(self):
        # 使用 Cruz 提供的資料庫 URL
        self.database_url = "postgresql://postgres:eEUaCXgXacRhvurlWobZDqsYafQJtlCM@postgres.railway.internal:5432/railway"
        self.namespace = "avery"  # Avery 的命名空間
        
        # 測試連接
        try:
            self._init_database()
            print(f"✅ pgvector 記憶系統已連接 (namespace: {self.namespace})")
        except Exception as e:
            print(f"❌ pgvector 連接失敗: {e}")
            raise
    
    def _get_connection(self):
        """獲取資料庫連接"""
        return psycopg2.connect(self.database_url)
    
    def _init_database(self):
        """初始化資料庫表格 (簡單版本)"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # 創建簡單的記憶表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS simple_memories (
                        id SERIAL PRIMARY KEY,
                        namespace VARCHAR(50) NOT NULL,
                        user_id VARCHAR(255) NOT NULL,
                        memory_key VARCHAR(100),
                        memory_value TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # 創建對話記錄表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS simple_conversations (
                        id SERIAL PRIMARY KEY,
                        namespace VARCHAR(50) NOT NULL,
                        user_id VARCHAR(255) NOT NULL,
                        user_message TEXT NOT NULL,
                        ai_response TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # 創建索引
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_simple_memories_namespace_user 
                    ON simple_memories(namespace, user_id);
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_simple_conversations_namespace_user 
                    ON simple_conversations(namespace, user_id);
                """)
                
                conn.commit()
    
    def get_user_info(self, user_id: str) -> Dict:
        """獲取用戶資訊"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT memory_key, memory_value 
                        FROM simple_memories 
                        WHERE namespace = %s AND user_id = %s
                    """, (self.namespace, user_id))
                    
                    result = {}
                    for row in cur.fetchall():
                        key, value = row
                        result[key] = value
                    
                    return result
        except Exception as e:
            print(f"❌ 獲取用戶資訊失敗: {e}")
            return {}
    
    def set_user_info(self, user_id: str, key: str, value: str):
        """設定用戶資訊"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # 先嘗試更新
                    cur.execute("""
                        UPDATE simple_memories 
                        SET memory_value = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE namespace = %s AND user_id = %s AND memory_key = %s
                    """, (value, self.namespace, user_id, key))
                    
                    # 如果沒有更新任何行，則插入新記錄
                    if cur.rowcount == 0:
                        cur.execute("""
                            INSERT INTO simple_memories (namespace, user_id, memory_key, memory_value)
                            VALUES (%s, %s, %s, %s)
                        """, (self.namespace, user_id, key, value))
                    
                    conn.commit()
                    print(f"💾 已儲存: {user_id} -> {key}: {value}")
        except Exception as e:
            print(f"❌ 儲存用戶資訊失敗: {e}")
    
    def add_interaction(self, user_id: str, user_message: str, ai_response: str):
        """添加對話記錄"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO simple_conversations (namespace, user_id, user_message, ai_response)
                        VALUES (%s, %s, %s, %s)
                    """, (self.namespace, user_id, user_message, ai_response))
                    
                    conn.commit()
                    print(f"💬 已記錄對話: {user_id}")
                    
                    # 自動提取用戶資訊
                    self._extract_user_info(user_id, user_message)
                    
        except Exception as e:
            print(f"❌ 記錄對話失敗: {e}")
    
    def _extract_user_info(self, user_id: str, message: str):
        """從訊息中自動提取用戶資訊"""
        message_lower = message.lower()
        
        # 簡單的名字識別
        if "我叫" in message or "我是" in message:
            if "我叫" in message:
                parts = message.split("我叫")[1].split("，")[0].split(",")[0].strip()
                if parts:
                    self.set_user_info(user_id, "name", parts)
            
            if "工程師" in message:
                self.set_user_info(user_id, "job", "工程師")
            elif "設計師" in message:
                self.set_user_info(user_id, "job", "設計師")
            elif "學生" in message:
                self.set_user_info(user_id, "job", "學生")
    
    def get_recent_memories(self, user_id: str, limit: int = 3) -> List[Dict]:
        """獲取最近的對話記錄"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT user_message, ai_response, created_at
                        FROM simple_conversations 
                        WHERE namespace = %s AND user_id = %s
                        ORDER BY created_at DESC
                        LIMIT %s
                    """, (self.namespace, user_id, limit))
                    
                    results = []
                    for row in cur.fetchall():
                        user_msg, ai_resp, created_at = row
                        results.append({
                            "user_message": user_msg,
                            "lumi_response": ai_resp,
                            "created_at": created_at
                        })
                    
                    return results
        except Exception as e:
            print(f"❌ 獲取對話記錄失敗: {e}")
            return []
    
    def test_connection(self):
        """測試資料庫連接"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    result = cur.fetchone()
                    return result[0] == 1
        except Exception as e:
            print(f"❌ 連接測試失敗: {e}")
            return False

if __name__ == "__main__":
    # 測試
    print("🧪 測試 pgvector 記憶系統...")
    
    try:
        memory = SimplePgVectorMemory()
        
        # 測試連接
        if memory.test_connection():
            print("✅ 資料庫連接正常")
        else:
            print("❌ 資料庫連接失敗")
            
        print("🎉 pgvector 記憶系統準備就緒！")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()