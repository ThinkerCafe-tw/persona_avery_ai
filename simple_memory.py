import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib
from github_sync import GitHubMemorySync

class SimpleLumiMemory:
    """簡化版Lumi記憶系統 - 使用JSON文件存儲"""
    
    def __init__(self):
        # 記憶存儲文件路徑
        self.memory_file = '/tmp/lumi_memories.json'
        self.memories = self._load_memories()
        
        # 初始化GitHub同步
        try:
            self.github_sync = GitHubMemorySync()
            print("🔄 GitHub記憶同步已初始化")
        except Exception as e:
            print(f"GitHub同步初始化失敗: {e}")
            self.github_sync = None
    
    def _load_memories(self) -> Dict:
        """載入記憶文件"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def _save_memories(self):
        """保存記憶到文件"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memories, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存記憶錯誤: {e}")
    
    def _generate_memory_id(self, user_id: str, content: str, timestamp: str) -> str:
        """生成唯一記憶ID"""
        source = f"{user_id}_{content}_{timestamp}"
        return hashlib.md5(source.encode()).hexdigest()[:12]
    
    def store_conversation_memory(self, user_id: str, user_message: str, lumi_response: str, emotion_tag: str):
        """儲存對話記憶"""
        timestamp = datetime.now().isoformat()
        memory_id = self._generate_memory_id(user_id, user_message, timestamp)
        
        if user_id not in self.memories:
            self.memories[user_id] = []
        
        memory = {
            'id': memory_id,
            'timestamp': timestamp,
            'user_message': user_message,
            'lumi_response': lumi_response,
            'emotion_tag': emotion_tag,
            'memory_type': 'conversation'
        }
        
        self.memories[user_id].append(memory)
        
        # 限制記憶數量避免文件過大
        if len(self.memories[user_id]) > 100:
            self.memories[user_id] = self.memories[user_id][-100:]
        
        self._save_memories()
        
        # 同步到GitHub（異步，不影響主流程）
        if self.github_sync:
            try:
                user_memories = self.memories.get(user_id, [])
                self.github_sync.sync_user_memory(user_id, user_memories)
            except Exception as e:
                print(f"GitHub同步錯誤: {e}")
        
        return memory_id
    
    def get_recent_memories(self, user_id: str, limit: int = 5) -> List[Dict]:
        """取得最近的記憶"""
        if user_id not in self.memories:
            return []
        
        user_memories = self.memories[user_id]
        # 按時間排序，返回最近的記憶
        sorted_memories = sorted(user_memories, key=lambda x: x['timestamp'], reverse=True)
        return sorted_memories[:limit]
    
    def search_memories_by_emotion(self, user_id: str, emotion_tag: str, limit: int = 3) -> List[Dict]:
        """根據情緒標籤搜索記憶"""
        if user_id not in self.memories:
            return []
        
        matching_memories = []
        for memory in self.memories[user_id]:
            if memory.get('emotion_tag') == emotion_tag:
                matching_memories.append(memory)
        
        # 按時間排序，返回最近的匹配記憶
        sorted_memories = sorted(matching_memories, key=lambda x: x['timestamp'], reverse=True)
        return sorted_memories[:limit]
    
    def get_memory_summary(self, user_id: str) -> Dict:
        """取得用戶記憶摘要"""
        if user_id not in self.memories:
            return {
                'total_memories': 0,
                'by_emotion': {},
                'recent_activity': 0
            }
        
        user_memories = self.memories[user_id]
        emotion_count = {}
        
        # 統計情緒分布
        for memory in user_memories:
            emotion = memory.get('emotion_tag', 'unknown')
            emotion_count[emotion] = emotion_count.get(emotion, 0) + 1
        
        # 計算最近7天的活躍度
        recent_date = datetime.now() - timedelta(days=7)
        recent_activity = 0
        for memory in user_memories:
            try:
                memory_date = datetime.fromisoformat(memory['timestamp'])
                if memory_date >= recent_date:
                    recent_activity += 1
            except:
                pass
        
        return {
            'total_memories': len(user_memories),
            'by_emotion': emotion_count,
            'recent_activity': recent_activity
        }
    
    def get_user_emotion_patterns(self, user_id: str, days: int = 30) -> Dict:
        """分析用戶情緒模式"""
        if user_id not in self.memories:
            return {
                'emotion_distribution': {},
                'total_interactions': 0,
                'dominant_emotion': 'friend'
            }
        
        user_memories = self.memories[user_id]
        start_date = datetime.now() - timedelta(days=days)
        
        emotion_count = {}
        total_interactions = 0
        
        for memory in user_memories:
            try:
                memory_date = datetime.fromisoformat(memory['timestamp'])
                if memory_date >= start_date:
                    emotion = memory.get('emotion_tag', 'friend')
                    emotion_count[emotion] = emotion_count.get(emotion, 0) + 1
                    total_interactions += 1
            except:
                pass
        
        dominant_emotion = 'friend'
        if emotion_count:
            dominant_emotion = max(emotion_count.items(), key=lambda x: x[1])[0]
        
        return {
            'emotion_distribution': emotion_count,
            'total_interactions': total_interactions,
            'dominant_emotion': dominant_emotion
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
    
    def create_daily_backup(self):
        """創建每日記憶備份"""
        if self.github_sync:
            try:
                success = self.github_sync.create_daily_backup(self.memories)
                if success:
                    print("✅ 每日記憶備份已創建")
                return success
            except Exception as e:
                print(f"每日備份錯誤: {e}")
                return False
        return False
    
    def load_user_memory_from_github(self, user_id: str) -> bool:
        """從GitHub載入用戶記憶"""
        if not self.github_sync:
            return False
        
        try:
            github_memories = self.github_sync.load_user_memory(user_id)
            if github_memories:
                self.memories[user_id] = github_memories
                self._save_memories()
                print(f"✅ 從GitHub恢復用戶 {user_id[:8]}... 記憶")
                return True
            return False
        except Exception as e:
            print(f"從GitHub載入記憶錯誤: {e}")
            return False
    
    def get_sync_status(self) -> Dict:
        """取得同步狀態"""
        if self.github_sync:
            return self.github_sync.get_sync_status()
        else:
            return {
                'github_token_configured': False,
                'repo_accessible': False,
                'branch_exists': False,
                'last_sync': None,
                'error': 'GitHub同步未初始化'
            }