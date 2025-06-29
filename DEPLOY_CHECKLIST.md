# ✅ Railway 部署檢查清單 - Cruz 最優架構

## 📋 **部署前準備**

### 🔧 **1. 檔案更新**
- [ ] **requirements.txt**: 更新為新依賴 (`cp requirements_new.txt requirements.txt`)
- [ ] **main.py**: 替換為最優架構版本 (`cp main_optimal.py main.py`)
- [ ] **Commit 變更**: `git add . && git commit -m "Railway deployment ready"`

### 🌍 **2. Railway 環境變數設定**

#### ✅ **保留這些變數**
```
LINE_CHANNEL_ACCESS_TOKEN=oPcA4TVqbg+/3bJPqNd1F9raZtxNy/XTtBZ+zN3Q52kUJ/I98cOwt/R+EARWUqWlPdLewvaypNiOneyxSyD22lJfXfrx50/cs3BIrIOQbeUARqSLPoFhylEfbyxeL4eZE3CUh9WMOrI2CX1pCIutngdB04t89/1O/w1cDnyilFU=
LINE_CHANNEL_SECRET=911feb4db68a686de125648739ebe6e2
GEMINI_API_KEY=AIzaSyABNDzghZ7n12S6-ANHIo4zk-FyA7tjxuU
ELEVENLABS_API_KEY=sk_744d84792233e9631afbc85874f8f4699a8631cc7932c9b1
FLASK_ENV=production
PORT=8080
```

#### ❌ **刪除這些變數** (不再需要)
```
VERTEX_AI_PROJECT_ID
VERTEX_AI_LOCATION  
GOOGLE_APPLICATION_CREDENTIALS_JSON
```

### 🎯 **3. 立即執行**

```bash
# 1. 更新檔案
cp requirements_new.txt requirements.txt
cp main_optimal.py main.py

# 2. 提交更改
git add .
git commit -m "🚀 Railway 部署 - Cruz 最優架構版本

✨ 更新內容:
- 使用 Whisper STT (本地免費)
- 使用 Gemini API (簡化)
- 移除 Google Cloud 複雜依賴
- 優化資源使用

📊 預期結果:
- 更快的語音處理
- 更穩定的服務
- 更低的成本"

# 3. 推送到 Railway
git push origin master
```

## 🚀 **部署步驟**

### **Step 1: 更新 Railway 環境變數**
1. 前往 Railway Dashboard
2. 選擇你的專案
3. Variables 頁面
4. 刪除所有 Google Cloud 相關變數
5. 確認保留的變數都正確

### **Step 2: 推送更新**
```bash
git push origin master
```

### **Step 3: 監控部署**
- 查看 Railway 部署日誌
- 等待 Whisper 模型下載完成 (約 2-3 分鐘)
- 確認服務啟動成功

### **Step 4: 功能測試**
1. **健康檢查**: 訪問你的 Railway URL
2. **文字測試**: 發送文字訊息到 LINE Bot
3. **語音測試**: 發送語音訊息測試 Whisper

## ⚠️ **預期部署時間**

- **首次部署**: 5-8 分鐘 (包含 Whisper 模型下載)
- **後續部署**: 2-3 分鐘
- **冷啟動**: 10-20 秒 (Whisper 模型載入)

## 🔍 **部署後驗證**

### **1. 健康檢查**
訪問: `https://your-app.railway.app/`
期望看到:
```json
{
  "service": "Lumi LINE Bot",
  "architecture": "Cruz Optimal (Whisper + Gemini + 11Labs)",
  "components": {
    "whisper_stt": true,
    "gemini_ai": true,
    "elevenlabs_tts": true,
    "memory_system": true
  }
}
```

### **2. LINE Bot 測試**
- 發送文字訊息: "你好"
- 發送語音訊息: 說 "測試語音功能"
- 確認回應正常

### **3. 監控指標**
- Gemini API 使用量 (不超過 50次/日)
- 回應時間 (目標 < 5 秒)
- Railway 資源使用率

## 🎊 **成功指標**

✅ **部署成功** 如果:
- Railway 顯示 "Deployed"
- 健康檢查返回正確 JSON
- LINE Bot 回應文字訊息
- LINE Bot 能處理語音訊息

🎉 **恭喜！Cruz 最優架構成功部署！**

---

**📞 需要協助?** 
- 檢查 Railway 部署日誌
- 確認環境變數設定
- 測試本地功能是否正常