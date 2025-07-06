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
                        embedding VECTOR(1536),
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

    def store_user_profile_name(self, user_id, name):
        """將 user_id 與 name 存成 profile 記憶"""
        print(f"[LOG] 儲存 profile: user_id={user_id}, name={name}")
        if not self._ensure_connection():
            print("❌ [LOG] 無法儲存 profile：Railway pgvector 服務連接失敗")
            return
        embedding = self._get_embedding(name)
        if embedding is None:
            print("❌ [LOG] 無法生成嵌入，profile 未儲存")
            return
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO lumi_memories (user_id, user_message, lumi_response, emotion_tag, embedding)
                    VALUES (%s, %s, %s, %s, %s);
                """, (user_id, f"我是{name}", f"記住用戶名稱：{name}", 'profile', embedding))
                self.conn.commit()
            print(f"✅ [LOG] 已儲存 user_id={user_id} 的 profile name={name}")
        except Exception as e:
            print(f"❌ [LOG] 儲存 profile 失敗: {e}")
            self._ensure_connection()

    def get_user_profile_name(self, user_id):
        """查詢 user_id 最新的 profile name"""
        print(f"\n=== 用戶名稱查詢開始 ===")
        print(f"[用戶名稱] 查詢用戶: {user_id}")
        
        if not self._ensure_connection():
            print("❌ [用戶名稱] 資料庫連接未建立")
            return None
        
        try:
            with self.conn.cursor() as cur:
                print(f"[用戶名稱] 執行 SQL SELECT...")
                cur.execute("""
                    SELECT user_message FROM lumi_memories
                    WHERE user_id = %s AND emotion_tag = 'profile'
                    ORDER BY timestamp DESC LIMIT 1;
                """, (user_id,))
                row = cur.fetchone()
                print(f"[用戶名稱] SQL 查詢完成，結果: {row}")
                
                if row:
                    # user_message 可能是「我是XXX」或「我叫XXX」
                    msg = row[0]
                    print(f"[用戶名稱] 原始訊息: {msg}")
                    
                    for prefix in ["我是", "我叫", "我的名字是"]:
                        if msg.startswith(prefix):
                            name = msg[len(prefix):].strip()
                            print(f"[用戶名稱] 找到名稱: {name}")
                            print(f"=== 用戶名稱查詢結束 ===\n")
                            return name
                    
                    print(f"[用戶名稱] 未找到標準前綴，直接返回: {msg}")
                    print(f"=== 用戶名稱查詢結束 ===\n")
                    return msg
                else:
                    print(f"[用戶名稱] 未找到用戶名稱記錄")
                    print(f"=== 用戶名稱查詢結束 ===\n")
                    return None
        except Exception as e:
            print(f"❌ [用戶名稱] 查詢 profile name 失敗: {e}")
            print(f"=== 用戶名稱查詢結束 ===\n")
            return None

    def store_conversation_memory(self, user_id, user_message, lumi_response, emotion_tag=None):
        print(f"\n=== 記憶儲存開始 ===")
        print(f"[記憶儲存] user_id: {user_id}")
        print(f"[記憶儲存] user_message: {user_message}")
        print(f"[記憶儲存] lumi_response: {lumi_response}")
        print(f"[記憶儲存] emotion_tag: {emotion_tag}")
        
        # 自動偵測 profile 記憶
        for prefix in ["我是", "我叫", "我的名字是"]:
            if isinstance(user_message, str) and user_message.strip().startswith(prefix):
                name = user_message.strip()[len(prefix):].strip()
                if name:
                    print(f"[記憶儲存] 偵測到 profile 記憶: {name}")
                    self.store_user_profile_name(user_id, name)
                    break
        
        if not self._ensure_connection():
            print("❌ [記憶儲存] 無法儲存記憶：Railway pgvector 服務連接失敗")
            return
        
        print(f"[記憶儲存] 開始生成嵌入...")
        embedding = self._get_embedding(user_message)
        if embedding is None:
            print("❌ [記憶儲存] 無法生成嵌入，記憶未儲存")
            return
        
        print(f"[記憶儲存] 嵌入生成成功，長度: {len(embedding)}")
        
        try:
            with self.conn.cursor() as cur:
                print(f"[記憶儲存] 執行 SQL INSERT...")
                cur.execute("""
                    INSERT INTO lumi_memories (user_id, user_message, lumi_response, emotion_tag, embedding)
                    VALUES (%s, %s, %s, %s, %s);
                """, (user_id, user_message, lumi_response, emotion_tag, embedding))
                self.conn.commit()
                print(f"✅ [記憶儲存] 已成功儲存用戶 {user_id[:8]}... 的對話記憶到 Railway pgvector")
        except Exception as e:
            print(f"❌ [記憶儲存] 儲存記憶到 Railway pgvector 失敗: {e}")
            self._ensure_connection()
        
        print(f"=== 記憶儲存結束 ===\n")

    def get_recent_memories(self, user_id, limit=5): # 這裡的 limit 應該是從 PGVector 檢索的數量
        print(f"\n=== 記憶讀取開始 ===")
        print(f"[記憶讀取] 查詢用戶: {user_id}")
        print(f"[記憶讀取] 查詢數量: {limit}")
        
        if not self._ensure_connection():
            print("❌ [記憶讀取] 資料庫連接未建立，無法檢索記憶。")
            return []
        
        try:
            with self.conn.cursor() as cur:
                print(f"[記憶讀取] 執行 SQL SELECT...")
                cur.execute("""
                    SELECT user_message, lumi_response, emotion_tag, timestamp
                    FROM lumi_memories
                    WHERE user_id = %s
                    ORDER BY timestamp DESC
                    LIMIT %s;
                """, (user_id, limit))
                rows = cur.fetchall()
                print(f"[記憶讀取] SQL 查詢完成，找到 {len(rows)} 筆記錄")
                
                memories = []
                for i, row in enumerate(rows):
                    memory = {
                        'user_message': row[0],
                        'lumi_response': row[1],
                        'emotion_tag': row[2],
                        'timestamp': row[3].isoformat() # 轉換為 ISO 格式字串
                    }
                    memories.append(memory)
                    print(f"[記憶讀取] 記錄 {i+1}: {memory}")
                
                # 返回按時間正序排列的記憶，以便於對話上下文的組織
                result = memories[::-1]
                print(f"[記憶讀取] 返回 {len(result)} 筆記憶")
                print(f"=== 記憶讀取結束 ===\n")
                return result
        except Exception as e:
            print(f"❌ [記憶讀取] 從 PGVector 檢索記憶失敗: {e}")
            print(f"=== 記憶讀取結束 ===\n")
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