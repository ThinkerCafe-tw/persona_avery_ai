#!/usr/bin/env python3
"""
🧠 Avery 記憶系統 - 參考 Cruz 的 pgvector 實現
使用連接池和健壯的錯誤處理
"""

import os
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import contextmanager

# 嘗試導入 pgvector 相關模組
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from psycopg2.pool import SimpleConnectionPool
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleLumiMemory:
    """Lumi記憶系統 - 參考 Cruz 的 pgvector 實現"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.namespace = "avery"
        self.pool = None
        self.use_pgvector = False
        
        # 初始化記憶系統
        self._initialize_memory_system()
    
    def _initialize_memory_system(self):
        """初始化記憶系統（pgvector 或內存備用）"""
        if PGVECTOR_AVAILABLE and self.database_url:
            try:
                # 參考 Cruz 的連接池配置
                self.pool = SimpleConnectionPool(
                    1, 10,  # min/max connections
                    self.database_url
                )
                self._initialize_database()
                self.use_pgvector = True
                logger.info("🎯 pgvector 記憶系統已連接 (持久化記憶)")
            except Exception as e:
                logger.error(f"pgvector 初始化失敗: {e}")
                logger.info("🔄 降級到內存記憶模式")
                self._initialize_memory_fallback()
        else:
            logger.warning("pgvector 不可用，使用內存記憶模式")
            self._initialize_memory_fallback()
    
    def _initialize_memory_fallback(self):
        """初始化內存備用記憶系統"""
        self.memory_store = {}  # 用戶資訊存儲
        self.conversations = {}  # 對話記錄存儲
        self.use_pgvector = False
    
    @contextmanager
    def get_connection(self):
        """獲取資料庫連接（參考 Cruz 的方法）"""
        if not self.use_pgvector or not self.pool:
            raise ValueError("pgvector 不可用")
        
        connection = None
        try:
            connection = self.pool.getconn()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"資料庫操作錯誤: {e}")
            raise
        finally:
            if connection:
                self.pool.putconn(connection)
    
    def _initialize_database(self):
        """初始化資料庫表格（參考 Cruz 的結構）"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # 啟用 pgvector 擴展
                    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                    
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
                    logger.info("資料庫表格初始化完成")
        except Exception as e:
            logger.error(f"資料庫初始化失敗: {e}")
            raise
    
    def get_user_info(self, user_id: str) -> Dict:
        """獲取用戶資訊"""
        if self.use_pgvector:
            try:
                with self.get_connection() as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cur:
                        cur.execute("""
                            SELECT memory_key, memory_value 
                            FROM user_memories 
                            WHERE namespace = %s AND user_id = %s
                        """, (self.namespace, user_id))
                        
                        result = {}
                        for row in cur.fetchall():
                            result[row['memory_key']] = row['memory_value']
                        
                        return result
            except Exception as e:
                logger.error(f"獲取用戶資訊失敗: {e}")
                return {}
        else:
            # 內存模式
            return self.memory_store.get(user_id, {})
    
    def set_user_info(self, user_id: str, key: str, value: str):
        """設定用戶資訊"""
        if self.use_pgvector:
            try:
                with self.get_connection() as conn:
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
                logger.error(f"設定用戶資訊失敗: {e}")
        else:
            # 內存模式
            if user_id not in self.memory_store:
                self.memory_store[user_id] = {}
            self.memory_store[user_id][key] = value
    
    def add_interaction(self, user_id: str, user_message: str, ai_response: str, emotion_tag: str = 'neutral'):
        """添加對話記錄"""
        if self.use_pgvector:
            try:
                with self.get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO conversations (namespace, user_id, user_message, ai_response, emotion_tag)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (self.namespace, user_id, user_message, ai_response, emotion_tag))
                        
                        conn.commit()
                        
                        # 自動提取用戶資訊
                        self._extract_user_info(user_id, user_message)
                        
            except Exception as e:
                logger.error(f"記錄對話失敗: {e}")
        else:
            # 內存模式
            if user_id not in self.conversations:
                self.conversations[user_id] = []
            
            conversation = {
                'user_message': user_message,
                'lumi_response': ai_response,
                'emotion_tag': emotion_tag,
                'created_at': datetime.now().isoformat()
            }
            
            self.conversations[user_id].append(conversation)
            
            # 限制記憶數量
            if len(self.conversations[user_id]) > 50:
                self.conversations[user_id] = self.conversations[user_id][-50:]
            
            # 自動提取用戶資訊
            self._extract_user_info(user_id, user_message)
    
    def _extract_user_info(self, user_id: str, message: str):
        """從訊息中自動提取用戶資訊"""
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
        if self.use_pgvector:
            try:
                with self.get_connection() as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cur:
                        cur.execute("""
                            SELECT user_message, ai_response, emotion_tag, created_at
                            FROM conversations 
                            WHERE namespace = %s AND user_id = %s
                            ORDER BY created_at DESC
                            LIMIT %s
                        """, (self.namespace, user_id, limit))
                        
                        results = []
                        for row in cur.fetchall():
                            results.append({
                                "user_message": row['user_message'],
                                "lumi_response": row['ai_response'],
                                "emotion_tag": row['emotion_tag'],
                                "created_at": row['created_at']
                            })
                        
                        return results
            except Exception as e:
                logger.error(f"獲取對話記錄失敗: {e}")
                return []
        else:
            # 內存模式
            if user_id not in self.conversations:
                return []
            
            user_convs = self.conversations[user_id]
            return user_convs[-limit:] if len(user_convs) >= limit else user_convs
    
    def search_memories_by_emotion(self, user_id: str, emotion_tag: str, limit: int = 3) -> List[Dict]:
        """根據情緒標籤搜索記憶"""
        if self.use_pgvector:
            try:
                with self.get_connection() as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cur:
                        cur.execute("""
                            SELECT user_message, ai_response, created_at
                            FROM conversations 
                            WHERE namespace = %s AND user_id = %s AND emotion_tag = %s
                            ORDER BY created_at DESC
                            LIMIT %s
                        """, (self.namespace, user_id, emotion_tag, limit))
                        
                        results = []
                        for row in cur.fetchall():
                            results.append({
                                "user_message": row['user_message'],
                                "lumi_response": row['ai_response'],
                                "created_at": row['created_at']
                            })
                        
                        return results
            except Exception as e:
                logger.error(f"搜索記憶失敗: {e}")
                return []
        else:
            # 內存模式
            if user_id not in self.conversations:
                return []
            
            matching = [conv for conv in self.conversations[user_id] 
                       if conv.get('emotion_tag') == emotion_tag]
            return matching[-limit:] if len(matching) >= limit else matching
    
    def get_memory_summary(self, user_id: str) -> Dict:
        """取得用戶記憶摘要"""
        if self.use_pgvector:
            try:
                with self.get_connection() as conn:
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
                logger.error(f"獲取記憶摘要失敗: {e}")
                return {
                    'total_memories': 0,
                    'by_emotion': {},
                    'recent_activity': 0
                }
        else:
            # 內存模式
            if user_id not in self.conversations:
                return {
                    'total_memories': 0,
                    'by_emotion': {},
                    'recent_activity': 0
                }
            
            user_convs = self.conversations[user_id]
            emotion_count = {}
            
            for conv in user_convs:
                emotion = conv.get('emotion_tag', 'neutral')
                emotion_count[emotion] = emotion_count.get(emotion, 0) + 1
            
            return {
                'total_memories': len(user_convs),
                'by_emotion': emotion_count,
                'recent_activity': len(user_convs)
            }
    
    def get_user_emotion_patterns(self, user_id: str, days: int = 30) -> Dict:
        """分析用戶情緒模式"""
        # 內存和 pgvector 版本類似，簡化實現
        summary = self.get_memory_summary(user_id)
        
        dominant_emotion = 'neutral'
        if summary['by_emotion']:
            dominant_emotion = max(summary['by_emotion'].items(), key=lambda x: x[1])[0]
        
        return {
            'emotion_distribution': summary['by_emotion'],
            'total_interactions': summary['total_memories'],
            'dominant_emotion': dominant_emotion
        }
    
    def get_context_for_response(self, user_id: str, current_message: str, emotion_tag: str) -> str:
        """為回應生成上下文"""
        emotion_memories = self.search_memories_by_emotion(user_id, emotion_tag, 2)
        
        if not emotion_memories:
            return ""
        
        context = "之前我們聊過的相關話題：\n"
        for memory in emotion_memories:
            context += f"- {memory['user_message'][:50]}...\n"
        
        return context
    
    def test_connection(self):
        """測試記憶系統連接"""
        if self.use_pgvector:
            try:
                with self.get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1")
                        result = cur.fetchone()
                        return result[0] == 1
            except Exception as e:
                logger.error(f"連接測試失敗: {e}")
                return False
        else:
            return True

if __name__ == "__main__":
    # 測試
    print("🧪 測試 Avery 記憶系統...")
    
    try:
        memory = SimpleLumiMemory()
        
        # 測試連接
        if memory.test_connection():
            print("✅ 記憶系統連接正常")
        else:
            print("❌ 記憶系統連接失敗")
        
        # 測試基本功能
        memory.add_interaction("test_user", "我叫小明", "你好小明！", "friend")
        user_info = memory.get_user_info("test_user")
        recent = memory.get_recent_memories("test_user")
        
        print(f"✅ 用戶資訊: {user_info}")
        print(f"✅ 最近記憶: {len(recent)} 條")
        print("🎉 記憶系統準備就緒！")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()