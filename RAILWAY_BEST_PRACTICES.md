# 🚀 Railway 部署教戰守則

> **基於 Railway 官方文檔和最佳實踐的完整部署指南**

## 📋 目錄
1. [Railway 架構理解](#railway-架構理解)
2. [部署前檢查清單](#部署前檢查清單)
3. [常見問題與解決方案](#常見問題與解決方案)
4. [最佳實踐](#最佳實踐)
5. [監控與除錯](#監控與除錯)

---

## 🏗️ Railway 架構理解

### Nixpacks vs Railpack
- **Nixpacks**: Railway 的原始建構系統，基於 Nix 包管理器
- **Railpack**: Railway 的新一代建構系統，專為 Railway 最佳化
  - Python 映像體積減少 77%
  - 更快的建構速度
  - 支援 Node、Python、Go、PHP、Static HTML

### Python 版本管理
Railway 支援多種 Python 版本指定方式：

#### 方法 1: `.python-version` 文件（推薦）
```bash
echo "3.11.8" > .python-version
```

#### 方法 2: `runtime.txt` 文件
```bash
echo "python-3.11.8" > runtime.txt
```

#### 方法 3: 環境變數
```bash
NIXPACKS_PYTHON_VERSION=3.11
```

---

## ✅ 部署前檢查清單

### 1. 文件結構檢查
```
project/
├── .python-version      # Python 版本 (推薦)
├── requirements.txt     # 依賴清單
├── main.py             # 主應用文件
├── Procfile            # 啟動命令 (可選)
└── .env                # 環境變數 (本地開發)
```

### 2. requirements.txt 最佳實踐

#### ✅ 正確配置
```txt
# 🧠 AI 與 Web 框架
Flask==2.3.3
google-generativeai==0.8.0
line-bot-sdk==3.9.0

# 🗄️ 資料庫連接 (使用 binary 版本)
psycopg2-binary>=2.9.0
pgvector>=0.2.0

# 🛠️ 基礎工具
python-dotenv==0.21.1
gunicorn==20.1.0
requests==2.31.0
```

#### ❌ 常見錯誤
```txt
# 不要使用這些
psycopg2==2.9.0           # 會在 Railway 編譯失敗
Django>=4.0               # 版本範圍太寬
some-package              # 沒有指定版本
```

### 3. Procfile 配置

#### Flask 應用
```procfile
web: gunicorn main:app --bind 0.0.0.0:$PORT
```

#### Django 應用
```procfile
web: python manage.py migrate && gunicorn myproject.wsgi
```

### 4. 環境變數設定
在 Railway 控制台設定以下變數：

#### 必需變數
- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_CHANNEL_SECRET`
- `GEMINI_API_KEY`

#### 可選變數
- `DATABASE_URL` (Railway PostgreSQL 會自動提供)
- `PORT` (Railway 會自動設定)

---

## 🔧 常見問題與解決方案

### 問題 1: psycopg2 編譯失敗
```
ERROR: Failed building wheel for psycopg2
pg_config is required to build psycopg2 from source
```

#### 解決方案
```bash
# 1. 移除 psycopg2
pip uninstall psycopg2

# 2. 安裝 binary 版本
pip install psycopg2-binary

# 3. 更新 requirements.txt
pip freeze > requirements.txt
```

### 問題 2: pip 命令不存在
```
/bin/bash: line 1: pip: command not found
```

#### 解決方案
**不要** 使用自定義 nixpacks.toml，讓 Railway 自動檢測：
```bash
# 刪除 nixpacks.toml
rm nixpacks.toml

# 確保有正確的 Python 版本文件
echo "3.11.8" > .python-version
```

### 問題 3: 模組導入錯誤
```
ModuleNotFoundError: No module named 'your_module'
```

#### 解決方案
```bash
# 1. 檢查虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 重新生成 requirements.txt
pip freeze > requirements.txt
```

### 問題 4: Railway 建構超時
```
Build failed with timeout
```

#### 解決方案
1. **減少依賴大小**
   ```txt
   # 避免重型依賴
   # tensorflow  # 太大
   # torch       # 太大
   
   # 使用輕量替代
   numpy>=1.21.0
   scikit-learn>=1.0.0
   ```

2. **移除不必要的文件**
   ```gitignore
   # .gitignore
   __pycache__/
   *.pyc
   .env
   venv/
   node_modules/
   *.log
   ```

---

## 🎯 最佳實踐

### 1. 依賴管理
```bash
# 創建乾淨的虛擬環境
python -m venv venv
source venv/bin/activate

# 只安裝必需的包
pip install flask gunicorn psycopg2-binary

# 生成精確的 requirements.txt
pip freeze > requirements.txt
```

### 2. 環境變數管理
```python
# 在代碼中使用環境變數
import os
from dotenv import load_dotenv

load_dotenv()  # 本地開發時載入 .env

DATABASE_URL = os.getenv('DATABASE_URL')
API_KEY = os.getenv('GEMINI_API_KEY')

# 提供預設值和錯誤處理
if not API_KEY:
    raise ValueError("GEMINI_API_KEY 環境變數未設定")
```

### 3. 健康檢查端點
```python
@app.route('/health')
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

### 4. 錯誤處理
```python
# 資料庫連接降級機制
try:
    # 嘗試連接 PostgreSQL
    conn = psycopg2.connect(DATABASE_URL)
    use_database = True
except:
    # 降級到內存存儲
    use_database = False
    logger.warning("資料庫不可用，使用內存模式")
```

---

## 📊 監控與除錯

### 1. 部署日誌監控
```bash
# Railway CLI (如果已安裝)
railway logs

# 或通過 Web 控制台
# https://railway.app/project/your-project/deployments
```

### 2. 健康檢查腳本
```python
import requests
import time

def monitor_deployment(url, max_attempts=20):
    for i in range(max_attempts):
        try:
            response = requests.get(f"{url}/health", timeout=10)
            if response.status_code == 200:
                print(f"✅ 部署成功! 嘗試 {i+1}/{max_attempts}")
                return True
        except:
            pass
        
        print(f"⏳ 等待部署... {i+1}/{max_attempts}")
        time.sleep(30)
    
    return False
```

### 3. 常見除錯步驟
1. **檢查建構日誌**: Railway 控制台 → Deployments → Build Logs
2. **檢查部署日誌**: Railway 控制台 → Deployments → Deploy Logs
3. **檢查運行日誌**: Railway 控制台 → Deployments → HTTP Logs
4. **測試本地環境**: 確保在本地可以正常運行

---

## 🚀 部署流程

### 1. 本地測試
```bash
# 測試應用
python main.py

# 測試依賴
python -c "import all_your_modules; print('All imports OK')"

# 測試 gunicorn
gunicorn main:app --bind 0.0.0.0:5000
```

### 2. 提交代碼
```bash
git add .
git commit -m "準備部署: 更新依賴和配置"
git push origin main
```

### 3. 監控部署
1. 觀察 Railway 控制台的建構過程
2. 檢查建構日誌中的錯誤
3. 等待部署完成
4. 測試應用端點

### 4. 驗證部署
```bash
curl https://your-app.up.railway.app/health
curl https://your-app.up.railway.app/
```

---

## 🔍 故障排除

### 建構失敗
1. 檢查 `requirements.txt` 語法
2. 確認 Python 版本相容性
3. 移除有問題的依賴

### 部署失敗
1. 檢查環境變數設定
2. 確認啟動命令正確
3. 檢查端口綁定

### 運行時錯誤
1. 檢查日誌輸出
2. 確認資料庫連接
3. 驗證 API 金鑰

---

## 📚 參考資源

- [Railway 官方文檔](https://docs.railway.com/)
- [Nixpacks 文檔](https://nixpacks.com/)
- [Python 部署指南](https://docs.railway.com/guides/deploy-python-app)
- [Flask 部署指南](https://docs.railway.com/guides/flask)

---

## 💡 總結

**關鍵原則：**
1. 🎯 **簡單為上**: 讓 Railway 自動檢測，避免過度配置
2. 🔧 **使用 binary**: psycopg2-binary 而非 psycopg2
3. 📝 **精確版本**: requirements.txt 使用固定版本號
4. 🧪 **本地測試**: 部署前確保本地環境完全正常
5. 📊 **監控日誌**: 密切關注建構和部署日誌

遵循這些指南，你的 Railway 部署成功率將大幅提升！🚀