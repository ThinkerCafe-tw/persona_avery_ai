# 🚀 Railway 部署指南 - pgvector 記憶系統

## 📋 概述

本指南將幫助您在 Railway 上部署 Lumi AI，並配置 pgvector 服務以實現長期記憶功能。

## 🔧 Railway 專案設置

### 1. 創建 Railway 專案

1. 登入 [Railway](https://railway.app/)
2. 點擊 "New Project"
3. 選擇 "Deploy from GitHub repo"
4. 連接您的 GitHub 倉庫

### 2. 添加 pgvector 服務

在您的 Railway 專案中：

1. 點擊 "New Service"
2. 選擇 "Database" → "pgvector"
3. Railway 的 pgvector 服務已經預裝並配置完成

### 3. 配置環境變數

在 Railway 專案設置中添加以下環境變數：

```bash
# 資料庫連接（Railway 會自動提供）
DATABASE_URL=postgresql://username:password@host:port/database

# Google Vertex AI 配置
VERTEX_AI_PROJECT_ID=your-project-id
VERTEX_AI_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account",...}

# 備用 Gemini API（可選）
GEMINI_API_KEY=your-gemini-api-key

# LINE Bot 配置
LINE_CHANNEL_ACCESS_TOKEN=your-line-access-token
LINE_CHANNEL_SECRET=your-line-channel-secret
```

## 🗄️ pgvector 配置

### 自動配置

Railway 的 pgvector 服務已經預裝並配置完成，我們的程式碼會自動：

1. 連接到 Railway 提供的 pgvector 實例
2. 註冊 pgvector 擴展
3. 創建必要的資料表和索引

### 手動驗證 pgvector

如果需要手動驗證 pgvector 是否正常工作：

```sql
-- 連接到 Railway pgvector 資料庫
-- 檢查 pgvector 擴展
SELECT * FROM pg_extension WHERE extname = 'vector';

-- 檢查我們的資料表
SELECT table_name FROM information_schema.tables 
WHERE table_name = 'lumi_memories';

-- 檢查索引
SELECT indexname, indexdef FROM pg_indexes 
WHERE tablename = 'lumi_memories';
```

## 📦 部署步驟

### 1. 準備程式碼

確保您的專案包含以下檔案：

```
persona_avery_ai/
├── app.py                 # 主應用程式
├── ai_logic.py           # AI 邏輯和記憶系統
├── simple_memory.py      # Railway pgvector 記憶管理
├── requirements.txt      # Python 依賴
├── Dockerfile           # Docker 配置
└── railway.json         # Railway 配置（可選）
```

### 2. requirements.txt

確保包含必要的依賴：

```txt
flask==2.3.3
psycopg2-binary==2.9.7
pgvector==0.2.3
google-generativeai==0.3.2
google-cloud-aiplatform==1.38.1
python-dotenv==1.0.0
numpy==1.24.3
line-bot-sdk==3.5.0
```

### 3. Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴檔案
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式
COPY . .

# 暴露端口
EXPOSE 5000

# 啟動應用程式
CMD ["python", "app.py"]
```

### 4. 部署到 Railway

1. 推送程式碼到 GitHub
2. Railway 會自動檢測並開始部署
3. 監控部署日誌確保沒有錯誤

## 🔍 部署驗證

### 1. 檢查部署狀態

在 Railway 儀表板中：

1. 查看服務狀態是否為 "Deployed"
2. 檢查日誌中是否有錯誤訊息
3. 確認環境變數已正確設定

### 2. 測試記憶系統

部署完成後，測試記憶功能：

```bash
# 在 Railway 終端中運行測試
python memory_test.py
```

### 3. 檢查 pgvector 連接

查看應用程式日誌，應該看到：

```
🔗 正在連接 Railway pgvector...
✅ Railway pgvector 連接成功！
✅ Railway pgvector 資料庫結構初始化完成
```

## 🚨 常見問題

### 1. pgvector 連接失敗

**症狀**：看到 "Railway pgvector 連接失敗" 錯誤

**解決方案**：
- 確認 Railway 專案中已添加 PostgreSQL 服務
- 檢查 DATABASE_URL 環境變數是否正確
- 確認 PostgreSQL 服務狀態為 "Running"

### 2. 向量嵌入失敗

**症狀**：看到 "生成嵌入失敗" 錯誤

**解決方案**：
- 檢查 Google Vertex AI 憑證是否正確
- 確認 VERTEX_AI_PROJECT_ID 設定
- 檢查網路連接是否正常

### 3. 記憶儲存失敗

**症狀**：對話沒有被記憶

**解決方案**：
- 檢查資料庫連接狀態
- 查看應用程式日誌中的錯誤訊息
- 確認資料表是否正確創建

## 📊 監控和維護

### 1. 日誌監控

Railway 提供詳細的應用程式日誌：

- 記憶儲存操作
- 資料庫連接狀態
- 錯誤和警告訊息

### 2. 資料庫監控

在 Railway 儀表板中：

- 查看 PostgreSQL 服務的資源使用情況
- 監控資料庫連接數
- 檢查儲存空間使用量

### 3. 效能優化

如果遇到效能問題：

1. **增加資源**：在 Railway 中升級 PostgreSQL 服務
2. **優化查詢**：檢查記憶檢索查詢的效能
3. **清理舊資料**：定期清理過期的記憶資料

## 🔧 進階配置

### 1. 自定義資料庫設定

如果需要自定義 PostgreSQL 設定：

```sql
-- 調整連接池設定
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET shared_buffers = '256MB';

-- 重新載入設定
SELECT pg_reload_conf();
```

### 2. 備份策略

Railway 提供自動備份功能：

1. 在 PostgreSQL 服務設定中啟用自動備份
2. 設定備份頻率（建議每日）
3. 配置備份保留期限

### 3. 擴展配置

如果需要更多 pgvector 功能：

```sql
-- 創建額外的向量索引
CREATE INDEX IF NOT EXISTS idx_memories_embedding_cosine 
ON lumi_memories USING ivfflat (embedding vector_cosine_ops);

-- 創建分區表（用於大量資料）
CREATE TABLE lumi_memories_partitioned (
    LIKE lumi_memories INCLUDING ALL
) PARTITION BY RANGE (created_at);
```

## 🎉 部署完成

成功部署後，您的 Lumi AI 將具備：

- ✅ 完整的長期記憶功能
- ✅ Railway pgvector 向量資料庫
- ✅ 自動擴展和備份
- ✅ 高可用性部署

## 📞 支援

如果遇到問題：

1. 檢查 Railway 官方文檔
2. 查看應用程式日誌
3. 確認環境變數設定
4. 測試記憶系統功能

---

🚀 **恭喜！** 您的 Lumi AI 現在已經在 Railway 上成功部署，並具備完整的長期記憶功能！ 