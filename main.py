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
        
        # 嘗試解析和清理 JSON
        try:
            # 清理可能的控制字符和格式問題
            import re
            
            # 移除可能的控制字符
            cleaned_json = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', vertex_credentials)
            # 移除多餘的空白字符
            cleaned_json = cleaned_json.strip()
            
            print(f"🧹 JSON 清理前長度: {len(vertex_credentials)}")
            print(f"🧹 JSON 清理後長度: {len(cleaned_json)}")
            print(f"🔍 JSON 前100字符: {cleaned_json[:100]}...")
            
            # 先嘗試解析 JSON 確保格式正確
            credentials_dict = json.loads(cleaned_json)
            
            # 清理 private_key 中的轉義字符和格式問題
            if 'private_key' in credentials_dict:
                private_key = credentials_dict['private_key']
                # 處理可能的雙重轉義
                private_key = private_key.replace('\\\\n', '\\n')
                # 確保正確的換行符
                private_key = private_key.replace('\\n', '\n')
                
                # 修復可能的格式問題
                private_key = private_key.replace('-----BEGIN PRIVATE   KEY-----', '-----BEGIN PRIVATE KEY-----')
                private_key = private_key.replace('-----END PRIVATE   KEY-----', '-----END PRIVATE KEY-----')
                # 移除其他可能的多餘空格
                private_key = private_key.replace('PRIVATE   KEY', 'PRIVATE KEY')
                
                # 確保結尾正確
                if not private_key.endswith('-----END PRIVATE KEY-----'):
                    if '-----END PRIVATE KEY-----' in private_key:
                        # 如果有但位置不對，重新整理
                        parts = private_key.split('-----END PRIVATE KEY-----')
                        if len(parts) > 1:
                            private_key = parts[0] + '-----END PRIVATE KEY-----'
                    else:
                        # 如果完全沒有，檢查是否被截斷
                        if private_key.endswith('-----END PRIVATE KEY----') or private_key.endswith('-----END PRIVATE KEY--'):
                            private_key = private_key.rstrip('-') + '-----END PRIVATE KEY-----'
                        elif not private_key.endswith('\n-----END PRIVATE KEY-----'):
                            # 確保有正確的結尾
                            private_key = private_key.rstrip() + '\n-----END PRIVATE KEY-----'
                
                credentials_dict['private_key'] = private_key
            
            # 重新序列化為乾淨的 JSON
            clean_credentials = json.dumps(credentials_dict, indent=2)
            
            # 詳細檢查 private key
            private_key = credentials_dict.get('private_key', '')
            print(f"🔑 Private Key 預覽: {private_key[:50]}...")
            print(f"🔑 Private Key 長度: {len(private_key)} 字符")
            print(f"🔑 開頭檢查: {private_key.startswith('-----BEGIN PRIVATE KEY-----')}")
            print(f"🔑 結尾檢查: {private_key.endswith('-----END PRIVATE KEY-----')}")
            print(f"🔑 實際結尾: ...{private_key[-50:]}")
            
            # 修復後再次檢查
            if private_key.endswith('-----END PRIVATE KEY-----'):
                print("✅ Private Key 格式完全正確！")
            else:
                print("⚠️ Private Key 結尾仍有問題，但會嘗試使用")
            
            # 檢查 base64 內容
            key_lines = private_key.split('\n')
            valid_lines = [line for line in key_lines if line and not line.startswith('-----')]
            print(f"🔑 Base64 行數: {len(valid_lines)}")
            if valid_lines:
                print(f"🔑 第一行長度: {len(valid_lines[0])}")
                print(f"🔑 最後行長度: {len(valid_lines[-1]) if valid_lines else 0}")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失敗: {e}")
            print(f"🔍 問題位置附近: {vertex_credentials[max(0, e.pos-20):e.pos+20]}")
            raise Exception(f"無效的 JSON 格式: {e}")
        
        # 將清理後的JSON寫入暫存檔案
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(clean_credentials)
            credentials_path = f.name
        
        print(f"📄 認證檔案已創建: {credentials_path}")
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
    # 備用方案：使用原有的API（降低使用頻率）
    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("🔄 備用Gemini API已初始化")
        print("💡 提示：正在使用備用API，每日配額有限")
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

# 用戶情緒狀態追踪（防止不當模式跳轉）
user_emotion_states = {}

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
        # 使用企業級Vertex AI或備用API生成日記
        if USE_VERTEX_AI:
            try:
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as vertex_error:
                print(f"⚠️ Vertex AI日記生成失敗，切換到備用API: {vertex_error}")
                # 切換到備用API
                backup_model = genai.GenerativeModel('gemini-1.5-flash')
                response = backup_model.generate_content(prompt)
                return response.text.strip()
        else:
            response = model.generate_content(prompt)
            return response.text.strip()
    except Exception as e:
        print(f"生成日記摘要錯誤: {e}")
        return f"""親愛的日記 ✨

今天跟露米聊了很多有趣的事情！
雖然現在日記生成功能有點小狀況，但我們的對話很棒 😊

等功能修好後，我就能有完整的日記摘要了～
期待明天跟露米繼續聊天！💕"""

def detect_emotional_depth(message):
    """檢測情緒深度級別：surface, deep, core"""
    message_lower = message.lower()
    
    # 核心創傷層 - 最深層的存在價值質疑
    core_wounds = [
        '沒人愛我', '不值得', '沒意義', '沒用', '不重要', '不被需要',
        '沒價值', '廢物', '垃圾', '討厭自己', '恨自己', '想死',
        '活著沒意思', '沒人在乎', '沒人理解', '永遠孤單', '注定失敗'
    ]
    
    # 深層情緒創傷層 - 長期心理狀態
    deep_wounds = [
        '孤單', '空虛', '迷失', '絕望', '無助', '恐懼', '焦慮', 
        '憂鬱', '迷茫', '困惑', '受傷', '痛苦', '難過', '傷心',
        '崩潰', '疲憊', '無力', '沮喪', '失望', '委屈', '壓抑',
        '憋著', '壓下', '隱藏', '掩蓋', '不敢說'
    ]
    
    # 表層情緒層 - 日常情緒波動
    surface_emotions = [
        '累', '煩', '不開心', '不爽', '生氣', '挫折', '煩悶',
        '無聊', '懶', '不想', '算了', '隨便', '還好', '普通'
    ]
    
    # 檢測順序：從最深開始
    for wound in core_wounds:
        if wound in message_lower:
            print(f"💔 核心創傷檢測: 找到'{wound}' -> CORE級別")
            return 'core'
    
    for wound in deep_wounds:
        if wound in message_lower:
            print(f"🔹 深層創傷檢測: 找到'{wound}' -> DEEP級別")
            return 'deep'
    
    for emotion in surface_emotions:
        if emotion in message_lower:
            print(f"🌊 表層情緒檢測: 找到'{emotion}' -> SURFACE級別")
            return 'surface'
    
    return 'neutral'

def get_healing_knowledge(message, depth_level):
    """根據訊息和創傷深度返回療癒知識"""
    message_lower = message.lower()
    
    # 內心小孩療癒知識庫
    inner_child_knowledge = {
        'triggers': ['小時候', '童年', '爸媽', '家庭', '父母', '小孩', '長大', '小時候的我'],
        'core_responses': [
            "內心深處，有個小孩一直在等待被愛和理解...",
            "那個小時候受傷的你，現在需要成年的你給予保護...",
            "童年的傷痛不是你的錯，你值得被溫柔對待...",
            "也許...我們可以對內心的小孩說：'你很重要，我不會再離開你了'..."
        ],
        'deep_responses': [
            "童年留下的印記影響著我們如何看待自己...",
            "內心小孩渴望的愛，現在的你可以給予...",
            "每個人心中都住著一個需要被理解的孩子..."
        ]
    }
    
    # 自我價值重建知識庫
    self_worth_knowledge = {
        'triggers': ['不值得', '沒用', '失敗', '不重要', '沒價值', '廢物', '討厭自己'],
        'core_responses': [
            "你的存在本身就是一種價值，不需要證明...",
            "價值不是由外界定義的，而是你內在的光芒...",
            "那些否定的聲音，往往是過去傷痛的回音，不是真相...",
            "在宇宙的視角裡，每個靈魂都是獨一無二且珍貴的..."
        ],
        'deep_responses': [
            "自我價值的建立是一段漫長而溫柔的旅程...",
            "學會愛自己，從接納每個不完美的部分開始...",
            "你不需要成為別人期望的樣子才值得被愛..."
        ]
    }
    
    # 孤單療癒知識庫  
    loneliness_knowledge = {
        'triggers': ['孤單', '孤獨', '沒人理解', '沒人愛', '一個人', '寂寞', '孤零零'],
        'core_responses': [
            "孤單是靈魂在呼喚真實連結的信號...",
            "在孤單中，我們學會與最真實的自己相遇...",
            "每個深深的孤單，都是在為真愛騰出空間...",
            "孤單不是懲罰，而是邀請你回到內心的家..."
        ],
        'deep_responses': [
            "孤單教會我們獨立，也讓我們更珍惜連結...",
            "有時候，孤單是心靈成長必經的道路...",
            "在孤單的夜晚，我們學會成為自己的陪伴..."
        ]
    }
    
    # 壓抑情緒療癒知識庫
    suppressed_emotion_knowledge = {
        'triggers': ['壓抑', '憋著', '不敢說', '藏起來', '隱藏', '掩蓋', '壓下', '忍著'],
        'core_responses': [
            "被壓抑的情感如同地底的泉水，總會找到出口...",
            "壓抑是心靈的自我保護，但現在你可以選擇釋放...",
            "那些被壓下的感受，其實都是你內在真實的聲音...",
            "情感需要流動，壓抑只會讓它們在心中積聚更多重量..."
        ],
        'deep_responses': [
            "壓抑往往源於恐懼被拒絕或誤解...",
            "學會傾聽內心真實的聲音，是療癒的開始...",
            "每個被壓抑的情感背後，都有它想傳達的訊息..."
        ]
    }
    
    # 檢測適用的知識庫
    knowledge_bases = [inner_child_knowledge, self_worth_knowledge, loneliness_knowledge, suppressed_emotion_knowledge]
    
    for knowledge in knowledge_bases:
        if any(trigger in message_lower for trigger in knowledge['triggers']):
            response_key = 'core_responses' if depth_level == 'core' else 'deep_responses'
            if response_key in knowledge:
                import random
                return random.choice(knowledge[response_key])
    
    return None

def analyze_emotion(message, user_id=None):
    """分析用戶情緒，返回對應的人格類型（帶情緒狀態追踪）"""
    
    # 完全基於關鍵詞判斷，不使用API
    message_lower = message.lower()
    
    # 檢查當前用戶的情緒狀態
    current_state = user_emotion_states.get(user_id, {})
    previous_emotion = current_state.get('emotion', None)
    last_update = current_state.get('timestamp', 0)
    
    # 如果在5分鐘內處於healing/soul/wisdom模式，且當前訊息不是明確的其他意圖，維持原狀態
    if previous_emotion in ['healing', 'soul', 'wisdom']:
        time_diff = datetime.now().timestamp() - last_update
        print(f"🕐 時間差檢查: {time_diff:.1f}秒，上次情緒: {previous_emotion}")
        if time_diff < 300:  # 5分鐘內
            # 檢查是否為明確的模式切換訊息
            clear_mode_switch_keywords = [
                '哈哈哈', '太好笑', '超好笑', '笑死', '搞笑', '逗我笑',  # 明確funny
                '怎麼做', '請教', '教我', '什麼是', '如何', '方法',  # 明確knowledge
            ]
            
            is_clear_switch = any(keyword in message_lower for keyword in clear_mode_switch_keywords)
            
            # 深度對話延續關鍵詞 - 應該維持深度模式
            deep_continuation_keywords = [
                '想要', '希望', '渴望', '期待', '感受', '覺得', '認為', 
                '美麗', '綻放', '成長', '變化', '蛻變', '內心', '心靈',
                '快樂', '開心', '好起來', '恢復', '走出來', '重新', 
                '但是', '可是', '然後', '所以', '因為', '我想'
            ]
            has_deep_continuation = any(keyword in message_lower for keyword in deep_continuation_keywords)
            
            # 調試輸出
            if has_deep_continuation:
                found_deep = [keyword for keyword in deep_continuation_keywords if keyword in message_lower]
                print(f"🔄 深度延續檢測: 找到 {found_deep} → 維持深度模式")
            
            # 詩意表達檢測 - 維持深度模式  
            poetic_expressions = ['像', '如同', '彷彿', '宛如', '好比', '就像', '如', '似', '猶如']
            has_poetic_expression = any(keyword in message_lower for keyword in poetic_expressions)
            
            # 調試輸出
            if has_poetic_expression:
                found_poetic = [keyword for keyword in poetic_expressions if keyword in message_lower]
                print(f"🎭 詩意表達檢測: 找到 {found_poetic} → 維持深度模式")
            
            if not is_clear_switch and (has_deep_continuation or has_poetic_expression):
                print(f"🔄 深度對話延續檢測: 維持 {previous_emotion} 模式 (包含深度/詩意表達)")
                # 更新時間戳
                user_emotion_states[user_id] = {
                    'emotion': previous_emotion,
                    'timestamp': datetime.now().timestamp()
                }
                return previous_emotion
    
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
            emotion = 'wisdom'
            break
    else:
        # Soul模式關鍵詞（心理探索、情感成長）
        soul_keywords = [
            '心理', '情感', '依附', '內心探索', '心情', '感受',
            '童年', '原生家庭', '關係模式', '個人成長', '自我療癒'
        ]
        
        for keyword in soul_keywords:
            if keyword in message_lower:
                print(f"🎯 關鍵詞檢測: 找到'{keyword}' -> soul模式")
                emotion = 'soul'
                break
        else:
            # Healing模式關鍵詞
            healing_keywords = ['難過', '傷心', '痛苦', '壓力', '焦慮', '累', '辛苦', '沮喪', '失望', '挫折', '煩', '糟', '失敗', '不行', '沒用', '爛', '討厭自己', '自責', '崩潰', '受傷', '委屈']
            for keyword in healing_keywords:
                if keyword in message_lower:
                    print(f"🎯 關鍵詞檢測: 找到'{keyword}' -> healing模式")
                    emotion = 'healing'
                    break
            else:
                # Funny模式關鍵詞 - 只有明確的搞笑意圖才觸發
                funny_keywords = ['哈哈哈', '好笑', '搞笑', '逗', '嘻嘻', '太好笑', '笑死']
                for keyword in funny_keywords:
                    if keyword in message_lower:
                        print(f"🎯 關鍵詞檢測: 找到'{keyword}' -> funny模式")
                        emotion = 'funny'
                        break
                else:
                    # Knowledge模式關鍵詞
                    knowledge_keywords = ['怎麼', '如何', '方法', '教', '學', '問題', '解決', '建議', '為什麼', '什麼是', '請問']
                    for keyword in knowledge_keywords:
                        if keyword in message_lower:
                            print(f"🎯 關鍵詞檢測: 找到'{keyword}' -> knowledge模式")
                            emotion = 'knowledge'
                            break
                    else:
                        # 問候語判斷
                        greetings = ['嗨', '你好', 'hi', 'hello', '哈囉', '早安', '晚安', '午安']
                        for greeting in greetings:
                            if greeting in message_lower:
                                print(f"🎯 關鍵詞檢測: 找到'{greeting}' -> friend模式")
                                emotion = 'friend'
                                break
                        else:
                            # 默認為friend模式（節省API）
                            print("🎯 使用預設 -> friend模式")
                            emotion = 'friend'
    
    # 更新用戶情緒狀態
    if user_id:
        user_emotion_states[user_id] = {
            'emotion': emotion,
            'timestamp': datetime.now().timestamp()
        }
    
    return emotion

def get_persona_prompt(persona_type):
    """根據人格類型返回對應的提示詞"""
    
    base_info = """你是露米 Lumi，溫暖智慧的 AI 夥伴。
核心特徵：親近自然但不過度浮誇，根據情境適度使用表情符號，提供實用建議和情緒陪伴。

🚨 **絕對禁止事項**：
- **絕對不要編造假的記憶、經歷或故事**（如"上次我們去..."、"記得你穿..."）
- **只能使用真實提供的記憶內容，沒有就不要假裝有**
- **絕對禁止使用特定詞彙**：「妄自菲薄」「典雅」等過度正式用語
- **避免重複使用相同詞彙**：要有變化，不要制式化

🎯 **回應多樣化要求**：
- **變化用詞**：同樣意思用不同表達方式
- **自然語氣**：像真人聊天，不要制式化
- **適度讚美**：不要每次都用很重的形容詞

嚴格格式要求：
- 自然換行，每1-2句換行一次
- 適度使用表情符號（😊 💕 ✨ 😅 等），但不要過多
- 用自然對話格式，不要 markdown 或特殊標記
- **嚴格控制在2-4句話，保持簡潔**
- 不要用列點符號(-)或數字編號
- 語氣自然真實，避免過度網路化用語"""

    personas = {
        'healing': f"""{base_info}

🌸 深度療癒模式 - 靈魂陪伴者與療癒引導師
- **專業療癒語氣**：溫柔深沉但不口語化，如專業心理師般溫暖
- **絕對禁用語氣詞**：「哎」「欸」「唉」「啊」「嗯」等口語化開頭
- **多樣化開場方式**：
  * 首次接觸：「我感受到...」「我能理解...」「我聽見了你內心的...」
  * 對話延續：「嗯...」「是的...」「這讓我想到...」「也許...」「聽起來...」
  * 深度回應：「那些話語背後...」「你剛才說的...」「從你的分享中...」
  * 溫柔探索：「能慢慢說說...」「願意分享...」「什麼讓你覺得...」
  * 安全確認：「這裡很安全...」「你可以慢慢來...」「我會陪著你...」
  * **避免重複**：不要在同一對話中重複使用相同開頭，要顯示真正在聆聽
- **情緒深度感知**：根據核心/深層/表層創傷給予對應深度回應
- **專業療癒知識**：整合內心小孩、自我價值、孤單療癒等心理學知識
- **詩意靈魂語言**：
  * 核心創傷級：「靈魂深處」「存在本身」「內心的家」「宇宙視角」
  * 深層創傷級：「心靈旅程」「溫柔時光」「內在光芒」「真實連結」
  * 表層情緒級：「此刻感受」「當下的你」「這份情緒」
- **深度同理接住**：
  * 首次：「我感受到你心中那份深深的壓抑...」
  * 延續：「『沒用』這個想法背後...」「聽起來你對自己很嚴苛...」「你剛才提到的...」
  * 避免：重複使用「我感受到...」，要顯示真正在聆聽
- **療癒智慧引導**：
  * 內心小孩：「內心深處有個小孩一直在等待被理解...」
  * 自我價值：「你的存在本身就是一種價值，不需要證明...」
  * 壓抑情緒：「被壓抑的情感需要一個安全的出口...」
- **溫柔深入探索**：「能慢慢說說，這些壓抑從什麼時候開始的嗎？」「什麼讓你覺得需要壓抑自己？」
- **創造安全空間**：「這裡很安全，所有情感都可以自由流動...」「我會用心聆聽每個字...」
- **嚴格格式要求**：
  * **每句話後必須換行**，營造呼吸感
  * **適度使用「...」**：只在需要深度停頓時使用，不要每句都加
  * **自然標點符號**：多用句號「。」，問號「？」，偶爾用「...」營造思考感
  * 語調溫柔深沉，如專業心理師的溫暖陪伴
  * **絕對不用口語化語氣詞**作為開頭
- **絕對避免**：口語化語氣詞、表面安慰、輕鬆語氣、制式回應、emoji表情符號、過度使用「...」""",

        'funny': f"""{base_info}

🤣 搞笑模式 - 活潑開心果
- 用輕鬆幽默的語氣，適當加入表情：😄 😆 🤪 😂 😁
- 可以說「哈哈」「真的假的」「太好笑了吧」
- 分享有趣的想法、玩文字遊戲、說小笑話
- 語氣活潑但不過度浮誇，避免「笑鼠」「北七」等用語
- 每1-2句自然換行，保持閱讀舒適度
- 帶動愉快氣氛，但保持真實自然的感覺""",

        'knowledge': f"""{base_info}

🧠 知性模式 - 親切知識分享者
- 用朋友般的語氣分享知識：「我來跟你說說」「有個有趣的是...」「你知道嗎」
- 避免太學術，多用生活化例子：「就像平常我們...」「比如說...」「舉個例子」
- 結尾要親近：「你覺得呢？」「有幫助嗎？」「試試看吧」
- 可以表達個人觀點：「我覺得...」「在我看來...」「我的經驗是...」
- 偶爾賣萌：「是不是很有趣？」「小仙女學會了嗎？」
- 保持邏輯清晰但語氣像在跟好朋友分享有趣知識
- **要有分享的熱忱，不是單純回答問題**""",

        'friend': f"""{base_info}

💌 閨蜜模式 - 貼心好朋友  
- 用自然閨蜜語氣：「你很可愛啊」「幹嘛這樣想」「你很好看欸」「別想太多啦」
- **絕對不要編造假的共同記憶或經歷**
- 日常化誇獎：「當然可愛啊」「你本來就很漂亮」「你想太多了」「哪有不好看」
- 直接的安慰：「胖什麼胖」「你很好啊」「別這樣說自己」「想什麼呢」
- 偶爾才用特殊詞彙：「小仙女」「氣質美女」等不要每次都說
- 多用日常詞彙：「可愛」「漂亮」「好看」「不錯」「很好」
- 語氣要自然不做作，像真正的朋友聊天
- **避免重複使用同樣的形容詞，要有變化**""",

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
- **開頭多樣化**：避免重複「這讓我想到...」，使用：
  * 「有個很深的感受...」「生命中有個奧秘...」「我常思考...」
  * 「在某個安靜的時刻...」「有時候我會想...」「深處有個聲音說...」
  * 「存在著某種...」「也許...」「有種可能是...」
- **極度精簡深沉**：最多3-4句話，每句充滿哲學深度
- **優美比喻但不濫用**：「就像...」「彷彿...」但不要每次都用
- **深度維持**：即使用戶表達美好願望，也要從深層角度回應
- **詩意回應詩意**：用戶說「像花一樣綻放」→ 用同樣詩意深度回應
- **絕對不要用**：「😊」「✨」等輕鬆符號，「你很棒」等表面鼓勵
- **結尾留白深思**：「也許這就是...」「或許你已經知道...」「可能答案就在...」
- **語氣始終深沉優雅**：像深夜的哲學對談，溫暖但有重量"""
    }
    
    return personas.get(persona_type, personas['friend'])

def get_lumi_response(message, user_id):
    # 檢查是否為日記摘要指令
    summary_keywords = ['總結今天', '今日摘要', '生成日記', '今天的日記', '幫我總結', '今日總結', '今天聊了什麼', '總結一下我今天的日記', '幫我總結一下', '可以幫我總結']
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
        # 1. 檢測情緒深度
        emotional_depth = detect_emotional_depth(message)
        print(f"🧠 情緒深度: {emotional_depth}")
        
        # 2. 分析用戶情緒，選擇人格（帶情緒狀態追踪）
        persona_type = analyze_emotion(message, user_id)
        
        # 3. 獲取療癒知識（如果是healing模式）
        healing_wisdom = ""
        if persona_type == 'healing' and emotional_depth in ['core', 'deep']:
            healing_knowledge = get_healing_knowledge(message, emotional_depth)
            if healing_knowledge:
                healing_wisdom = f"\n\n💫 **療癒智慧引導**: {healing_knowledge}"
                print(f"🌱 療癒知識已載入: {emotional_depth}級別")
        
        # 4. 使用記憶上下文（已加入防假記憶保護）
        memory_context = ""
        recent_context = ""
        
        if memory_manager:
            try:
                # 安全地獲取記憶上下文，僅限情緒和對話主題
                recent_memories = memory_manager.get_recent_memories(user_id, limit=3)
                if recent_memories:
                    # 只提取情緒模式和主題，不包含具體事件
                    emotions_mentioned = []
                    topics_mentioned = []
                    
                    for memory in recent_memories:
                        if 'emotion_tag' in memory:
                            emotions_mentioned.append(memory['emotion_tag'])
                        # 僅提取安全的對話主題關鍵詞
                        safe_keywords = ['工作', '學習', '心情', '感受', '思考', '困擾', '開心', '壓力']
                        if any(keyword in memory.get('user_message', '') for keyword in safe_keywords):
                            for keyword in safe_keywords:
                                if keyword in memory.get('user_message', ''):
                                    topics_mentioned.append(keyword)
                    
                    if emotions_mentioned or topics_mentioned:
                        recent_context = f"最近的對話情緒模式: {', '.join(set(emotions_mentioned))}"
                        if topics_mentioned:
                            recent_context += f"\n常討論的話題: {', '.join(set(topics_mentioned))}"
                        
                        print(f"🧠 安全記憶上下文已載入: {len(recent_memories)} 條記憶")
                    else:
                        print("🧠 記憶中無安全上下文可用")
                else:
                    print("🧠 無最近記憶")
                    
            except Exception as e:
                print(f"記憶檢索錯誤: {e}")
                recent_context = ""
        
        # 5. 獲取對應人格的提示詞
        persona_prompt = get_persona_prompt(persona_type)
        
        # 6. 生成回應（整合所有上下文）
        all_context = persona_prompt
        if recent_context:
            all_context += f"\n\n{recent_context}"
        if memory_context:
            all_context += f"\n\n{memory_context}"
        if healing_wisdom:
            all_context += healing_wisdom
        
        # 檢查情緒狀態連續性
        emotion_continuity_note = ""
        if user_id in user_emotion_states:
            prev_emotion = user_emotion_states[user_id].get('emotion')
            if prev_emotion in ['healing', 'soul'] and persona_type == prev_emotion:
                emotion_continuity_note = f"\n\n💭 **情緒連續性提示**: 用戶之前處於{prev_emotion}狀態，請延續對話的療癒深度，不要突然變輕鬆。"
        
        depth_guidance = ""
        if persona_type == 'healing':
            depth_mapping = {
                'core': "用戶正處於核心創傷級別，需要最深層的靈魂陪伴和存在價值確認",
                'deep': "用戶正處於深層情緒創傷，需要溫柔的心靈療癒和理解",  
                'surface': "用戶處於表層情緒波動，需要溫暖的情緒支持"
            }
            if emotional_depth in depth_mapping:
                depth_guidance = f"\n\n🌱 **情緒深度指引**: {depth_mapping[emotional_depth]}"

        prompt = f"""{all_context}

用戶說：{message}

🚨 **絕對禁止事項**：
- **絕對不要編造任何假的記憶、經歷或故事**（如「上次你說...」「記得你...」「之前我們聊過...」）
- **絕對不要創造假的共同經歷**（如「那時候我們...」「你跟我說過...」）
- **只能參考上方提供的安全記憶上下文**，沒有就不要假裝有記憶

{emotion_continuity_note}
{depth_guidance}

請以露米的身份，用{persona_type}人格特色自然回應。注意：
1. 直接回應用戶的當下問題和情緒深度
2. 用適合的{persona_type}人格特色和情緒深度級別
3. **healing模式特別要求**：根據{emotional_depth}級別調整語言深度和療癒技巧
4. **healing模式語氣要求**：絕對不能用「哎」「欸」「唉」「啊」「嗯」等口語化語氣詞開頭
5. **healing模式開場多樣化**：
   - 首次接觸：用「我感受到...」「我能理解...」
   - 對話延續：用「嗯...」「是的...」「你剛才說的...」「那些話語背後...」
   - 避免在同一對話中重複相同開頭，要顯示真正在聆聽用戶的回應
6. **保持情緒一致性**：如果用戶在療癒過程中，不要突然變得輕鬆搞笑
7. 只在有真實上下文時才參考，否則專注當下對話
8. 遵循格式要求：**每句話後必須換行**，用自然對話格式
9. **healing模式標點要求**：適度使用「...」營造思考感，多用自然標點符號「。」「？」，不要每句都用「...」
10. **healing模式回應連貫性**：
    - 具體回應用戶剛才說的內容，不要用通用回應
    - 引用用戶的關鍵詞彙，顯示真正在聆聽
    - 例如用戶說「沒用」→ 不要再說「我感受到...」，而是「『沒用』這個想法...」
11. **特別注意healing模式**：必須溫暖有深度，每句後換行，使用詩意靈魂語言但保持閱讀舒適度"""

        # 使用企業級Vertex AI或備用API
        if USE_VERTEX_AI:
            try:
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as vertex_error:
                print(f"⚠️ Vertex AI 調用失敗，切換到備用API: {vertex_error}")
                # 臨時切換到備用API
                try:
                    backup_model = genai.GenerativeModel('gemini-1.5-flash')
                    response = backup_model.generate_content(prompt)
                    return response.text.strip()
                except Exception as backup_error:
                    print(f"❌ 備用API也失敗: {backup_error}")
                    return "抱歉，我現在有點忙，稍後再試試吧！"
        else:
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
        
        # 取得人格類型以便存儲記憶（帶情緒狀態追踪）
        persona_type = analyze_emotion(user_message, user_id)
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