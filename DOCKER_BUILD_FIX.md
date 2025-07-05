# 🔧 Docker 構建修復指南

## 🚨 問題描述

部署時遇到 Docker 構建失敗：
```
✕ [5/7] RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
process "/bin/sh -c pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt" did not complete successfully: exit code: 1
```

## 🛠️ 解決方案

### 方案 1：使用簡化版本（推薦）

1. **重命名簡化檔案**：
   ```bash
   mv Dockerfile.simple Dockerfile
   mv requirements-test.txt requirements.txt
   ```

2. **提交並推送**：
   ```bash
   git add .
   git commit -m "使用簡化 Dockerfile 修復構建問題"
   git push origin main
   ```

### 方案 2：逐步添加依賴

如果方案 1 不行，逐步添加依賴：

1. **先使用最基礎的依賴**：
   ```txt
   Flask
   line-bot-sdk
   python-dotenv
   ```

2. **測試構建成功後，逐步添加**：
   ```txt
   Flask
   line-bot-sdk
   python-dotenv
   psycopg2-binary
   ```

3. **最後添加 Google AI 依賴**：
   ```txt
   Flask
   line-bot-sdk
   python-dotenv
   psycopg2-binary
   pgvector
   google-generativeai
   google-cloud-aiplatform
   numpy
   requests
   ```

### 方案 3：使用特定版本

如果還是有問題，使用已知相容的版本：

```txt
Flask==2.3.3
line-bot-sdk==3.5.0
python-dotenv==1.0.0
psycopg2-binary==2.9.7
pgvector==0.2.3
google-generativeai==0.3.2
google-cloud-aiplatform==1.38.1
numpy==1.24.3
requests==2.31.0
```

## 🔍 常見問題

### 1. psycopg2-binary 安裝失敗
- 確保 Dockerfile 中有 `libpq-dev` 和 `gcc`
- 嘗試使用 `psycopg2` 而不是 `psycopg2-binary`

### 2. pgvector 安裝失敗
- 確保使用 Python 3.11
- 檢查是否有編譯錯誤

### 3. Google AI 依賴問題
- 確保使用相容的版本
- 考慮分階段安裝

## 📋 檢查清單

- [ ] 使用簡化 Dockerfile
- [ ] 移除版本限制
- [ ] 確保系統依賴正確
- [ ] 測試本地構建
- [ ] 推送並重新部署

## 🚀 快速修復命令

```bash
# 1. 使用簡化版本
mv Dockerfile.simple Dockerfile
mv requirements-test.txt requirements.txt

# 2. 提交更改
git add .
git commit -m "修復 Docker 構建問題"
git push origin main

# 3. 監控部署
# 在 Railway 儀表板中查看部署日誌
```

---

🎯 **如果還有問題，請查看 Railway 的詳細錯誤日誌！** 