# LINE Bot AI 美業助理

這是一個專為美業工作者設計的 LINE Bot AI 助理，使用 Google Gemini AI 提供智慧對話功能。

## 功能特色
- 智慧對話：使用 Google Gemini AI 回應客人問題
- 美業專精：針對接睫毛、美容保養等領域優化
- LINE 整合：直接在 LINE 上與客人互動
- 低成本運行：使用 Google App Engine 免費額度

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

### 5. 部署到 Google App Engine
```bash
gcloud app deploy
```

### 6. 設定 LINE Webhook
在 LINE Developers Console 中設定 Webhook URL：
```
https://你的專案名稱.uc.r.appspot.com/webhook
```

## 使用方式
1. 將你的 LINE Bot 加為好友
2. 傳送訊息給 Bot
3. Bot 會使用 AI 智慧回應

## 成本說明
- Google App Engine：免費額度每月足夠小型使用
- Gemini API：免費額度每月 60 次請求/分鐘
- LINE Messaging API：免費額度每月 1000 則訊息

## 注意事項
- 確保 `.env` 檔案不會被上傳到 git
- 定期檢查 API 使用量避免超過免費額度