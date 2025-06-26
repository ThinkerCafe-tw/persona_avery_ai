import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib

# 簡化版記憶管理器，移除Chroma依賴以避免部署問題
# 實際部署時可考慮使用更輕量的向量存儲方案

class LumiMemoryManager:
    """Lumi 量子記憶系統管理器"""
    
    def __init__(self):
        # 初始化Chroma客戶端
        self.chroma_client = chromadb.Client()
        
        # 建立記憶集合
        self.collections = {
            'personality': self._get_or_create_collection('lumi_personality_memories'),
            'emotion': self._get_or_create_collection('lumi_emotion_memories'),
            'knowledge': self._get_or_create_collection('lumi_knowledge_memories'),
            'conversation': self._get_or_create_collection('lumi_conversation_memories')
        }
        
        # 配置Gemini Embedding
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
    def _get_or_create_collection(self, name: str):
        """取得或建立記憶集合"""
        try:
            return self.chroma_client.get_collection(name)
        except:
            return self.chroma_client.create_collection(name)
    
    def _generate_embedding(self, text: str) -> List[float]:
        """使用Gemini生成向量嵌入"""
        try:
            # 使用Gemini的文本嵌入模型
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(f"請為以下文本生成語義向量嵌入：{text}")
            
            # 這裡需要實際的嵌入API，暫時使用簡化版本
            # 實際部署時可考慮使用sentence-transformers
            from sentence_transformers import SentenceTransformer
            embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            return embedding_model.encode([text])[0].tolist()
            
        except Exception as e:
            print(f"生成嵌入向量錯誤: {e}")
            # 返回零向量作為備用方案
            return [0.0] * 384
    
    def _generate_memory_id(self, user_id: str, content: str, timestamp: str) -> str:
        """生成唯一記憶ID"""
        source = f"{user_id}_{content}_{timestamp}"
        return hashlib.md5(source.encode()).hexdigest()
    
    def store_memory(self, 
                    user_id: str, 
                    content: str, 
                    memory_type: str,
                    emotion_tag: str,
                    importance_score: float = 0.5,
                    metadata: Dict = None) -> str:
        """儲存記憶到向量資料庫"""
        
        timestamp = datetime.now().isoformat()
        memory_id = self._generate_memory_id(user_id, content, timestamp)
        
        # 生成向量嵌入
        embedding = self._generate_embedding(content)
        
        # 準備元數據
        if metadata is None:
            metadata = {}
        
        full_metadata = {
            'user_id': user_id,
            'timestamp': timestamp,
            'emotion_tag': emotion_tag,
            'importance_score': importance_score,
            'memory_type': memory_type,
            **metadata
        }
        
        # 根據記憶類型存入對應集合
        collection_key = memory_type if memory_type in self.collections else 'conversation'
        collection = self.collections[collection_key]
        
        try:
            collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[full_metadata],
                ids=[memory_id]
            )
            
            print(f"記憶已存儲: {memory_type} - {emotion_tag}")
            return memory_id
            
        except Exception as e:
            print(f"存儲記憶錯誤: {e}")
            return None
    
    def retrieve_memories(self, 
                         query: str, 
                         user_id: str,
                         memory_types: List[str] = None,
                         emotion_filter: str = None,
                         limit: int = 5,
                         time_weight: bool = True) -> List[Dict]:
        """檢索相關記憶"""
        
        # 生成查詢向量
        query_embedding = self._generate_embedding(query)
        
        # 確定搜索的記憶類型
        if memory_types is None:
            memory_types = ['conversation', 'emotion', 'knowledge', 'personality']
        
        all_results = []
        
        # 在各個集合中搜索
        for memory_type in memory_types:
            if memory_type not in self.collections:
                continue
                
            collection = self.collections[memory_type]
            
            # 準備過濾條件
            where_filter = {'user_id': user_id}
            if emotion_filter:
                where_filter['emotion_tag'] = emotion_filter
            
            try:
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=limit,
                    where=where_filter
                )
                
                # 處理結果
                for i in range(len(results['documents'][0])):
                    memory = {
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'distance': results['distances'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'memory_type': memory_type
                    }
                    
                    # 計算時間權重
                    if time_weight:
                        memory['final_score'] = self._calculate_time_weighted_score(
                            1 - memory['distance'],  # 相似度分數
                            memory['metadata']['timestamp'],
                            memory['metadata'].get('importance_score', 0.5)
                        )
                    else:
                        memory['final_score'] = 1 - memory['distance']
                    
                    all_results.append(memory)
                    
            except Exception as e:
                print(f"檢索記憶錯誤 ({memory_type}): {e}")
        
        # 按最終分數排序並返回
        all_results.sort(key=lambda x: x['final_score'], reverse=True)
        return all_results[:limit]
    
    def _calculate_time_weighted_score(self, similarity_score: float, timestamp: str, importance_score: float) -> float:
        """計算包含時間權重的最終分數"""
        try:
            memory_time = datetime.fromisoformat(timestamp)
            current_time = datetime.now()
            time_diff = (current_time - memory_time).days
            
            # 時間衰減函數：越近的記憶權重越高
            time_weight = 1.0 / (1.0 + time_diff * 0.1)
            
            # 綜合分數：相似度 * 時間權重 * 重要性
            final_score = similarity_score * time_weight * (0.5 + importance_score)
            
            return min(final_score, 1.0)  # 確保分數不超過1
            
        except Exception:
            return similarity_score
    
    def store_conversation_memory(self, user_id: str, user_message: str, lumi_response: str, emotion_tag: str):
        """專門儲存對話記憶"""
        conversation_content = f"用戶: {user_message}\nLumi: {lumi_response}"
        
        return self.store_memory(
            user_id=user_id,
            content=conversation_content,
            memory_type='conversation',
            emotion_tag=emotion_tag,
            importance_score=0.6,
            metadata={
                'user_message': user_message,
                'lumi_response': lumi_response
            }
        )
    
    def get_user_emotion_patterns(self, user_id: str, days: int = 30) -> Dict:
        """分析用戶近期情緒模式"""
        try:
            # 計算時間範圍
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            emotion_collection = self.collections['emotion']
            
            # 查詢用戶最近的情緒記憶
            results = emotion_collection.query(
                query_embeddings=[self._generate_embedding("情緒分析")],
                n_results=100,
                where={
                    'user_id': user_id,
                    'timestamp': {'$gte': start_date}
                }
            )
            
            # 統計情緒分布
            emotion_count = {}
            for metadata in results['metadatas'][0]:
                emotion = metadata.get('emotion_tag', 'unknown')
                emotion_count[emotion] = emotion_count.get(emotion, 0) + 1
            
            return {
                'emotion_distribution': emotion_count,
                'total_interactions': len(results['metadatas'][0]),
                'analysis_period': f"{days}天",
                'dominant_emotion': max(emotion_count.items(), key=lambda x: x[1])[0] if emotion_count else 'friend'
            }
            
        except Exception as e:
            print(f"情緒模式分析錯誤: {e}")
            return {'emotion_distribution': {}, 'total_interactions': 0}
    
    def get_memory_summary(self, user_id: str) -> Dict:
        """取得用戶記憶摘要"""
        summary = {
            'total_memories': 0,
            'by_type': {},
            'by_emotion': {},
            'recent_activity': []
        }
        
        for memory_type, collection in self.collections.items():
            try:
                # 查詢該類型的所有記憶數量
                results = collection.query(
                    query_embeddings=[self._generate_embedding("摘要")],
                    n_results=1000,
                    where={'user_id': user_id}
                )
                
                count = len(results['metadatas'][0])
                summary['by_type'][memory_type] = count
                summary['total_memories'] += count
                
                # 統計情緒分布
                for metadata in results['metadatas'][0]:
                    emotion = metadata.get('emotion_tag', 'unknown')
                    summary['by_emotion'][emotion] = summary['by_emotion'].get(emotion, 0) + 1
                
            except Exception as e:
                print(f"摘要統計錯誤 ({memory_type}): {e}")
                summary['by_type'][memory_type] = 0
        
        return summary