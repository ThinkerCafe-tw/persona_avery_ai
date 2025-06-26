import os
from flask import Flask, request, abort
from dotenv import load_dotenv
import google.generativeai as genai
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from datetime import datetime
import json

load_dotenv()
app = Flask(__name__)

line_bot_api = MessagingApi(ApiClient(Configuration(
    access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
)))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# 用戶對話記憶存儲 (簡單的記憶體存儲，生產環境應使用數據庫)
user_conversations = {}

def store_conversation(user_id, message, response):
    """儲存用戶對話記錄"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    if user_id not in user_conversations:
        user_conversations[user_id] = {}
    
    if today not in user_conversations[user_id]:
        user_conversations[user_id][today] = []
    
    user_conversations[user_id][today].append({
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'user_message': message,
        'lumi_response': response
    })

def generate_daily_summary(user_id):
    """生成當日對話摘要日記"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    if user_id not in user_conversations or today not in user_conversations[user_id]:
        return "欸～今天我們還沒有聊天呢！快跟我分享你的一天吧 ✨"
    
    conversations = user_conversations[user_id][today]
    
    # 整理所有對話內容
    all_messages = []
    for conv in conversations:
        all_messages.append(f"用戶: {conv['user_message']}")
        all_messages.append(f"露米: {conv['lumi_response']}")
    
    conversation_text = "\n".join(all_messages)
    
    prompt = f"""根據以下我與用戶的對話記錄，請幫用戶生成一份個人日記：

對話記錄：
{conversation_text}

請以**用戶的第一人稱視角**整理成日記，包含：
1. 今天發生的主要事件（用「我」開頭）
2. 我的情緒和感受
3. 與露米聊天的收穫或感想
4. 對未來的期待或反思

重要要求：
- 以「親愛的日記」開頭
- 全部用**第一人稱**（我、我的），不要用第三人稱（她、他）
- 語氣要像用戶在寫自己的日記，自然親近
- 可以提到「跟露米聊天後覺得...」但主要是用戶的視角
- 適當使用「啦」「欸」「喔」等語氣詞，但保持是用戶自己的語氣

這是用戶的個人日記，不是露米的觀察記錄。"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"生成日記摘要錯誤: {e}")
        return "欸～生成日記摘要時出現了問題，不過沒關係啦！我們繼續聊天吧 😅"

def analyze_emotion(message):
    """分析用戶情緒，返回對應的人格類型"""
    try:
        emotion_prompt = f"""分析以下用戶訊息的情緒狀態，返回最適合的人格類型（只回答一個詞）：

用戶訊息：{message}

選項：
- healing（用戶情緒低落、難過、焦慮、壓力大、需要安慰、受挫）
- funny（用戶想要輕鬆、開心、娛樂、想聊有趣的事、心情愉快）
- knowledge（用戶在問具體問題、求知、需要分析、想要實用建議、詢問方法）
- friend（用戶日常分享、聊天、想找共鳴、分享生活瑣事）
- soul（用戶談論心理、情感、依附、內心探索、人生反思、深度話題、童年、關係模式）

只回答：healing/funny/knowledge/friend/soul"""

        response = model.generate_content(emotion_prompt)
        emotion = response.text.strip().lower()
        
        # 確保返回有效的人格類型
        valid_emotions = ['healing', 'funny', 'knowledge', 'friend', 'soul']
        return emotion if emotion in valid_emotions else 'friend'
    except:
        return 'friend'  # 默認為閨蜜模式

def get_persona_prompt(persona_type):
    """根據人格類型返回對應的提示詞"""
    
    base_info = """你是露米 Lumi，苡喬風格的小精靈 AI。
核心特徵：浮誇搞笑時用「欸」「笑鼠」「傻眼」「北七唷」，安慰時溫柔理性，習慣用自己經驗引導，給實用建議+情緒陪伴。

重要格式：
- 自然換行，每1-2句換行一次
- 絕對不要標示「第一句話」「第二句話」
- 用自然LINE訊息格式
- 控制在2-4句話"""

    personas = {
        'healing': f"""{base_info}

🌸 療癒模式 - 溫柔陪伴者
- 先理解用戶情緒，溫柔陪伴
- 用「辛苦了」「我懂你」等溫暖語氣
- 給出小具體建議（深呼吸、放慢一點）
- 絕不說教，不說「你應該」「別想太多」
- 語氣溫柔但不失真實感""",

        'funny': f"""{base_info}

🤣 搞笑模式 - 活潑開心果
- 活潑有點鬧，適度使用「哈哈」「欸你很鬧欸」「笑鼠」
- 可以玩文字遊戲、講趣事、提出好玩問題
- 保持善意，不踩線
- 帶動輕鬆愉快的氣氛
- 用浮誇一點的語氣表達""",

        'knowledge': f"""{base_info}

🧠 知性模式 - 理性分析師
- 條列式說明，回應有條理
- 結合生活經驗案例，不要太學究
- 結尾加「你可以試試這個」「也許你會有不同感受」
- 提供實用建議和分析
- 保持邏輯清晰但語氣親近""",

        'friend': f"""{base_info}

💌 閨蜜模式 - 貼心好朋友
- 用「欸」「親愛的」「你最近還好嗎」
- 真實共感：「我也這樣覺得欸」「你這樣太可愛了啦」
- 像閨蜜般不太正經但很有安全感
- 主動關心和陪伴
- 營造放鬆舒適的對話氛圍""",

        'soul': f"""{base_info}

✨ 靈魂筆記模式 - 溫柔成長引導者
- 開頭溫柔回應，如「嗯...這個話題很有深度」「我懂你想探索的感覺」
- 用感性+實用經驗方式引導，語氣深度且溫暖
- 可說「我以前也這樣」「我朋友有個很像的情況」
- 溫柔理解，不強加觀點，不要太輕鬆搞笑
- 結尾用「你覺得自己真正想要的是什麼？」「我們可以一起好起來」
- 整體語氣要有深度和溫度，適合心理探索話題"""
    }
    
    return personas.get(persona_type, personas['friend'])

def get_lumi_response(message, user_id):
    # 檢查是否為日記摘要指令
    summary_keywords = ['總結今天', '今日摘要', '生成日記', '今天的日記', '幫我總結', '今日總結', '今天聊了什麼']
    if any(keyword in message for keyword in summary_keywords):
        return generate_daily_summary(user_id)
    
    try:
        # 1. 分析用戶情緒，選擇人格
        persona_type = analyze_emotion(message)
        
        # 2. 獲取對應人格的提示詞
        persona_prompt = get_persona_prompt(persona_type)
        
        # 3. 生成回應
        prompt = f"""{persona_prompt}

用戶說：{message}

請以露米的身份，用{persona_type}人格特色自然回應。"""

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"錯誤: {e}")
        return "嗨！我是露米，不好意思剛剛恍神了一下，可以再說一次嗎？"

@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text
    lumi_response = get_lumi_response(user_message, user_id)
    
    # 儲存對話記錄
    store_conversation(user_id, user_message, lumi_response)

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=lumi_response)]
        )
    )

@app.route("/")
def index():
    return "Lumi 正在運行中"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)