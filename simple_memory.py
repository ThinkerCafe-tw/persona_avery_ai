import os
import json
from datetime import datetime
from github import Github, GithubException

class SimpleLumiMemory:
    def __init__(self):
        self.memory_file = os.path.join(os.getcwd(), 'lumi_memory.json')
        self.user_memories = self._load_memories_from_file()
        print("SimpleLumiMemory: 記憶系統已初始化")

        # GitHub 配置
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repo_name = os.getenv('GITHUB_REPO')
        self.github_branch = os.getenv('GITHUB_BRANCH', 'main') # 預設為 main 分支
        self.github_memory_path = os.getenv('GITHUB_MEMORY_PATH', 'memory/user_memories.json')

        self.github_client = None
        if self.github_token and self.github_repo_name:
            try:
                self.github_client = Github(self.github_token)
                print("SimpleLumiMemory: GitHub 客戶端已初始化")
            except Exception as e:
                print(f"SimpleLumiMemory: GitHub 客戶端初始化失敗: {e}")

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

    def create_daily_backup(self):
        if not self.github_client or not self.github_repo_name:
            print("SimpleLumiMemory: GitHub 配置不完整，無法備份。")
            return False

        try:
            repo = self.github_client.get_user().get_repo(self.github_repo_name.split('/')[1])
            contents = repo.get_contents(self.github_memory_path, ref=self.github_branch)
            
            # 讀取本地記憶檔案內容
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                local_memory_content = f.read()

            # 更新 GitHub 上的檔案
            repo.update_file(
                contents.path,
                f"Update memory backup {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                local_memory_content,
                contents.sha,
                branch=self.github_branch
            )
            print("SimpleLumiMemory: 記憶備份已更新到 GitHub。")
            return True
        except GithubException as e:
            if e.status == 404: # 檔案不存在，則創建
                try:
                    repo = self.github_client.get_user().get_repo(self.github_repo_name.split('/')[1])
                    with open(self.memory_file, 'r', encoding='utf-8') as f:
                        local_memory_content = f.read()
                    repo.create_file(
                        self.github_memory_path,
                        f"Initial memory backup {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        local_memory_content,
                        branch=self.github_branch
                    )
                    print("SimpleLumiMemory: 記憶備份已創建到 GitHub。")
                    return True
                except Exception as create_e:
                    print(f"SimpleLumiMemory: 創建 GitHub 記憶備份失敗: {create_e}")
                    return False
            else:
                print(f"SimpleLumiMemory: GitHub 備份失敗: {e}")
                return False
        except Exception as e:
            print(f"SimpleLumiMemory: 備份記憶時發生錯誤: {e}")
            return False

    def load_user_memory_from_github(self, user_id):
        if not self.github_client or not self.github_repo_name:
            print("SimpleLumiMemory: GitHub 配置不完整，無法恢復記憶。")
            return False

        try:
            repo = self.github_client.get_user().get_repo(self.github_repo_name.split('/')[1])
            contents = repo.get_contents(self.github_memory_path, ref=self.github_branch)
            github_memory_content = contents.decoded_content.decode('utf-8')
            
            # 載入 GitHub 上的記憶並覆蓋本地記憶
            self.user_memories = json.loads(github_memory_content)
            self._save_memories_to_file() # 同步到本地檔案
            print("SimpleLumiMemory: 記憶已從 GitHub 恢復。")
            return True
        except GithubException as e:
            if e.status == 404:
                print("SimpleLumiMemory: GitHub 上沒有找到記憶備份檔案。")
            else:
                print(f"SimpleLumiMemory: 從 GitHub 恢復記憶失敗: {e}")
            return False
        except Exception as e:
            print(f"SimpleLumiMemory: 恢復記憶時發生錯誤: {e}")
            return False

    def get_sync_status(self):
        status = {
            'github_token_configured': bool(self.github_token),
            'github_repo_configured': bool(self.github_repo_name),
            'repo_accessible': False,
            'branch_exists': False,
            'last_sync': None
        }

        if self.github_client and self.github_repo_name:
            try:
                repo = self.github_client.get_user().get_repo(self.github_repo_name.split('/')[1])
                status['repo_accessible'] = True
                try:
                    repo.get_branch(self.github_branch)
                    status['branch_exists'] = True
                    try:
                        contents = repo.get_contents(self.github_memory_path, ref=self.github_branch)
                        status['last_sync'] = datetime.fromisoformat(json.loads(contents.decoded_content.decode('utf-8')).get('last_sync_timestamp', 'N/A')).strftime('%Y-%m-%d %H:%M:%S')
                    except GithubException as e:
                        if e.status == 404:
                            status['last_sync'] = "記憶檔案不存在"
                        else:
                            print(f"SimpleLumiMemory: 獲取記憶檔案狀態失敗: {e}")
                    except Exception as e:
                        print(f"SimpleLumiMemory: 解析記憶檔案時間戳失敗: {e}")
                except GithubException as e:
                    if e.status == 404:
                        status['branch_exists'] = False
                        print(f"SimpleLumiMemory: 分支 {self.github_branch} 不存在。")
                    else:
                        print(f"SimpleLumiMemory: 檢查分支失敗: {e}")
            except GithubException as e:
                if e.status == 404:
                    print("SimpleLumiMemory: GitHub 倉庫不存在或無法訪問。")
                else:
                    print(f"SimpleLumiMemory: 檢查 GitHub 倉庫失敗: {e}")
            except Exception as e:
                print(f"SimpleLumiMemory: 檢查 GitHub 連接時發生錯誤: {e}")
        return status