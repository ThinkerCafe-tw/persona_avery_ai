import os
import json
from datetime import datetime
import psycopg2
from pgvector.psycopg2 import register_vector
import numpy as np
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

class SimpleLumiMemory:
    def __init__(self):
        self.conn = None
        self._initialize_railway_pgvector()
        # 移除 self.embedding_model 相關程式碼
        print("SimpleLumiMemory: 初始化完成")

    def _initialize_railway_pgvector(self):
        """初始化 Railway pgvector 服務連接"""
        try:
            # 從 Railway 環境變數獲取連接字串
            database_url = os.getenv('DATABASE_URL')
            print(f"[LOG] DATABASE_URL: {database_url}")
            
            if not database_url:
                print("❌ [LOG] 未找到 DATABASE_URL 環境變數")
                print("請確保在 Railway 中正確配置了 pgvector 服務")
                return
            
            print(f"[LOG] 正在連接 Railway pgvector 服務... {database_url[:50]}...")
            
            # 建立連接
            self.conn = psycopg2.connect(database_url)
            
            # 註冊 pgvector 擴展
            register_vector(self.conn)
            
            # 初始化資料庫結構
            self._initialize_db()
            
            print("✅ [LOG] Railway pgvector 服務連接成功！")
            
        except Exception as e:
            print(f"❌ [LOG] Railway pgvector 服務連接失敗: {e}")
            print("請檢查：")
            print("1. Railway 專案中是否已添加 pgvector 服務")
            print("2. DATABASE_URL 環境變數是否正確設定")
            print("3. 網路連接是否正常")
            self.conn = None

    def _initialize_db(self):
        """初始化 Railway pgvector 資料庫結構"""
        if not self.conn:
            print("❌ [LOG] 無法初始化資料庫結構，未連接資料庫")
            return
            
        try:
            with self.conn.cursor() as cur:
                # Railway pgvector 服務已經預裝了 vector 擴展，但我們還是確保它存在
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                self.conn.commit()
                
                # 創建記憶資料表（Railway pgvector 優化版本）
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS lumi_memories (
                        id SERIAL PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        user_message TEXT NOT NULL,
                        lumi_response TEXT NOT NULL,
                        emotion_tag TEXT,
                        timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        embedding VECTOR(768),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # 創建索引以優化查詢效能
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_lumi_memories_user_id 
                    ON lumi_memories(user_id);
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_lumi_memories_timestamp 
                    ON lumi_memories(timestamp DESC);
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_lumi_memories_emotion_tag 
                    ON lumi_memories(emotion_tag) WHERE emotion_tag IS NOT NULL;
                """)
                
                self.conn.commit()
                print("✅ [LOG] Railway pgvector 資料庫結構初始化完成")
                
        except Exception as e:
            print(f"❌ [LOG] Railway pgvector 資料庫初始化失敗: {e}")
            self.conn = None

    def _get_embedding(self, text):
        """使用 OpenAI 生成文本嵌入"""
        print(f"[LOG] 生成嵌入 for text: {text}")
        try:
            if not isinstance(text, str):
                text = str(text)
            if not text.strip():
                return np.zeros(1536).tolist()  # OpenAI ada-002 是 1536 維
            result = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            print(f"[LOG] 嵌入生成成功，長度: {len(result['data'][0]['embedding'])}")
            return result['data'][0]['embedding']
        except Exception as e:
            print(f"❌ [LOG] 生成嵌入失敗: {e}")
            return None

    def _ensure_connection(self):
        """確保資料庫連接正常"""
        if not self.conn:
            print("❌ [LOG] 資料庫連接未建立")
            return False
        
        try:
            # 測試連接
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
            print("[LOG] 資料庫連接測試成功")
            return True
        except Exception as e:
            print(f"❌ [LOG] 資料庫連接測試失敗: {e}")
            # 嘗試重新連接
            try:
                self._initialize_railway_pgvector()
                return self.conn is not None
            except:
                return False

    def store_conversation_memory(self, user_id, user_message, lumi_response, emotion_tag=None):
        print(f"[LOG] 儲存記憶: user_id={user_id}, user_message={user_message}, lumi_response={lumi_response}, emotion_tag={emotion_tag}")
        if not self._ensure_connection():
            print("❌ [LOG] 無法儲存記憶：Railway pgvector 服務連接失敗")
            return

        embedding = self._get_embedding(user_message)
        if embedding is None:
            print("❌ [LOG] 無法生成嵌入，記憶未儲存")
            return

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO lumi_memories (user_id, user_message, lumi_response, emotion_tag, embedding)
                    VALUES (%s, %s, %s, %s, %s);
                """, (user_id, user_message, lumi_response, emotion_tag, embedding))
                self.conn.commit()
            print(f"✅ [LOG] 已儲存用戶 {user_id[:8]}... 的對話記憶到 Railway pgvector")
        except Exception as e:
            print(f"❌ [LOG] 儲存記憶到 Railway pgvector 失敗: {e}")
            # 嘗試重新連接
            self._ensure_connection()

    def get_recent_memories(self, user_id, limit=5): # 這裡的 limit 應該是從 PGVector 檢索的數量
        if not self._ensure_connection():
            print("警告: 資料庫連接未建立，無法檢索記憶。")
            return []
        
        # 這裡的「recent」可以有多種定義：
        # 1. 簡單地按時間排序取最近的
        # 2. 根據當前用戶的訊息進行相似度搜尋
        # 為了簡化，我們暫時先實現按時間排序取最近的。
        # 如果需要相似度搜尋，get_recent_memories 需要接收一個 query_message 參數。

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT user_message, lumi_response, emotion_tag, timestamp
                    FROM lumi_memories
                    WHERE user_id = %s
                    ORDER BY timestamp DESC
                    LIMIT %s;
                """, (user_id, limit))
                rows = cur.fetchall()
                
                memories = []
                for row in rows:
                    memories.append({
                        'user_message': row[0],
                        'lumi_response': row[1],
                        'emotion_tag': row[2],
                        'timestamp': row[3].isoformat() # 轉換為 ISO 格式字串
                    })
                # 返回按時間正序排列的記憶，以便於對話上下文的組織
                return memories[::-1] 
        except Exception as e:
            print(f"SimpleLumiMemory: 從 PGVector 檢索記憶失敗: {e}")
            return []

    def get_similar_memories(self, user_id, query_message, limit=5, similarity_threshold=0.7):
        """根據相似度搜尋相關記憶"""
        if not self._ensure_connection():
            print("警告: 資料庫連接未建立，無法進行相似度搜尋。")
            return []
        
        query_embedding = self._get_embedding(query_message)
        if query_embedding is None:
            print("警告: 無法生成查詢嵌入，使用時間排序檢索。")
            return self.get_recent_memories(user_id, limit)
        
        try:
            with self.conn.cursor() as cur:
                # 使用餘弦相似度搜尋最相關的記憶
                cur.execute("""
                    SELECT user_message, lumi_response, emotion_tag, timestamp,
                           1 - (embedding <=> %s) as similarity
                    FROM lumi_memories
                    WHERE user_id = %s
                    AND 1 - (embedding <=> %s) > %s
                    ORDER BY embedding <=> %s
                    LIMIT %s;
                """, (query_embedding, user_id, query_embedding, similarity_threshold, query_embedding, limit))
                rows = cur.fetchall()
                
                memories = []
                for row in rows:
                    memories.append({
                        'user_message': row[0],
                        'lumi_response': row[1],
                        'emotion_tag': row[2],
                        'timestamp': row[3].isoformat(),
                        'similarity': float(row[4])
                    })
                return memories
        except Exception as e:
            print(f"SimpleLumiMemory: 相似度搜尋失敗: {e}")
            return self.get_recent_memories(user_id, limit)

    def get_user_profile_memories(self, user_id, limit=10):
        """獲取用戶個人資料相關的記憶（偏好、習慣、重要事件等）"""
        if not self._ensure_connection():
            print("警告: 資料庫連接未建立，無法獲取用戶資料記憶。")
            return []
        
        # 定義個人資料相關的關鍵詞
        profile_keywords = [
            '喜歡', '討厭', '習慣', '工作', '學校', '家人', '朋友', '興趣', '愛好',
            '生日', '年齡', '住址', '電話', 'email', '職業', '學歷', '夢想', '目標',
            '害怕', '擔心', '開心', '難過', '壓力', '放鬆', '運動', '音樂', '電影',
            '食物', '顏色', '動物', '地方', '旅行', '學習', '技能', '成就', '挫折'
        ]
        
        try:
            with self.conn.cursor() as cur:
                # 搜尋包含個人資料關鍵詞的記憶
                keyword_conditions = " OR ".join([f"user_message ILIKE '%{keyword}%'" for keyword in profile_keywords])
                cur.execute(f"""
                    SELECT user_message, lumi_response, emotion_tag, timestamp
                    FROM lumi_memories
                    WHERE user_id = %s AND ({keyword_conditions})
                    ORDER BY timestamp DESC
                    LIMIT %s;
                """, (user_id, limit))
                rows = cur.fetchall()
                
                memories = []
                for row in rows:
                    memories.append({
                        'user_message': row[0],
                        'lumi_response': row[1],
                        'emotion_tag': row[2],
                        'timestamp': row[3].isoformat()
                    })
                return memories
        except Exception as e:
            print(f"SimpleLumiMemory: 獲取用戶資料記憶失敗: {e}")
            return []

    def get_emotional_memories(self, user_id, emotion_type=None, limit=5):
        """獲取特定情緒類型的記憶"""
        if not self._ensure_connection():
            print("警告: 資料庫連接未建立，無法獲取情緒記憶。")
            return []
        
        try:
            with self.conn.cursor() as cur:
                if emotion_type:
                    cur.execute("""
                        SELECT user_message, lumi_response, emotion_tag, timestamp
                        FROM lumi_memories
                        WHERE user_id = %s AND emotion_tag = %s
                        ORDER BY timestamp DESC
                        LIMIT %s;
                    """, (user_id, emotion_type, limit))
                else:
                    cur.execute("""
                        SELECT user_message, lumi_response, emotion_tag, timestamp
                        FROM lumi_memories
                        WHERE user_id = %s AND emotion_tag IS NOT NULL
                        ORDER BY timestamp DESC
                        LIMIT %s;
                    """, (user_id, limit))
                
                rows = cur.fetchall()
                memories = []
                for row in rows:
                    memories.append({
                        'user_message': row[0],
                        'lumi_response': row[1],
                        'emotion_tag': row[2],
                        'timestamp': row[3].isoformat()
                    })
                return memories
        except Exception as e:
            print(f"SimpleLumiMemory: 獲取情緒記憶失敗: {e}")
            return []

    def get_long_term_memories(self, user_id, days_back=30, limit=20):
        """獲取長期記憶（指定天數內的重要記憶）"""
        if not self._ensure_connection():
            print("警告: 資料庫連接未建立，無法獲取長期記憶。")
            return []
        
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT user_message, lumi_response, emotion_tag, timestamp
                    FROM lumi_memories
                    WHERE user_id = %s 
                    AND timestamp >= NOW() - INTERVAL '%s days'
                    ORDER BY timestamp DESC
                    LIMIT %s;
                """, (user_id, days_back, limit))
                rows = cur.fetchall()
                
                memories = []
                for row in rows:
                    memories.append({
                        'user_message': row[0],
                        'lumi_response': row[1],
                        'emotion_tag': row[2],
                        'timestamp': row[3].isoformat()
                    })
                return memories
        except Exception as e:
            print(f"SimpleLumiMemory: 獲取長期記憶失敗: {e}")
            return []

    def get_memory_statistics(self, user_id):
        """獲取用戶記憶統計資訊"""
        if not self._ensure_connection():
            print("警告: 資料庫連接未建立，無法獲取記憶統計。")
            return {}
        
        try:
            with self.conn.cursor() as cur:
                # 總對話數
                cur.execute("SELECT COUNT(*) FROM lumi_memories WHERE user_id = %s", (user_id,))
                total_conversations = cur.fetchone()[0]
                
                # 情緒分布
                cur.execute("""
                    SELECT emotion_tag, COUNT(*) 
                    FROM lumi_memories 
                    WHERE user_id = %s AND emotion_tag IS NOT NULL 
                    GROUP BY emotion_tag
                    ORDER BY COUNT(*) DESC
                """, (user_id,))
                emotion_distribution = dict(cur.fetchall())
                
                # 最近互動時間
                cur.execute("SELECT MAX(timestamp) FROM lumi_memories WHERE user_id = %s", (user_id,))
                last_interaction = cur.fetchone()[0]
                
                # 互動頻率（最近7天）
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM lumi_memories 
                    WHERE user_id = %s 
                    AND timestamp >= NOW() - INTERVAL '7 days'
                """, (user_id,))
                weekly_interactions = cur.fetchone()[0]
                
                return {
                    'total_conversations': total_conversations,
                    'emotion_distribution': emotion_distribution,
                    'last_interaction': last_interaction.isoformat() if last_interaction else None,
                    'weekly_interactions': weekly_interactions,
                    'memory_strength': 'strong' if total_conversations > 50 else 'medium' if total_conversations > 20 else 'weak'
                }
        except Exception as e:
            print(f"SimpleLumiMemory: 獲取記憶統計失敗: {e}")
            return {}

    def get_daily_memories(self, user_id, date_str):
        if not self._ensure_connection():
            print("警告: 資料庫連接未建立，無法檢索每日記憶。")
            return []
        
        try:
            with self.conn.cursor() as cur:
                # 查詢特定用戶在特定日期的所有對話記錄
                cur.execute("""
                    SELECT user_message, lumi_response, emotion_tag, timestamp
                    FROM lumi_memories
                    WHERE user_id = %s AND DATE(timestamp) = %s
                    ORDER BY timestamp ASC;
                """, (user_id, date_str))
                rows = cur.fetchall()
                
                memories = []
                for row in rows:
                    memories.append({
                        'user_message': row[0],
                        'lumi_response': row[1],
                        'emotion_tag': row[2],
                        'timestamp': row[3].isoformat()
                    })
                return memories
        except Exception as e:
            print(f"SimpleLumiMemory: 從 PGVector 檢索每日記憶失敗: {e}")
            return []

    def get_memory_summary(self, user_id):
        if not self._ensure_connection():
            print("警告: 資料庫連接未建立，無法獲取記憶摘要。")
            return {'total_memories': 0, 'last_interaction': 'N/A'}
        
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*), MAX(timestamp)
                    FROM lumi_memories
                    WHERE user_id = %s;
                """, (user_id,))
                count, last_ts = cur.fetchone()
                
                return {
                    'total_memories': count if count else 0,
                    'last_interaction': last_ts.isoformat() if last_ts else 'N/A'
                }
        except Exception as e:
            print(f"SimpleLumiMemory: 從 PGVector 獲取記憶摘要失敗: {e}")
            return {'total_memories': 0, 'last_interaction': 'N/A'}

    def get_user_emotion_patterns(self, user_id):
        if not self._ensure_connection():
            print("警告: 資料庫連接未建立，無法獲取情緒模式。")
            return {'dominant_emotion': 'friend', 'total_interactions': 0}

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT emotion_tag, COUNT(*)
                    FROM lumi_memories
                    WHERE user_id = %s AND emotion_tag IS NOT NULL
                    GROUP BY emotion_tag
                    ORDER BY COUNT(*) DESC
                    LIMIT 1;
                """, (user_id,))
                dominant_row = cur.fetchone()

                cur.execute("""
                    SELECT COUNT(*)
                    FROM lumi_memories
                    WHERE user_id = %s;
                """, (user_id,))
                total_interactions = cur.fetchone()[0]

                dominant_emotion = dominant_row[0] if dominant_row else 'friend'
                return {
                    'dominant_emotion': dominant_emotion,
                    'total_interactions': total_interactions if total_interactions else 0
                }
        except Exception as e:
            print(f"SimpleLumiMemory: 從 PGVector 獲取情緒模式失敗: {e}")
            return {'dominant_emotion': 'friend', 'total_interactions': 0}