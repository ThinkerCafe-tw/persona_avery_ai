# 🚀 LINE Bot SDK 快速修復指南

## 🚨 當前問題

Railway 部署時出現 LINE Bot SDK 導入錯誤：
```
ImportError: cannot import name 'LineBotApi' from 'linebot.v3'
```

## ✅ 解決方案

### 方案 1：使用備用檔案（推薦）

```bash
# 1. 使用備用檔案
mv app_backup.py app.py

# 2. 提交更改
git add .
git commit -m "使用備用 app.py 修復 LINE Bot SDK 問題"
git push origin main
```

### 方案 2：降級 LINE Bot SDK 版本

```bash
# 1. 修改 requirements.txt
echo "line-bot-sdk==2.4.2" > requirements.txt
echo "Flask" >> requirements.txt
echo "python-dotenv" >> requirements.txt
echo "google-generativeai" >> requirements.txt
echo "google-cloud-aiplatform>=1.40.0" >> requirements.txt
echo "psycopg2-binary" >> requirements.txt
echo "pgvector" >> requirements.txt
echo "numpy" >> requirements.txt
echo "requests" >> requirements.txt

# 2. 提交更改
git add .
git commit -m "降級 LINE Bot SDK 版本"
git push origin main
```

### 方案 3：清理 Railway 緩存

如果上述方案不行，可能需要清理 Railway 的緩存：

1. 在 Railway 儀表板中
2. 找到您的應用程式
3. 點擊 "Settings"
4. 找到 "Build & Deploy" 部分
5. 點擊 "Clear build cache"
6. 重新部署

## 🔍 問題原因

1. **版本不相容**：LINE Bot SDK v3 的導入結構與我們的程式碼不符
2. **緩存問題**：Railway 可能緩存了舊的程式碼
3. **依賴衝突**：不同版本的依賴可能衝突

## 📋 檢查清單

- [ ] 使用備用 app.py
- [ ] 降級 LINE Bot SDK 版本
- [ ] 清理 Railway 緩存
- [ ] 重新部署
- [ ] 測試 LINE Bot 功能

## 🚀 快速修復命令

```bash
# 最簡單的修復方法
mv app_backup.py app.py
git add .
git commit -m "快速修復 LINE Bot SDK 問題"
git push origin main
```

## ⚠️ 注意事項

1. **備用檔案**：`app_backup.py` 使用已知工作的導入方式
2. **版本相容性**：v2.4.2 是穩定版本
3. **功能完整性**：所有功能都會正常工作

## 🎯 預期結果

修復後應該看到：
- ✅ 沒有導入錯誤
- ✅ Flask 應用程式正常啟動
- ✅ LINE Bot 功能正常
- ✅ 記憶系統正常工作

---

🚀 **選擇方案 1 是最快的修復方法！** 