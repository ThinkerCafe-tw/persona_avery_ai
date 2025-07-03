import os
import json
from datetime import datetime


class SimpleLumiMemory:
    def __init__(self):
        self.memory_file = os.path.join(os.getcwd(), 'lumi_memory.json')
        self.user_memories = self._load_memories_from_file()
        print("SimpleLumiMemory: 記憶系統已初始化")

    def _load_memories_from_file(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    memories = json.load(f)
                    print(f"SimpleLumiMemory: 從 {self.memory_file} 載入記憶")
                    return memories
            except json.JSONDecodeError as e:
                print(f"SimpleLumiMemory: 記憶檔案損壞或格式錯誤: {e}")
                return {}
        return {}

    def _save_memories_to_file(self):
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_memories, f, ensure_ascii=False, indent=2)
            print(f"SimpleLumiMemory: 記憶已儲存到 {self.memory_file}")
        except Exception as e:
            print(f"SimpleLumiMemory: 儲存記憶到檔案失敗: {e}")

    def store_conversation_memory(self, user_id, user_message, lumi_response, emotion_tag=None):
        if user_id not in self.user_memories:
            self.user_memories[user_id] = []
        
        self.user_memories[user_id].append({
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'lumi_response': lumi_response,
            'emotion_tag': emotion_tag
        })
        self._save_memories_to_file()
        print(f"SimpleLumiMemory: 已儲存用戶 {user_id[:8]}... 的對話記憶")

    def get_recent_memories(self, user_id, limit=3):
        return self.user_memories.get(user_id, [])[-limit:]

    def get_memory_summary(self, user_id):
        memories = self.user_memories.get(user_id, [])
        return {
            'total_memories': len(memories),
            'last_interaction': memories[-1]['timestamp'] if memories else 'N/A'
        }

    def get_user_emotion_patterns(self, user_id):
        memories = self.user_memories.get(user_id, [])
        emotion_counts = {}
        for m in memories:
            if m.get('emotion_tag'):
                emotion_counts[m['emotion_tag']] = emotion_counts.get(m['emotion_tag'], 0) + 1
        
        dominant_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else 'friend'
        return {
            'dominant_emotion': dominant_emotion,
            'total_interactions': len(memories)
        }
