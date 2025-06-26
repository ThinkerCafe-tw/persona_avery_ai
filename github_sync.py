import os
import json
import requests
from datetime import datetime
from typing import Dict, Optional
import base64

class GitHubMemorySync:
    """GitHub記憶同步管理器"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = 'ThinkerCafe-tw'
        self.repo_name = 'persona_avery_ai'
        self.branch = 'memory-sync'
        self.base_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        
        # 如果沒有token，使用本地模式
        if not self.github_token:
            print("⚠️ GitHub Token未設置，使用本地同步模式")
    
    def _get_headers(self) -> Dict:
        """取得GitHub API請求頭"""
        return {
            'Authorization': f'token {self.github_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def _ensure_branch_exists(self) -> bool:
        """確保memory-sync分支存在"""
        if not self.github_token:
            return False
            
        try:
            # 檢查分支是否存在
            url = f"{self.base_url}/branches/{self.branch}"
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                # 分支不存在，創建新分支
                return self._create_branch()
            else:
                print(f"檢查分支錯誤: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"分支檢查失敗: {e}")
            return False
    
    def _create_branch(self) -> bool:
        """創建memory-sync分支"""
        try:
            # 取得master分支的最新commit SHA
            url = f"{self.base_url}/git/refs/heads/master"
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code != 200:
                print(f"取得master分支失敗: {response.status_code}")
                return False
            
            master_sha = response.json()['object']['sha']
            
            # 創建新分支
            url = f"{self.base_url}/git/refs"
            data = {
                'ref': f'refs/heads/{self.branch}',
                'sha': master_sha
            }
            
            response = requests.post(url, headers=self._get_headers(), json=data)
            
            if response.status_code == 201:
                print(f"✅ 創建分支 {self.branch} 成功")
                return True
            else:
                print(f"創建分支失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"創建分支錯誤: {e}")
            return False
    
    def sync_user_memory(self, user_id: str, memory_data: Dict) -> bool:
        """同步單個用戶記憶到GitHub"""
        if not self.github_token:
            return self._local_sync(user_id, memory_data)
        
        try:
            # 確保分支存在
            if not self._ensure_branch_exists():
                return False
            
            # 準備文件路徑和內容
            file_path = f"memories/users/{user_id}/memories.json"
            content = json.dumps(memory_data, ensure_ascii=False, indent=2)
            content_base64 = base64.b64encode(content.encode()).decode()
            
            # 檢查文件是否已存在
            file_url = f"{self.base_url}/contents/{file_path}"
            get_response = requests.get(f"{file_url}?ref={self.branch}", headers=self._get_headers())
            
            data = {
                'message': f'🧠 Update memory for user {user_id[:8]}... - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                'content': content_base64,
                'branch': self.branch
            }
            
            # 如果文件存在，需要提供SHA
            if get_response.status_code == 200:
                data['sha'] = get_response.json()['sha']
            
            # 創建或更新文件
            response = requests.put(file_url, headers=self._get_headers(), json=data)
            
            if response.status_code in [200, 201]:
                print(f"✅ 用戶 {user_id[:8]}... 記憶同步成功")
                return True
            else:
                print(f"記憶同步失敗: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"記憶同步錯誤: {e}")
            return False
    
    def _local_sync(self, user_id: str, memory_data: Dict) -> bool:
        """本地文件同步備份"""
        try:
            # 創建本地記憶備份目錄
            backup_dir = "/tmp/lumi_memory_backup"
            os.makedirs(backup_dir, exist_ok=True)
            
            # 保存用戶記憶
            user_file = f"{backup_dir}/{user_id}_memories.json"
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 本地備份成功: {user_file}")
            return True
            
        except Exception as e:
            print(f"本地備份錯誤: {e}")
            return False
    
    def load_user_memory(self, user_id: str) -> Optional[Dict]:
        """從GitHub載入用戶記憶"""
        if not self.github_token:
            return self._load_local_memory(user_id)
        
        try:
            file_path = f"memories/users/{user_id}/memories.json"
            file_url = f"{self.base_url}/contents/{file_path}"
            
            response = requests.get(f"{file_url}?ref={self.branch}", headers=self._get_headers())
            
            if response.status_code == 200:
                content_base64 = response.json()['content']
                content = base64.b64decode(content_base64).decode()
                memory_data = json.loads(content)
                print(f"✅ 從GitHub載入用戶 {user_id[:8]}... 記憶")
                return memory_data
            elif response.status_code == 404:
                print(f"用戶 {user_id[:8]}... 記憶不存在")
                return None
            else:
                print(f"載入記憶失敗: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"載入記憶錯誤: {e}")
            return None
    
    def _load_local_memory(self, user_id: str) -> Optional[Dict]:
        """從本地載入記憶"""
        try:
            backup_dir = "/tmp/lumi_memory_backup"
            user_file = f"{backup_dir}/{user_id}_memories.json"
            
            if os.path.exists(user_file):
                with open(user_file, 'r', encoding='utf-8') as f:
                    memory_data = json.load(f)
                print(f"✅ 從本地載入用戶 {user_id[:8]}... 記憶")
                return memory_data
            else:
                return None
                
        except Exception as e:
            print(f"本地載入錯誤: {e}")
            return None
    
    def create_daily_backup(self, all_memories: Dict) -> bool:
        """創建每日記憶備份"""
        if not self.github_token:
            return self._create_local_daily_backup(all_memories)
        
        try:
            if not self._ensure_branch_exists():
                return False
            
            # 準備備份文件
            today = datetime.now().strftime('%Y-%m-%d')
            file_path = f"memories/backups/daily/{today}_backup.json"
            
            backup_data = {
                'backup_date': today,
                'total_users': len(all_memories),
                'total_memories': sum(len(memories) for memories in all_memories.values()),
                'memories': all_memories
            }
            
            content = json.dumps(backup_data, ensure_ascii=False, indent=2)
            content_base64 = base64.b64encode(content.encode()).decode()
            
            file_url = f"{self.base_url}/contents/{file_path}"
            data = {
                'message': f'📅 Daily memory backup - {today}',
                'content': content_base64,
                'branch': self.branch
            }
            
            response = requests.put(file_url, headers=self._get_headers(), json=data)
            
            if response.status_code in [200, 201]:
                print(f"✅ 每日備份成功: {today}")
                return True
            else:
                print(f"每日備份失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"每日備份錯誤: {e}")
            return False
    
    def _create_local_daily_backup(self, all_memories: Dict) -> bool:
        """創建本地每日備份"""
        try:
            backup_dir = "/tmp/lumi_memory_backup/daily"
            os.makedirs(backup_dir, exist_ok=True)
            
            today = datetime.now().strftime('%Y-%m-%d')
            backup_file = f"{backup_dir}/{today}_backup.json"
            
            backup_data = {
                'backup_date': today,
                'total_users': len(all_memories),
                'total_memories': sum(len(memories) for memories in all_memories.values()),
                'memories': all_memories
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 本地每日備份成功: {backup_file}")
            return True
            
        except Exception as e:
            print(f"本地每日備份錯誤: {e}")
            return False
    
    def get_sync_status(self) -> Dict:
        """取得同步狀態"""
        status = {
            'github_token_configured': bool(self.github_token),
            'repo_accessible': False,
            'branch_exists': False,
            'last_sync': None
        }
        
        if self.github_token:
            try:
                # 檢查repo可訪問性
                response = requests.get(self.base_url, headers=self._get_headers())
                status['repo_accessible'] = response.status_code == 200
                
                # 檢查分支存在性
                if status['repo_accessible']:
                    branch_url = f"{self.base_url}/branches/{self.branch}"
                    branch_response = requests.get(branch_url, headers=self._get_headers())
                    status['branch_exists'] = branch_response.status_code == 200
                    
                    if status['branch_exists']:
                        # 取得最後提交時間
                        commits_url = f"{self.base_url}/commits?sha={self.branch}&per_page=1"
                        commits_response = requests.get(commits_url, headers=self._get_headers())
                        if commits_response.status_code == 200:
                            commits = commits_response.json()
                            if commits:
                                status['last_sync'] = commits[0]['commit']['committer']['date']
                
            except Exception as e:
                print(f"狀態檢查錯誤: {e}")
        
        return status