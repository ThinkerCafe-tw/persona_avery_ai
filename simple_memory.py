import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import psycopg2

class SimpleLumiMemory:
    """Lumi記憶系統 - pgvector版本"""
    
    def __init__(self):
        # 使用 Cruz 的 pgvector 資料庫
        self.database_url = os.getenv('DATABASE_URL', "postgresql://postgres:eEUaCXgXacRhvurlWobZDqsYafQJtlCM@postgres.railway.internal:5432/railway")
        self.namespace = "avery"
        
        # 初始化 pgvector 連接
        try:
            self._init_pgvector()
            print("🎯 pgvector 記憶系統已連接 (持久化記憶)")
        except Exception as e:
            print(f"❌ pgvector 連接失敗: {e}")
            raise
    
    def _get_connection(self):
        """獲取資料庫連接"""
        return psycopg2.connect(self.database_url)
    
    def _init_pgvector(self):
        """初始化 pgvector 資料庫表格"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # 創建用戶記憶表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_memories (
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
                    CREATE TABLE IF NOT EXISTS conversations (
                        id SERIAL PRIMARY KEY,
                        namespace VARCHAR(50) NOT NULL,
                        user_id VARCHAR(255) NOT NULL,
                        user_message TEXT NOT NULL,
                        ai_response TEXT NOT NULL,
                        emotion_tag VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # 創建索引
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_user_memories_namespace_user 
                    ON user_memories(namespace, user_id);
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_conversations_namespace_user 
                    ON conversations(namespace, user_id);
                """)
                
                conn.commit()
    
    def get_user_info(self, user_id: str) -> Dict:
        """獲取用戶資訊"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT memory_key, memory_value 
                        FROM user_memories 
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
                        UPDATE user_memories 
                        SET memory_value = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE namespace = %s AND user_id = %s AND memory_key = %s
                    """, (value, self.namespace, user_id, key))
                    
                    # 如果沒有更新任何行，則插入新記錄
                    if cur.rowcount == 0:
                        cur.execute("""
                            INSERT INTO user_memories (namespace, user_id, memory_key, memory_value)
                            VALUES (%s, %s, %s, %s)
                        """, (self.namespace, user_id, key, value))
                    
                    conn.commit()
        except Exception as e:
            print(f"❌ 儲存用戶資訊失敗: {e}")
    
    def add_interaction(self, user_id: str, user_message: str, ai_response: str, emotion_tag: str = 'neutral'):
        """添加對話記錄"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO conversations (namespace, user_id, user_message, ai_response, emotion_tag)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (self.namespace, user_id, user_message, ai_response, emotion_tag))
                    
                    conn.commit()
                    
                    # 自動提取用戶資訊
                    self._extract_user_info(user_id, user_message)
                    
        except Exception as e:
            print(f"❌ 記錄對話失敗: {e}")
    
    def _extract_user_info(self, user_id: str, message: str):
        """從訊息中自動提取用戶資訊"""
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
                        SELECT user_message, ai_response, emotion_tag, created_at
                        FROM conversations 
                        WHERE namespace = %s AND user_id = %s
                        ORDER BY created_at DESC
                        LIMIT %s
                    """, (self.namespace, user_id, limit))
                    
                    results = []
                    for row in cur.fetchall():
                        user_msg, ai_resp, emotion_tag, created_at = row
                        results.append({
                            "user_message": user_msg,
                            "lumi_response": ai_resp,
                            "emotion_tag": emotion_tag,
                            "created_at": created_at
                        })
                    
                    return results
        except Exception as e:
            print(f"❌ 獲取對話記錄失敗: {e}")
            return []
    
    def search_memories_by_emotion(self, user_id: str, emotion_tag: str, limit: int = 3) -> List[Dict]:
        """根據情緒標籤搜索記憶"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT user_message, ai_response, created_at
                        FROM conversations 
                        WHERE namespace = %s AND user_id = %s AND emotion_tag = %s
                        ORDER BY created_at DESC
                        LIMIT %s
                    """, (self.namespace, user_id, emotion_tag, limit))
                    
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
            print(f"❌ 搜索記憶失敗: {e}")
            return []
    
    def get_memory_summary(self, user_id: str) -> Dict:
        """取得用戶記憶摘要"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # 總對話數
                    cur.execute("""
                        SELECT COUNT(*) FROM conversations 
                        WHERE namespace = %s AND user_id = %s
                    """, (self.namespace, user_id))
                    total_memories = cur.fetchone()[0]
                    
                    # 情緒分布
                    cur.execute("""
                        SELECT emotion_tag, COUNT(*) 
                        FROM conversations 
                        WHERE namespace = %s AND user_id = %s
                        GROUP BY emotion_tag
                    """, (self.namespace, user_id))
                    
                    by_emotion = {}
                    for row in cur.fetchall():
                        emotion, count = row
                        by_emotion[emotion or 'neutral'] = count
                    
                    # 最近7天活躍度
                    cur.execute("""
                        SELECT COUNT(*) FROM conversations 
                        WHERE namespace = %s AND user_id = %s 
                        AND created_at >= NOW() - INTERVAL '7 days'
                    """, (self.namespace, user_id))
                    recent_activity = cur.fetchone()[0]
                    
                    return {
                        'total_memories': total_memories,
                        'by_emotion': by_emotion,
                        'recent_activity': recent_activity
                    }
        except Exception as e:
            print(f"❌ 獲取記憶摘要失敗: {e}")
            return {
                'total_memories': 0,
                'by_emotion': {},
                'recent_activity': 0
            }
    
    def get_user_emotion_patterns(self, user_id: str, days: int = 30) -> Dict:
        """分析用戶情緒模式"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT emotion_tag, COUNT(*) 
                        FROM conversations 
                        WHERE namespace = %s AND user_id = %s 
                        AND created_at >= NOW() - INTERVAL '%s days'
                        GROUP BY emotion_tag
                    """, (self.namespace, user_id, days))
                    
                    emotion_distribution = {}
                    total_interactions = 0
                    
                    for row in cur.fetchall():
                        emotion, count = row
                        emotion = emotion or 'neutral'
                        emotion_distribution[emotion] = count
                        total_interactions += count
                    
                    dominant_emotion = 'neutral'
                    if emotion_distribution:
                        dominant_emotion = max(emotion_distribution.items(), key=lambda x: x[1])[0]
                    
                    return {
                        'emotion_distribution': emotion_distribution,
                        'total_interactions': total_interactions,
                        'dominant_emotion': dominant_emotion
                    }
        except Exception as e:
            print(f"❌ 分析情緒模式失敗: {e}")
            return {
                'emotion_distribution': {},
                'total_interactions': 0,
                'dominant_emotion': 'neutral'
            }
    
    def get_context_for_response(self, user_id: str, current_message: str, emotion_tag: str) -> str:
        """為回應生成上下文"""
        # 取得相同情緒的歷史記憶
        emotion_memories = self.search_memories_by_emotion(user_id, emotion_tag, 2)
        
        if not emotion_memories:
            return ""
        
        context = "之前我們聊過的相關話題：\n"
        for memory in emotion_memories:
            context += f"- {memory['user_message'][:50]}...\n"
        
        return context
    
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
        memory = SimpleLumiMemory()
        
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