# ✅ Railway 部署檢查清單

## 🚀 部署前檢查

### 1. Railway 專案設置
- [ ] 已在 Railway 創建新專案
- [ ] 已連接 GitHub 倉庫
- [ ] 已添加 pgvector 服務

### 2. 環境變數配置
- [ ] `DATABASE_URL` - Railway 自動提供
- [ ] `VERTEX_AI_PROJECT_ID` - Google Cloud 專案 ID
- [ ] `VERTEX_AI_LOCATION` - 通常為 `us-central1`
- [ ] `GOOGLE_APPLICATION_CREDENTIALS_JSON` - 服務帳戶憑證
- [ ] `LINE_CHANNEL_ACCESS_TOKEN` - LINE Bot 存取權杖
- [ ] `LINE_CHANNEL_SECRET` - LINE Bot 密鑰

### 3. 程式碼準備
- [ ] `simple_memory.py` - 已更新為 Railway pgvector 版本
- [ ] `requirements.txt` - 包含所有必要依賴
- [ ] `Dockerfile` - 已優化為 Railway 部署
- [ ] `railway.json` - Railway 配置文件
- [ ] `app.py` - 包含健康檢查端點

### 4. Google Cloud 設置
- [ ] 已啟用 Vertex AI API
- [ ] 已創建服務帳戶
- [ ] 已下載服務帳戶金鑰
- [ ] 已設定適當權限

### 5. LINE Bot 設置
- [ ] 已在 LINE Developers 創建 Bot
- [ ] 已獲取 Channel Access Token
- [ ] 已獲取 Channel Secret
- [ ] 已設定 Webhook URL

## 🔧 部署步驟

### 1. 推送程式碼
```bash
git add .
git commit -m "準備 Railway 部署"
git push origin main
```

### 2. Railway 部署
- [ ] Railway 自動檢測並開始部署
- [ ] 監控部署日誌
- [ ] 確認部署成功

### 3. 環境變數設定
- [ ] 在 Railway 儀表板設定所有環境變數
- [ ] 確認 DATABASE_URL 正確
- [ ] 測試 Google Cloud 憑證

### 4. 服務驗證
- [ ] 檢查應用程式狀態為 "Deployed"
- [ ] 測試健康檢查端點 `/health`
- [ ] 測試首頁端點 `/`

## 🧪 功能測試

### 1. 記憶系統測試
```bash
# 在 Railway 終端中運行
python memory_test.py
```

### 2. LINE Bot 測試
- [ ] 發送測試訊息到 LINE Bot
- [ ] 確認 Bot 正常回覆
- [ ] 測試記憶功能

### 3. pgvector 連接測試
- [ ] 檢查日誌中的連接訊息
- [ ] 確認資料表已創建
- [ ] 測試記憶儲存和檢索

## 📊 監控檢查

### 1. 日誌監控
- [ ] 檢查應用程式日誌
- [ ] 確認無錯誤訊息
- [ ] 監控記憶操作日誌

### 2. 資料庫監控
- [ ] 檢查 pgvector 服務狀態
- [ ] 監控資料庫連接
- [ ] 檢查儲存空間使用

### 3. 效能監控
- [ ] 監控回應時間
- [ ] 檢查記憶檢索效能
- [ ] 監控資源使用

## 🚨 故障排除

### 常見問題檢查
- [ ] pgvector 連接失敗 → 檢查 DATABASE_URL
- [ ] 嵌入生成失敗 → 檢查 Google Cloud 憑證
- [ ] LINE Bot 無回應 → 檢查 Webhook URL
- [ ] 記憶不工作 → 檢查 pgvector 連接

### 日誌檢查
- [ ] 查看 Railway 應用程式日誌
- [ ] 檢查 pgvector 服務日誌
- [ ] 確認環境變數正確載入

## 🎉 部署完成確認

### 最終檢查清單
- [ ] ✅ 應用程式正常運行
- [ ] ✅ LINE Bot 正常回應
- [ ] ✅ 記憶系統正常工作
- [ ] ✅ pgvector 連接穩定
- [ ] ✅ 健康檢查通過
- [ ] ✅ 所有功能測試通過

## 📞 支援資源

### 文檔
- [ ] `RAILWAY_DEPLOYMENT_GUIDE.md` - 詳細部署指南
- [ ] `LONG_TERM_MEMORY_GUIDE.md` - 記憶系統指南
- [ ] `PROMPT_IMPROVEMENTS.md` - 提示詞改進說明

### 測試工具
- [ ] `memory_test.py` - 記憶系統測試
- [ ] `/health` 端點 - 健康檢查
- [ ] `/` 端點 - 服務狀態

---

🎯 **完成所有檢查項目後，您的 Lumi AI 就成功部署在 Railway 上了！** 