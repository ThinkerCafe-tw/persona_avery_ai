import os
import json # 暫時保留，可能用於調試或備份，但最終會移除
from datetime import datetime
import psycopg2 # 新增
from pgvector.psycopg2 import register_vector # 新增
import google.generativeai as genai # 新增
import numpy as np # 新增

# 載入環境變數 (確保在 app.py 或其他入口點已載入)
# from dotenv import load_dotenv
# load_dotenv()

class SimpleLumiMemory:
    def __init__(self):
        # 移除檔案記憶相關的初始化
        # persistent_dir = os.getenv('PERSISTENT_STORAGE_PATH', '/app/data')
        # os.makedirs(persistent_dir, exist_ok=True)
        # self.memory_file = os.path.join(persistent_dir, 'lumi_memory.json')
        # self.user_memories = self._load_memories_from_file()

        self.conn = None
        try:
            print("嘗試連接資料庫，DATABASE_URL =", os.getenv('DATABASE_URL'))            
            self.conn = psycopg2.connect(os.getenv('DATABASE_URL'))
            register_vector(self.conn) # 註冊 pgvector 類型
            self._initialize_db()
            print("SimpleLumiMemory: PGVector 記憶系統已初始化並連接資料庫")
        except Exception as e:
            print(f"SimpleLumiMemory: 連接 PGVector 資料庫失敗: {e}")
            # 這裡可以選擇是否要讓應用程式崩潰，或者使用備用記憶方案
            # 目前先讓它打印錯誤，如果沒有資料庫連接，記憶功能將失效

        # 初始化嵌入模型
        try:
            genai.configure(api_key=os.getenv('GEMINI_API_KEY')) # 確保 GEMINI_API_KEY 已設定
            self.embedding_model = genai.GenerativeModel('models/text-embedding-004')
            print("SimpleLumiMemory: 嵌入模型已初始化")
        except Exception as e:
            print(f"SimpleLumiMemory: 嵌入模型初始化失敗: {e}")
            self.embedding_model = None


    def _initialize_db(self):
        with self.conn.cursor() as cur:
            # 啟用 vector 擴展
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            self.conn.commit() # 提交變更

            # 創建記憶資料表
            # embedding 欄位使用 VECTOR(768) 因為 text-embedding-004 的輸出維度是 768
            cur.execute("""
                CREATE TABLE IF NOT EXISTS lumi_memories (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    lumi_response TEXT NOT NULL,
                    emotion_tag TEXT,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    embedding VECTOR(768)
                );
            """)
            self.conn.commit() # 提交變更
            print("SimpleLumiMemory: 資料庫表已檢查/創建")

    # 移除 _load_memories_from_file 和 _save_memories_to_file
    # def _load_memories_from_file(self):
    #     ...
    # def _save_memories_to_file(self):
    #     ...

    def _get_embedding(self, text):
        if not self.embedding_model:
            print("警告: 嵌入模型未初始化，無法生成嵌入。")
            return None
        try:
            # 確保輸入是字串
            if not isinstance(text, str):
                text = str(text)
            
            # 處理空字串情況
            if not text.strip():
                return np.zeros(768).tolist() # 返回一個零向量

            response = self.embedding_model.embed_content(
                model="models/text-embedding-004",
                content=text
            )
            # 確保返回的是 list，以便於 psycopg2 處理
            return response.embedding.tolist()
        except Exception as e:
            print(f"生成嵌入失敗: {e}")
            return None

    def store_conversation_memory(self, user_id, user_message, lumi_response, emotion_tag=None):
        if not self.conn:
            print("警告: 資料庫連接未建立，無法儲存記憶。")
            return

        embedding = self._get_embedding(user_message)
        if embedding is None:
            print("警告: 無法生成嵌入，記憶未儲存。")
            return

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO lumi_memories (user_id, user_message, lumi_response, emotion_tag, embedding)
                    VALUES (%s, %s, %s, %s, %s);
                """, (user_id, user_message, lumi_response, emotion_tag, embedding))
                self.conn.commit()
            print(f"SimpleLumiMemory: 已儲存用戶 {user_id[:8]}... 的對話記憶到 PGVector")
        except Exception as e:
            print(f"SimpleLumiMemory: 儲存記憶到 PGVector 失敗: {e}")

    def get_recent_memories(self, user_id, limit=5): # 這裡的 limit 應該是從 PGVector 檢索的數量
        if not self.conn:
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

    def get_daily_memories(self, user_id, date_str):
        if not self.conn:
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
        if not self.conn:
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
        if not self.conn:
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
