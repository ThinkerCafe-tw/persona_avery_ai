# 🎤 語音輸入(STT)功能設計文件

## 🎯 目標
讓用戶可以直接說話給Lumi，實現真正的語音對話體驗

## 🔄 完整語音交互流程
```
用戶說話 → LINE語音訊息 → STT轉文字 → Lumi處理 → TTS生成語音 → 用戶聽到回應
```

## 🛠️ 技術方案

### 方案1: Google Speech-to-Text API (推薦)
**優點:**
- 中文識別準確度高
- 已有Google Cloud帳戶
- 支援實時語音識別
- 與現有Vertex AI整合

**實施步驟:**
```python
from google.cloud import speech

def transcribe_audio(audio_content):
    """將音頻轉換為文字"""
    client = speech.SpeechClient()
    
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=16000,
        language_code="zh-TW",  # 台灣中文
        alternative_language_codes=["zh-CN"],  # 備用大陸中文
        enable_automatic_punctuation=True,
        model="latest_long"
    )
    
    response = client.recognize(config=config, audio=audio)
    return response.results[0].alternatives[0].transcript
```

### 方案2: OpenAI Whisper API (備用)
**優點:**
- 多語言支援優秀
- 對話式語音識別佳
- 可處理不清楚的發音

```python
import openai

def whisper_transcribe(audio_file):
    """使用Whisper進行語音識別"""
    with open(audio_file, "rb") as audio:
        transcript = openai.Audio.transcribe(
            "whisper-1", 
            audio,
            language="zh"
        )
    return transcript["text"]
```

## 📱 LINE Bot整合

### 處理語音訊息
```python
from linebot.v3.webhooks import AudioMessageContent

@handler.add(MessageEvent, message=AudioMessageContent)
def handle_audio_message(event):
    """處理用戶語音訊息"""
    user_id = event.source.user_id
    
    try:
        # 1. 下載語音文件
        message_content = line_bot_api.get_message_content(event.message.id)
        audio_data = message_content.content
        
        # 2. 語音轉文字
        transcribed_text = transcribe_audio(audio_data)
        print(f"🎤 用戶語音內容: {transcribed_text}")
        
        # 3. 如果轉換成功，按文字訊息處理
        if transcribed_text:
            # 模擬文字訊息事件
            process_text_message(user_id, transcribed_text, event.reply_token)
        else:
            # 語音識別失敗的友善回應
            reply_message = "不好意思，我沒聽清楚你說什麼，可以再說一次嗎？或者用文字跟我說～"
            send_reply(event.reply_token, reply_message)
            
    except Exception as e:
        print(f"語音處理錯誤: {e}")
        error_reply = "語音處理出了點問題，要不要試試用文字跟我聊呢？"
        send_reply(event.reply_token, error_reply)
```

## 🎯 用戶體驗設計

### 語音交互模式
1. **純文字模式** (預設)
   - 用戶: 文字 → Lumi: 文字

2. **語音輸出模式** 
   - 用戶: 文字 → Lumi: 文字 + 語音

3. **完整語音模式** ⭐
   - 用戶: 語音 → Lumi: 文字 + 語音

### 語音模式控制指令
```
"開啟語音輸入" → 開啟STT功能
"開啟語音輸出" → 開啟TTS功能  
"開啟完整語音" → 同時開啟STT+TTS
"關閉語音" → 關閉所有語音功能
```

## 🔧 實施優先順序

### Phase 1: STT基礎功能 (1週)
- Google Speech-to-Text API整合
- LINE語音訊息處理
- 基本中文語音識別

### Phase 2: 語音品質優化 (1週)
- 音頻預處理 (降噪、格式轉換)
- 識別準確度調優
- 錯誤處理優化

### Phase 3: 完整語音體驗 (1週)  
- STT + TTS 完整整合
- 語音模式切換
- 用戶偏好記憶

## 🎤 測試場景

### 基本語音識別測試
```
"你好" → 應識別為: "你好"
"我心情不好" → 應識別為: "我心情不好" 
"今天天氣如何" → 應識別為: "今天天氣如何"
```

### 方言和口音測試
```
台灣國語、大陸普通話、港式中文
不同年齡層的發音特色
快速說話、慢速說話
```

### 環境噪音測試
```
安靜環境、背景音樂、戶外噪音
手機內建麥克風品質測試
```

## 💡 高級功能 (未來考慮)

### 1. 情緒語調識別
- 從語音中識別情緒 (開心、難過、生氣)
- 結合文字內容和語調進行情緒分析
- 提供更精準的人格模式切換

### 2. 語音指令
```
"Lumi，總結今天" → 觸發日記功能
"Lumi，我想聽音樂" → 特殊功能觸發
"Lumi，記住這件事" → 重要事件標記
```

### 3. 多輪語音對話
- 連續語音交流無需重複開啟
- 自動偵測語音結束點
- 智能等待和回應時機

## 🔒 隱私和安全

### 語音數據處理
- 語音文件僅暫存，處理後立即刪除
- 不永久儲存用戶語音內容
- STT結果可選擇性記錄到記憶系統

### 用戶控制權
- 用戶可隨時關閉語音功能
- 清楚告知語音處理流程
- 提供語音數據使用說明

## 🎯 成功指標

### 技術指標
- STT識別準確率 > 90%
- 語音處理延遲 < 3秒
- 錯誤處理覆蓋率 100%

### 用戶體驗指標
- 語音功能使用率
- 用戶滿意度回饋
- 錯誤報告頻率

這將創造真正的語音AI伴侶體驗！🎤✨