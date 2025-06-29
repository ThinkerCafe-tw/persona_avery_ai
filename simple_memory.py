import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class SimpleLumiMemory:
    """簡化版記憶系統 - 內存存儲模式（暫時降級，等 pgvector 修復）"""
    
    def __init__(self):
        self.memory_store = {}  # 用戶資訊存儲
        self.conversations = {}  # 對話記錄存儲
        print("🧠 使用內存記憶模式 (重啟會清空)")
    
    def get_user_info(self, user_id: str) -> Dict:
        """獲取用戶資訊"""
        return self.memory_store.get(user_id, {})
    
    def set_user_info(self, user_id: str, key: str, value: str):
        """設定用戶資訊"""
        if user_id not in self.memory_store:
            self.memory_store[user_id] = {}
        self.memory_store[user_id][key] = value
    
    def add_interaction(self, user_id: str, user_message: str, ai_response: str, emotion_tag: str = 'neutral'):
        """添加對話記錄"""
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
        if user_id not in self.conversations:
            return []
        
        user_convs = self.conversations[user_id]
        return user_convs[-limit:] if len(user_convs) >= limit else user_convs
    
    def search_memories_by_emotion(self, user_id: str, emotion_tag: str, limit: int = 3) -> List[Dict]:
        """根據情緒標籤搜索記憶"""
        if user_id not in self.conversations:
            return []
        
        matching = [conv for conv in self.conversations[user_id] 
                   if conv.get('emotion_tag') == emotion_tag]
        return matching[-limit:] if len(matching) >= limit else matching
    
    def get_memory_summary(self, user_id: str) -> Dict:
        """取得用戶記憶摘要"""
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
        
        # 最近7天活躍度（簡化版）
        recent_activity = len(user_convs)
        
        return {
            'total_memories': len(user_convs),
            'by_emotion': emotion_count,
            'recent_activity': recent_activity
        }
    
    def get_user_emotion_patterns(self, user_id: str, days: int = 30) -> Dict:
        """分析用戶情緒模式"""
        if user_id not in self.conversations:
            return {
                'emotion_distribution': {},
                'total_interactions': 0,
                'dominant_emotion': 'neutral'
            }
        
        user_convs = self.conversations[user_id]
        emotion_distribution = {}
        
        for conv in user_convs:
            emotion = conv.get('emotion_tag', 'neutral')
            emotion_distribution[emotion] = emotion_distribution.get(emotion, 0) + 1
        
        dominant_emotion = 'neutral'
        if emotion_distribution:
            dominant_emotion = max(emotion_distribution.items(), key=lambda x: x[1])[0]
        
        return {
            'emotion_distribution': emotion_distribution,
            'total_interactions': len(user_convs),
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
        """測試記憶系統（內存模式總是成功）"""
        return True

if __name__ == "__main__":
    # 測試
    print("🧪 測試內存記憶系統...")
    
    memory = SimpleLumiMemory()
    
    # 測試基本功能
    memory.add_interaction("test_user", "我叫小明", "你好小明！", "friend")
    user_info = memory.get_user_info("test_user")
    recent = memory.get_recent_memories("test_user")
    
    print(f"✅ 用戶資訊: {user_info}")
    print(f"✅ 最近記憶: {len(recent)} 條")
    print("🎉 內存記憶系統準備就緒！")