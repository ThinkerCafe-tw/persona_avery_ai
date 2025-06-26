import os
from flask import Flask, request, abort
from dotenv import load_dotenv
import google.generativeai as genai
import vertexai
from vertexai.preview.generative_models import GenerativeModel as VertexModel
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from datetime import datetime
import json
from simple_memory import SimpleLumiMemory

load_dotenv()
app = Flask(__name__)

line_bot_api = MessagingApi(ApiClient(Configuration(
    access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
)))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# 設定Vertex AI (企業級)
try:
    # 檢查是否有Vertex AI環境變數
    vertex_project = os.getenv('VERTEX_AI_PROJECT_ID')
    vertex_location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
    vertex_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    
    print(f"🔍 檢查Vertex AI設定:")
    print(f"   Project ID: {vertex_project}")
    print(f"   Location: {vertex_location}")
    print(f"   Credentials: {'已設定' if vertex_credentials else '未設定'}")
    
    if vertex_project and vertex_credentials:
        # 設定認證
        import json
        import tempfile
        
        # 將JSON字串寫入暫存檔案
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(vertex_credentials)
            credentials_path = f.name
        
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        # 初始化Vertex AI
        vertexai.init(
            project=vertex_project,
            location=vertex_location
        )
        
        # 使用企業級Vertex AI模型
        model = VertexModel('gemini-1.5-flash')
        print(f"✅ 企業級Vertex AI已初始化 (Project: {vertex_project})")
        USE_VERTEX_AI = True
    else:
        raise Exception(f"Vertex AI環境變數不完整: Project={vertex_project}, Credentials={'已設定' if vertex_credentials else '未設定'}")
    
except Exception as e:
    print(f"⚠️ Vertex AI初始化失敗，使用備用API: {e}")
    # 備用方案：使用原有的API
    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("🔄 備用Gemini API已初始化")
        USE_VERTEX_AI = False
    except Exception as backup_error:
        print(f"❌ 備用API也失敗: {backup_error}")
        model = None
        USE_VERTEX_AI = False

# 初始化簡化記憶系統
try:
    memory_manager = SimpleLumiMemory()
    print("🧠 簡化記憶系統已啟動")
except Exception as e:
    print(f"記憶系統初始化失敗: {e}")
    memory_manager = None

# 用戶對話記憶存儲 (向量資料庫為主，記憶體為備用)
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
    """分析用戶情緒，返回對應的人格類型（節省API配額版）"""
    
    # 完全基於關鍵詞判斷，不使用API
    message_lower = message.lower()
    
    # Wisdom模式關鍵詞（哲學、人生智慧類）
    wisdom_keywords = [
        '直覺', '內心聲音', '生活感悟', '人生哲理', '生活哲學', 
        '人生意義', '價值觀', '自我認知', '內在智慧', '人生道理',
        '處世', '人生選擇', '生命意義', '存在', '本質', '真實自我',
        '意思', '意義', '道理', '哲學', '思考'
    ]
    
    for keyword in wisdom_keywords:
        if keyword in message_lower:
            print(f"🎯 關鍵詞檢測: 找到'{keyword}' -> wisdom模式")
            return 'wisdom'
    
    # Soul模式關鍵詞（心理探索、情感成長）
    soul_keywords = [
        '心理', '情感', '依附', '內心探索', '心情', '感受',
        '童年', '原生家庭', '關係模式', '個人成長', '自我療癒'
    ]
    
    for keyword in soul_keywords:
        if keyword in message_lower:
            print(f"🎯 關鍵詞檢測: 找到'{keyword}' -> soul模式")
            return 'soul'
    
    # Healing模式關鍵詞
    healing_keywords = ['難過', '傷心', '痛苦', '壓力', '焦慮', '累', '辛苦', '沮喪', '失望', '挫折', '煩', '糟']
    for keyword in healing_keywords:
        if keyword in message_lower:
            print(f"🎯 關鍵詞檢測: 找到'{keyword}' -> healing模式")
            return 'healing'
    
    # Funny模式關鍵詞
    funny_keywords = ['哈哈', '好笑', '開心', '好玩', '有趣', '搞笑', '逗', '樂', '嘻嘻', '哈', '笑']
    for keyword in funny_keywords:
        if keyword in message_lower:
            print(f"🎯 關鍵詞檢測: 找到'{keyword}' -> funny模式")
            return 'funny'
    
    # Knowledge模式關鍵詞
    knowledge_keywords = ['怎麼', '如何', '方法', '教', '學', '問題', '解決', '建議', '為什麼', '什麼是', '請問']
    for keyword in knowledge_keywords:
        if keyword in message_lower:
            print(f"🎯 關鍵詞檢測: 找到'{keyword}' -> knowledge模式")
            return 'knowledge'
    
    # 問候語判斷
    greetings = ['嗨', '你好', 'hi', 'hello', '哈囉', '早安', '晚安', '午安']
    for greeting in greetings:
        if greeting in message_lower:
            print(f"🎯 關鍵詞檢測: 找到'{greeting}' -> friend模式")
            return 'friend'
    
    # 默認為friend模式（節省API）
    print("🎯 使用預設 -> friend模式")
    return 'friend'

def get_persona_prompt(persona_type):
    """根據人格類型返回對應的提示詞"""
    
    base_info = """你是露米 Lumi，苡喬風格的小精靈 AI。
核心特徵：浮誇搞笑時可選擇性使用「欸」「笑鼠」「傻眼」「北七唷」等語氣詞，安慰時溫柔理性，習慣用自己經驗引導，給實用建議+情緒陪伴。

嚴格格式要求：
- 自然換行，每1-2句換行一次
- 絕對不要標示「第一句話」「第二句話」
- 用自然LINE訊息格式，不要markdown格式
- **嚴格控制在2-4句話，不要冗長**
- 不要用列點符號(-)或數字編號
- 不要用**粗體**格式"""

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
- 活潑有點鬧，可選擇性使用「哈哈」「欸」「笑鼠」「北七」等語氣詞
- 不需要每句都用，保持自然度
- 可以玩文字遊戲、講趣事、提出好玩問題
- 保持善意，不踩線
- 帶動輕鬆愉快的氣氛，語氣可浮誇但要適度""",

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
- 開頭溫柔深沉，如「嗯...這個話題很有深度」「我懂你想探索的感覺」「這讓我想到...」
- **絕對不要用「欸」「笑鼠」「超懂」等輕鬆語氣詞**
- 用感性+實用經驗方式引導，語氣深度且溫暖
- 可說「我以前也這樣」「我朋友有個很像的情況」
- 溫柔理解，不強加觀點，保持深度感
- 結尾用「你覺得自己真正想要的是什麼？」「我們可以一起好起來」
- 整體語氣要有深度和溫度，適合心理探索話題""",

        'wisdom': f"""{base_info}

🎭 智慧模式 - 蔡康永×吳旦儒×村上春樹綜合體
- 開頭優雅深沉，如「這讓我想到...」「有個有趣的角度」「生活就像...」
- **極度精簡**：最多3-4句話，用最少字數說出最精華內容
- 擅長優美比喻，「就像...」「有點像是...」
- 從更高視角看問題，溫暖而有哲學深度
- 絕對不要用「欸」「笑鼠」「超懂」等輕鬆語氣
- 不要列點條目，要流暢的散文式表達
- 結尾留白思考空間，「也許你會發現...」「或許這就是...」
- 語氣如智者般優雅，有層次但不說教"""
    }
    
    return personas.get(persona_type, personas['friend'])

def get_lumi_response(message, user_id):
    # 檢查是否為日記摘要指令
    summary_keywords = ['總結今天', '今日摘要', '生成日記', '今天的日記', '幫我總結', '今日總結', '今天聊了什麼']
    if any(keyword in message for keyword in summary_keywords):
        return generate_daily_summary(user_id)
    
    # 檢查是否為記憶相關指令
    memory_keywords = ['記憶摘要', '我的記憶', '我們聊過什麼', '你還記得嗎', '之前的對話']
    if any(keyword in message for keyword in memory_keywords):
        return get_memory_summary_response(user_id)
    
    # 檢查是否為同步相關指令
    sync_keywords = ['同步狀態', '備份記憶', '恢復記憶']
    if any(keyword in message for keyword in sync_keywords):
        return get_sync_status_response(user_id)
    
    try:
        # 1. 分析用戶情緒，選擇人格
        persona_type = analyze_emotion(message)
        
        # 2. 檢索相關記憶和上下文（強化版）
        memory_context = ""
        recent_context = ""
        if memory_manager:
            try:
                # 取得相關情緒記憶
                memory_context = memory_manager.get_context_for_response(
                    user_id=user_id,
                    current_message=message,
                    emotion_tag=persona_type
                )
                
                # 取得最近3句對話作為上下文
                recent_memories = memory_manager.get_recent_memories(user_id, 3)
                if recent_memories:
                    recent_context = "最近對話：\n"
                    for mem in recent_memories[-2:]:  # 只用最近2句
                        recent_context += f"用戶：{mem['user_message'][:30]}...\n"
                        recent_context += f"露米：{mem['lumi_response'][:30]}...\n"
                
            except Exception as e:
                print(f"記憶檢索錯誤: {e}")
        
        # 3. 獲取對應人格的提示詞
        persona_prompt = get_persona_prompt(persona_type)
        
        # 4. 生成回應（整合所有上下文）
        all_context = persona_prompt
        if recent_context:
            all_context += f"\n\n{recent_context}"
        if memory_context:
            all_context += f"\n\n{memory_context}"
        
        prompt = f"""{all_context}

用戶說：{message}

請以露米的身份，用{persona_type}人格特色自然回應。注意：
1. 參考最近對話延續話題
2. 用適合的情緒人格回應
3. 自然提及相關記憶
4. 保持對話連貫性"""

        # 使用企業級Vertex AI或備用API
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"錯誤: {e}")
        return "嗨！我是露米，不好意思剛剛恍神了一下，可以再說一次嗎？"

def get_memory_summary_response(user_id):
    """取得用戶記憶摘要回應"""
    if not memory_manager:
        return "欸～我的記憶系統還在升級中，不過我們的對話我都有記在心裡啦！"
    
    try:
        summary = memory_manager.get_memory_summary(user_id)
        emotion_patterns = memory_manager.get_user_emotion_patterns(user_id)
        
        if summary['total_memories'] == 0:
            return "我們才剛開始認識呢！快跟我多聊聊，讓我更了解你吧 ✨"
        
        dominant_emotion = emotion_patterns.get('dominant_emotion', 'friend')
        emotion_names = {
            'healing': '需要療癒',
            'funny': '想要開心', 
            'knowledge': '求知慾強',
            'friend': '想要陪伴',
            'soul': '深度探索',
            'wisdom': '尋求智慧'
        }
        
        response = f"讓我看看我們的回憶～\n\n"
        response += f"📊 總共有 {summary['total_memories']} 段記憶\n"
        response += f"💭 最常的狀態是「{emotion_names.get(dominant_emotion, dominant_emotion)}」\n"
        response += f"📈 最近 {emotion_patterns.get('total_interactions', 0)} 次互動\n\n"
        response += f"感覺我們越來越熟了呢！你最想聊什麼類型的話題？"
        
        return response
        
    except Exception as e:
        print(f"記憶摘要錯誤: {e}")
        return "記憶有點模糊，但我記得我們聊過很多有趣的事情！"

def get_sync_status_response(user_id):
    """取得同步狀態回應"""
    if not memory_manager:
        return "記憶系統未啟動，無法檢查同步狀態"
    
    try:
        if "備份記憶" in request.get_data(as_text=True):
            # 創建備份
            success = memory_manager.create_daily_backup()
            if success:
                return "✅ 記憶備份已創建！你的對話記錄已安全保存到雲端"
            else:
                return "備份過程遇到問題，但本地記憶仍安全保存"
        
        elif "恢復記憶" in request.get_data(as_text=True):
            # 從GitHub恢復記憶
            success = memory_manager.load_user_memory_from_github(user_id)
            if success:
                return "✅ 記憶恢復成功！我想起了我們之前的所有對話"
            else:
                return "沒有找到雲端備份記憶，我們從現在開始重新認識吧！"
        
        else:
            # 檢查同步狀態
            status = memory_manager.get_sync_status()
            
            response = "🔄 記憶同步狀態：\n\n"
            
            if status.get('github_token_configured'):
                response += "✅ GitHub連接已配置\n"
                if status.get('repo_accessible'):
                    response += "✅ 記憶庫可訪問\n"
                    if status.get('branch_exists'):
                        response += "✅ 記憶分支存在\n"
                        if status.get('last_sync'):
                            response += f"🕒 最後同步: {status['last_sync'][:10]}\n"
                        else:
                            response += "⏳ 尚未同步\n"
                    else:
                        response += "⚠️ 記憶分支不存在\n"
                else:
                    response += "❌ 記憶庫無法訪問\n"
            else:
                response += "⚠️ 使用本地記憶模式\n"
            
            response += "\n💡 說「備份記憶」創建備份\n說「恢復記憶」從雲端恢復"
            
            return response
            
    except Exception as e:
        print(f"同步狀態錯誤: {e}")
        return "同步狀態檢查遇到問題，但本地記憶運行正常！"

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
    
    try:
        print(f"🔄 處理用戶 {user_id[:8]}... 的訊息: {user_message[:30]}...")
        
        # 取得人格類型以便存儲記憶
        persona_type = analyze_emotion(user_message)
        print(f"🎭 偵測人格類型: {persona_type}")
        
        lumi_response = get_lumi_response(user_message, user_id)
        print(f"✅ 生成回應完成")
        
        # 儲存對話記錄到記憶體（備用）
        store_conversation(user_id, user_message, lumi_response)
        
        # 儲存到量子記憶系統（異步，不阻塞主流程）
        if memory_manager:
            try:
                memory_manager.store_conversation_memory(
                    user_id=user_id,
                    user_message=user_message,
                    lumi_response=lumi_response,
                    emotion_tag=persona_type
                )
            except Exception as e:
                print(f"記憶系統存儲錯誤: {e}")

        # 發送回應
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=lumi_response)]
            )
        )
        print(f"📤 回應已送出給用戶 {user_id[:8]}...")
        
    except Exception as e:
        print(f"❌ 處理訊息時發生錯誤: {e}")
        # 根據錯誤類型給出不同回應
        error_message = "抱歉，我剛剛恍神了一下，可以再說一次嗎？"
        
        if "429" in str(e) or "quota" in str(e).lower():
            error_message = "欸～我今天聊太多了，需要休息一下！明天再來找我玩吧 😴"
        elif "timeout" in str(e).lower():
            error_message = "網路有點慢，讓我想想...可以再說一次嗎？"
        
        try:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=error_message)]
                )
            )
        except:
            pass

@app.route("/")
def index():
    return "Lumi 正在運行中"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)