# 🚀 Railway 部署指南 - Cruz 最優架構

## 📋 部署前檢查清單

### ✅ **已完成**
- [x] Whisper STT 系統
- [x] Gemini AI 整合
- [x] 11Labs TTS 配置
- [x] 完整語音循環測試

### 🔧 **需要在 Railway 設定**

#### 1. **環境變數更新**
```bash
# 保留這些
LINE_CHANNEL_ACCESS_TOKEN=oPcA4TVqbg+/3bJPqNd1F9raZtxNy/XTtBZ+zN3Q52kUJ/I98cOwt/R+EARWUqWlPdLewvaypNiOneyxSyD22lJfXfrx50/cs3BIrIOQbeUARqSLPoFhylEfbyxeL4eZE3CUh9WMOrI2CX1pCIutngdB04t89/1O/w1cDnyilFU=
LINE_CHANNEL_SECRET=911feb4db68a686de125648739ebe6e2
GEMINI_API_KEY=AIzaSyABNDzghZ7n12S6-ANHIo4zk-FyA7tjxuU
ELEVENLABS_API_KEY=sk_744d84792233e9631afbc85874f8f4699a8631cc7932c9b1
FLASK_ENV=production
PORT=8080

# 刪除這些 (不再需要)
# VERTEX_AI_PROJECT_ID=cool-ruler-419911
# VERTEX_AI_LOCATION=us-central1  
# GOOGLE_APPLICATION_CREDENTIALS_JSON={...大段JSON...}
```

#### 2. **文件更新**
- [ ] 更新 `requirements.txt` 為新依賴
- [ ] 更新主應用文件使用新架構
- [ ] 確保 Railway 有足夠資源運行 Whisper

#### 3. **資源考量**
- **CPU**: Whisper 需要適當 CPU (base 模型適中)
- **RAM**: 建議至少 1GB (Whisper 模型載入)
- **儲存**: Whisper 模型約 140MB

## 🚀 **部署步驟**

### Step 1: 更新 requirements.txt
```bash
cp requirements_new.txt requirements.txt
```

### Step 2: 更新主應用
需要修改你的主 Flask 應用使用新架構：
- 導入 `whisper_stt` 而非 Google STT
- 導入 `gemini_ai` 而非 Vertex AI
- 保持現有 LINE Bot 邏輯

### Step 3: Railway 環境變數
1. 登入 Railway Dashboard
2. 選擇你的專案
3. Variables 頁面：
   - 移除所有 Google Cloud 相關變數
   - 確認 GEMINI_API_KEY 和 ELEVENLABS_API_KEY

### Step 4: 推送更新
```bash
git push origin master
```

### Step 5: 監控部署
- 查看 Railway 部署日誌
- 確認 Whisper 模型載入成功
- 測試語音功能

## ⚠️ **潛在問題與解決**

### Whisper 載入時間
**問題**: 首次載入 Whisper 模型較慢
**解決**: 
- 使用 `tiny` 或 `base` 模型 (已設定 base)
- 考慮預載入策略

### 記憶體使用
**問題**: Whisper 可能消耗較多 RAM
**解決**:
- 監控 Railway 資源使用
- 必要時升級 plan

### 冷啟動
**問題**: Railway 冷啟動可能較慢
**解決**:
- 實現健康檢查端點
- 考慮 keepalive 策略

## 🎯 **部署後驗證**

### 功能測試
1. **LINE Bot 回應**: 確認基本文字功能
2. **語音轉文字**: 發送語音訊息測試 Whisper
3. **AI 對話**: 確認 Gemini API 回應
4. **語音輸出**: 確認 11Labs TTS 正常

### 監控指標
- Gemini API 使用量 (50次/日限制)
- 回應時間 (目標 < 5秒)
- 錯誤率
- 資源使用率

## 💡 **優化建議**

### 性能優化
- 考慮 Whisper 模型大小調整
- 實現智能快取機制
- 優化語音檔案處理

### 成本優化
- 監控 Railway 資源使用
- 優化不必要的計算
- 實現優雅的降級機制

---

**🎊 準備好部署 Cruz 最優架構了！**