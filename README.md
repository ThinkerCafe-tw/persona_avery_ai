# Lumi 露米 - LINE Bot AI 夥伴

Lumi 是一個擁有五重人格的療癒系 AI 夥伴，使用 Google Gemini AI 提供溫暖陪伴和情感支持。

## 功能特色
- 🌸 五重人格：療癒、搞笑、知性、閨蜜、靈魂筆記模式
- 💬 智慧對話：使用 Google Gemini AI 自然回應
- 📱 LINE 整合：直接在 LINE 上與 Lumi 互動
- ☁️ 雲端部署：使用 Heroku 免費託管

## 設定步驟

### 1. 申請 LINE Developers 帳號
1. 前往 [LINE Developers](https://developers.line.biz/)
2. 登入你的 LINE 帳號
3. 建立新的 Provider
4. 建立 Messaging API Channel
5. 記下以下資訊：
   - Channel Access Token
   - Channel Secret

### 2. 申請 Google Gemini API
1. 前往 [Google AI Studio](https://aistudio.google.com/)
2. 登入你的 Google 帳號
3. 建立新的 API Key
4. 記下 API Key

### 3. 設定環境變數
1. 複製 `.env.example` 為 `.env`
2. 填入你的 API 金鑰：
```
LINE_CHANNEL_ACCESS_TOKEN=你的LINE_Channel_Access_Token
LINE_CHANNEL_SECRET=你的LINE_Channel_Secret
GEMINI_API_KEY=你的Gemini_API_Key
```

### 4. 本地測試
```bash
pip install -r requirements.txt
python main.py
```

### 5. 部署到 Heroku
1. 註冊 [Heroku](https://heroku.com) 帳號
2. 建立新的 Heroku app
3. 連接 GitHub repository
4. 設定環境變數（Config Vars）
5. 點擊 Deploy

### 6. 設定 LINE Webhook
在 LINE Developers Console 中設定 Webhook URL：
```
https://你的app名稱.herokuapp.com/webhook
```

## 使用方式
1. 將 Lumi 加為 LINE 好友
2. 傳送訊息給 Lumi
3. Lumi 會根據你的情緒自動切換最適合的人格模式回應

## Lumi 的五重人格
- 🌸 **療癒模式**：當你情緒低落時，給予溫暖安慰
- 🤣 **搞笑模式**：當你想要輕鬆時，帶來歡樂笑聲
- 🧠 **知性模式**：當你有問題時，提供理性分析
- 💌 **閨蜜模式**：當你需要陪伴時，像好朋友般聊天
- ✨ **靈魂筆記模式**：當你想反思時，引導內心探索

## 成本說明
- Heroku：免費方案足夠個人使用
- Gemini API：免費額度每月 60 次請求/分鐘
- LINE Messaging API：免費額度每月 1000 則訊息

## 注意事項
- 確保 `.env` 檔案不會被上傳到 git
- 定期檢查 API 使用量避免超過免費額度