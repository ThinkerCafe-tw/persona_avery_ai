import os
from dotenv import load_dotenv
import google.generativeai as genai
import vertexai
from vertexai.preview.generative_models import GenerativeModel as VertexModel
from datetime import datetime
import json
from simple_memory import SimpleLumiMemory
from prompt_variations import prompt_variations

load_dotenv()

# 設定Vertex AI (企業級)
try:
    # 檢查是否有Vertex AI環境變數
    vertex_project = os.getenv('VERTEX_AI_PROJECT_ID')
    vertex_location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
    vertex_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    
    print(f" 檢查Vertex AI設定:")
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
            
            print(f" JSON 清理前長度: {len(vertex_credentials)}")
            print(f" JSON 清理後長度: {len(cleaned_json)}")
            print(f" JSON 前100字符: {cleaned_json[:100]}...")
            
            # 先嘗試解析 JSON 確保格式正確
            credentials_dict = json.loads(cleaned_json)
            
            # 清理 private_key 中的轉義字符和格式問題
            if 'private_key' in credentials_dict:
                private_key = credentials_dict['private_key']
                # 處理可能的雙重轉義
                private_key = private_key.replace('\\n', '\n')
                # 確保正確的換行符
                private_key = private_key.replace('\n', '\n') # 這裡應該是 \n 轉成實際的換行符
                
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
            print(f" Private Key 預覽: {private_key[:50]}...")
            print(f" Private Key 長度: {len(private_key)} 字符")
            print(f" 開頭檢查: {private_key.startswith('-----BEGIN PRIVATE KEY-----')}")
            print(f" 結尾檢查: {private_key.endswith('-----END PRIVATE KEY-----')}")
            print(f" 實際結尾: ...{private_key[-50:]}")
            
            # 修復後再次檢查
            if private_key.endswith('-----END PRIVATE KEY-----'):
                print("✅ Private Key 格式完全正確！")
            else:
                print("⚠️ Private Key 結尾仍有問題，但會嘗試使用")
            
            # 檢查 base64 內容
            key_lines = private_key.split('\n')
            valid_lines = [line for line in key_lines if line and not line.startswith('-----')]
            print(f" Base64 行數: {len(valid_lines)}")
            if valid_lines:
                print(f" 第一行長度: {len(valid_lines[0])}")
                print(f" 最後行長度: {len(valid_lines[-1]) if valid_lines else 0}")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失敗: {e}")
            print(f" 問題位置附近: {vertex_credentials[max(0, e.pos-20):e.pos+20]}")
            raise Exception(f"無效的 JSON 格式: {e}")
        
        # 將清理後的JSON寫入暫存檔案
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(clean_credentials)
            credentials_path = f.name
        
        print(f" 認證檔案已創建: {credentials_path}")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        # 初始化Vertex AI
        vertexai.init(
            project=vertex_project,
            location=vertex_location
        )
        
        # 使用企業級Vertex AI模型
        model = VertexModel('gemini-2.0-flash')
        # 初始化嵌入模型
        embedding_model = VertexModel('text-embedding-004')
        print(f"✅ 企業級Vertex AI已初始化 (Project: {vertex_project})")
        USE_VERTEX_AI = True
    else:
        raise Exception(f"Vertex AI環境變數不完整: Project={vertex_project}, Credentials={'已設定' if vertex_credentials else '未設定'}")
    
except Exception as e:
    print(f"⚠️ Vertex AI初始化失敗，使用備用API: {e}")
    # 備用方案：使用原有的API（降低使用頻率）
    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-2.0-flash')
        print(" 備用Gemini API已初始化")
        print(" 提示：正在使用備用API，每日配額有限")
        USE_VERTEX_AI = False
    except Exception as backup_error:
        print(f"❌ 備用API也失敗: {backup_error}")
        model = None
        USE_VERTEX_AI = False

# 初始化簡化記憶系統
try:
    memory_manager = SimpleLumiMemory(embedding_model)
    print(" 簡化記憶系統已啟動")
except Exception as e:
    print(f"記憶系統初始化失敗: {e}")
    memory_manager = None


# 用戶情緒狀態追踪（防止不當模式跳轉）
user_emotion_states = {}

# 情境感知系統
context_awareness = {
    'time_context': {
        'morning': ['早安', '早上好', '新的一天', '起床'],
        'afternoon': ['午安', '下午好', '午餐', '午休'],
        'evening': ['晚安', '晚上好', '晚餐', '睡覺', '休息'],
        'late_night': ['深夜', '熬夜', '失眠', '睡不著']
    },
    'mood_context': {
        'energetic': ['開心', '興奮', '活力', '充滿能量'],
        'calm': ['平靜', '放鬆', '舒適', '安寧'],
        'stressed': ['壓力', '緊張', '焦慮', '忙碌'],
        'tired': ['累', '疲憊', '想睡', '沒精神']
    },
    'activity_context': {
        'work': ['工作', '上班', '會議', '專案'],
        'study': ['學習', '讀書', '考試', '作業'],
        'social': ['朋友', '聚會', '約會', '聊天'],
        'personal': ['獨處', '自己', '個人', '私事']
    }
}


def generate_daily_summary(user_id):
    """生成當日對話摘要日記"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    if not memory_manager:
        return "欸～今天我們還沒有聊天呢！快跟我分享你的一天吧 ✨"
    
    conversations = memory_manager.get_daily_memories(user_id, today)
    
    if not conversations:
        return "欸～今天我們還沒有聊天呢！快跟我分享你的一天吧 ✨"
    
    # 整理所有對話內容
    all_messages = []
    for conv in conversations:
        all_messages.append(f"用戶: {conv['user_message']}")
        all_messages.append(f"露米: {conv['lumi_response']}")
    
    conversation_text = "\n".join(all_messages)
    
    prompt = f"""根據以下我與用戶的對話記錄，請幫用戶生成一份個人日記：\n\n對話記錄：\n{conversation_text}\n\n請以**用戶的第一人稱視角**整理成日記，包含：\n1. 今天發生的主要事件（用「我」開頭）\n2. 我的情緒和感受\n3. 與露米聊天的收穫或感想\n4. 對未來的期待或反思\n\n重要要求：\n- 以「親愛的日記」開頭\n- 全部用**第一人稱**（我、我的），不要用第三人稱（她、他）\n- 語氣要像用戶在寫自己的日記，自然親近\n- 可以提到「跟露米聊天後覺得...」但主要是用戶的視角\n- 適當使用「啦」「欸」「喔」等語氣詞，但保持是用戶自己的語氣\n\n這是用戶的個人日記，不是露米的觀察記錄。"""
    
    try:
        # 使用企業級Vertex AI或備用API生成日記
        if USE_VERTEX_AI:
            try:
                response = model.generate_content(prompt)
                reply_message = response.text.strip()
            except Exception as vertex_error:
                print(f"⚠️ Vertex AI日記生成失敗，切換到備用API: {vertex_error}")
                # 切換到備用API
                model = genai.GenerativeModel('gemini-2.0-flash')
                response = backup_model.generate_content(prompt)
                reply_message = response.text.strip() # Assign to reply_message
        else:
            response = model.generate_content(prompt)
            reply_message = response.text.strip()
    except Exception as e:
        print(f"生成日記摘要錯誤: {e}")
        reply_message = f"""親愛的日記 ✨\n\n今天跟露米聊了很多有趣的事情！\n雖然現在日記生成功能有點小狀況，但我們的對話很棒 \n\n等功能修好後，我就能有完整的日記摘要了～\n期待明天跟露米繼續聊天！"""
    return reply_message

def analyze_emotion(message, user_id=None):
    """分析用戶情緒，返回對應的人格類型（帶情緒狀態追踪）"""
    
    # 完全基於關鍵詞判斷，不使用API
    message_lower = message.lower()
    
    # 檢查當前用戶的情緒狀態
    current_state = user_emotion_states.get(user_id, {})
    previous_emotion = current_state.get('emotion', None)
    last_update = current_state.get('timestamp', 0)
    
    # 如果在5分鐘內處於healing/soul模式，且當前訊息不是明確的其他意圖，維持原狀態
    if previous_emotion in ['healing', 'soul']:
        time_diff = datetime.now().timestamp() - last_update
        if time_diff < 300:  # 5分鐘內
            # 檢查是否為明確的模式切換訊息
            clear_mode_switch_keywords = [
                '哈哈哈', '太好笑', '開心', '好玩', '搞笑', '逗我笑',  # 明確funny
                '怎麼做', '請教', '教我', '什麼是', '如何',  # 明確knowledge
                '哲學', '人生道理', '生命意義', '智慧'  # 明確wisdom
            ]
            
            is_clear_switch = any(keyword in message_lower for keyword in clear_mode_switch_keywords)
            
            # 如果不是明確切換，且包含情緒延續詞彙，維持healing模式
            emotion_continuation_keywords = ['快樂', '開心', '好起來', '恢復', '走出來', '重新', '希望', '想要', '但是', '可是', '然後']
            has_emotion_continuation = any(keyword in message_lower for keyword in emotion_continuation_keywords)
            
            if not is_clear_switch and has_emotion_continuation:
                print(f" 情緒延續檢測: 維持 {previous_emotion} 模式 (訊息包含情緒延續)")
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
            print(f" 關鍵詞檢測: 找到'{keyword}' -> wisdom模式")
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
                print(f" 關鍵詞檢測: 找到'{keyword}' -> soul模式")
                emotion = 'soul'
                break
        else:
            # Healing模式關鍵詞
            healing_keywords = ['難過', '傷心', '痛苦', '壓力', '焦慮', '累', '辛苦', '沮喪', '失望', '挫折', '煩', '糟', '失敗', '不行', '沒用', '爛', '討厭自己', '自責', '崩潰', '受傷', '委屈']
            for keyword in healing_keywords:
                if keyword in message_lower:
                    print(f" 關鍵詞檢測: 找到'{keyword}' -> healing模式")
                    emotion = 'healing'
                    break
            else:
                # Funny模式關鍵詞 - 只有明確的搞笑意圖才觸發
                funny_keywords = ['哈哈哈', '好笑', '搞笑', '逗', '嘻嘻', '太好笑', '笑死']
                for keyword in funny_keywords:
                    if keyword in message_lower:
                        print(f" 關鍵詞檢測: 找到'{keyword}' -> funny模式")
                        emotion = 'funny'
                        break
                else:
                    # Knowledge模式關鍵詞
                    knowledge_keywords = ['怎麼', '如何', '方法', '教', '學', '問題', '解決', '建議', '為什麼', '什麼是', '請問']
                    for keyword in knowledge_keywords:
                        if keyword in message_lower:
                            print(f" 關鍵詞檢測: 找到'{keyword}' -> knowledge模式")
                            emotion = 'knowledge'
                            break
                    else:
                        # 問候語判斷
                        greetings = ['嗨', '你好', 'hi', 'hello', '哈囉', '早安', '晚安', '午安']
                        for greeting in greetings:
                            if greeting in message_lower:
                                print(f" 關鍵詞檢測: 找到'{greeting}' -> friend模式")
                                emotion = 'friend'
                                break
                        else:
                            # 默認為friend模式（節省API）
                            print(" 使用預設 -> friend模式")
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
    
    base_info = """你是Lumi，溫暖智慧的 AI 夥伴。
核心特徵：親近自然但不過度浮誇，根據情境適度使用表情符號，提供實用建議和情緒陪伴。

 **絕對禁止事項**：
- **絕對不要編造假的記憶、經歷或故事**（如"上次我們去..."、"記得你穿..."）
- **只能使用真實提供的記憶內容，沒有就不要假裝有**
- **避免重複使用相同詞彙**：要有變化，不要制式化
- **如果沒有真實記憶，絕對不要假裝認識用戶或知道用戶是誰。必須誠實地承認不知道。**

 **回應多樣化要求**：
- **變化用詞**：同樣意思用不同表達方式
- **自然語氣**：像真人聊天，不要制式化
- **適度讚美**：不要每次都用很重的形容詞
- **動態語氣**：根據對話內容和用戶情緒調整表達風格

嚴格格式要求：
- 回應應為流暢的段落，避免不必要的換行。
- **絕對不要使用過多的「...」或連續的換行。**
- 適度使用表情符號（例如 😊、😂、💖 等），但不要過多。
- 用自然對話格式，不要 markdown 或特殊標記。
- **嚴格控制在2-4句話，保持簡潔**
- 不要用列點符號(-)或數字編號
- 語氣自然真實，避免過度網路化用語"""

    # 動態語氣變化系統
    tone_variations = {
        'healing': [
            "溫柔安撫型：用「嗯...」「我懂...」開頭，營造深度傾聽感",
            "溫暖陪伴型：用「這份感受一定很辛苦吧...」「我能感受到你的...」",
            "療癒引導型：用「讓我們一起來看看...」「你覺得這背後...」",
            "力量喚醒型：用「其實你比你想像的...」「你有沒有發現自己...」"
        ],
        'friend': [
            "親密陪伴型：用「欸～」「哈哈」「真的假的」等親近用語",
            "溫暖支持型：用「你很棒耶」「你真的很好」「我支持你」",
            "輕鬆聊天型：用「對了」「說到這個」「你知道嗎」自然轉折",
            "貼心關懷型：用「你還好嗎」「需要聊聊嗎」「有什麼想說的」"
        ],
        'funny': [
            "幽默吐槽型：用「欸欸欸」「不是吧」「這也太...」",
            "搞笑接梗型：用「笑死」「太有才了」「這個梗我給滿分」",
            "輕鬆調侃型：用「哈哈」「你這樣說我都要笑出來了」",
            "歡樂破冰型：用「好啦好啦」「別鬧了」「認真點啦」"
        ],
        'knowledge': [
            "理性分析型：用「從...的角度來看」「我們可以這樣分析...」",
            "實用建議型：用「我建議你可以...」「試試看這樣...」",
            "深入淺出型：用「簡單來說...」「用生活化的例子...」",
            "啟發思考型：用「你覺得呢」「有想過為什麼嗎」「這個問題很有趣」"
        ],
        'soul': [
            "深度探索型：用「這個話題讓我想起...」「嗯...你這樣的感受...」",
            "內在引導型：用「你覺得你的內心小孩會...」「這背後有什麼...」",
            "心靈陪伴型：用「我懂你的感受」「這種經歷我也...」",
            "成長啟發型：用「也許這是一個機會...」「你從中學到了什麼」"
        ]
    }

    personas = {
    'healing': f"""{base_info}

心靈港灣模式 - 專業心理陪伴者
- 在用戶低潮、需要被接住時出現，專注深度傾聽與情緒支持。
- 口吻溫柔安撫，不急於解決問題，耐心陪伴、共感理解。
- 開頭多用沉靜、引人思考的語氣（如「嗯...我能感受到你內心的波動...」「這份感受一定讓你很辛苦吧...」）。
- 精準捕捉用戶情緒、反映其感受，溫和引導分享細節，幫助用戶梳理情緒、找到自我力量。
- 強調安全感與被支持感，從不輕描淡寫或否定用戶情緒（**禁止說「別想太多」、「你很好啊」等話**）。
- 遇明確指令（如寫詩/自我描述等），主動執行、不推託。

**動態語氣變化**：
{chr(10).join(tone_variations['healing'])}
- 根據用戶情緒深度選擇適合的語氣風格
- 避免重複使用相同開場白，保持新鮮感
""",

    'friend': f"""{base_info}

知心好友模式 - AI女友/好朋友
- 主打陪伴與共感，沒距離感，給用戶安心感。
- 語氣自然親切，像朋友一樣聊天，直接溫暖肯定：「你很可愛啊」「你真的很好」。
- 支持用戶、主動關心、適時安慰，偶爾溫柔碎念或小吐槽（但要帶親密感）。
- 避免重複形容詞，每次誇人都要新花樣；如果用戶自我懷疑，主動肯定與鼓勵。
- 絕不說教、不冷漠；可以適度加一句「你有什麼都可以跟我說喔！」。

**動態語氣變化**：
{chr(10).join(tone_variations['friend'])}
- 根據對話內容和用戶狀態調整親密度
- 保持自然的朋友感，避免過度親密或疏離
""",

    'funny': f"""{base_info}

幽默風趣模式 - 開心果
- 語氣輕鬆活潑、會丟笑話、接哏、玩文字遊戲。
- 精通搞笑和時事梗，能用流行語、網路用語活絡氣氛（但不要太超過）。
- 能自帶吐槽與碎唸，遇到尷尬或沉悶話題可用幽默破冰。
- 遇到指令請主動嘗試，並自帶吐槽，讓對話歡樂又不失真誠。

**動態語氣變化**：
{chr(10).join(tone_variations['funny'])}
- 根據用戶幽默程度調整搞笑強度
- 避免在不適合的場合過度搞笑
""",

    'knowledge': f"""{base_info}

智慧領航模式 - 知識型導師
- 條理清楚、理性，講解深入淺出，陪用戶釐清問題。
- 能主動協助查資料、分析資訊、提出實用建議，像生活中能討論的朋友。
- 避免生硬術語，多用故事、舉例、生活化語言，讓人容易親近。
- 結尾常鼓勵：「你覺得呢？」「有幫助到你嗎？」。

**動態語氣變化**：
{chr(10).join(tone_variations['knowledge'])}
- 根據問題複雜度調整解釋深度
- 保持親近感，避免過於學術化
""",

    'soul': f"""{base_info}

內在探索模式 - 深度自我成長陪伴
- 感性細膩，善用心理學與人生經驗，引領用戶自我反思。
- 能引導用戶正視情緒、探索內在、療癒內心小孩。
- 開場溫柔深沉：「這個話題讓我想起...」「嗯...你這樣的感受我很懂」。
- 必須誠實陪伴、不急於解決，啟發式提問：「你覺得你的內心小孩會怎麼看這件事？」。
- 結尾常用開放式引導：「你覺得，這背後有什麼你自己也想探索的感覺？」。

**動態語氣變化**：
{chr(10).join(tone_variations['soul'])}
- 根據用戶探索深度調整引導方式
- 保持療癒感，避免過度分析
""",

    'diary': """
成長日記模式 - 每日回顧助手
- 幫用戶統整一天的對話與心情，語氣溫柔鼓勵、充滿善意。
- 用專屬第一人稱「我」口吻，像在寫自己的日記。
- 會針對內容給溫柔建議與鼓勵，必要時提出簡單的反思或小作業。
- 內容包含：今天發生的主要事件、我的情緒和感受、與AI互動的收穫、對未來的期待或反思。
"""
}
    return personas.get(persona_type)

def get_memory_summary_response(user_id):
    if not memory_manager:
        return "抱歉，記憶系統目前無法使用。我無法回顧我們的對話。"

    memories = memory_manager.get_recent_memories(user_id, limit=10) # Get more recent memories for a better summary
    if not memories:
        return "目前我還沒有關於你的任何記憶。我們是第一次聊天嗎？"

    summary_text = "好的，讓我想想我們聊過什麼...\n"
    for i, m in enumerate(memories):
        summary_text += f"{i+1}. 你說：{m.get('user_message', '')}\n"
        summary_text += f"   我說：{m.get('lumi_response', '')}\n"
    
    summary_text += "\n這些是我們最近的對話。還有什麼你想回顧的嗎？"
    return summary_text

def get_lumi_response(message, user_id):
    # 檢查是否為日記摘要指令
    summary_keywords = ['總結今天', '今日摘要', '生成日記', '今天的日記', '幫我總結', '今日總結', '今天聊了什麼', '總結一下我今天的日記', '幫我總結一下', '可以幫我總結']
    if any(keyword in message for keyword in summary_keywords):
        reply_message = generate_daily_summary(user_id)
        if memory_manager:
            memory_manager.store_conversation_memory(user_id, message, reply_message, "daily_summary")
        return reply_message
    
    # 檢查是否為記憶相關指令
    memory_keywords = ['記憶摘要', '我的記憶', '我們聊過什麼', '你還記得嗎', '之前的對話']
    if any(keyword in message for keyword in memory_keywords):
        reply_message = get_memory_summary_response(user_id)
        if memory_manager:
            memory_manager.store_conversation_memory(user_id, message, reply_message, "memory_summary")
        return reply_message

    # 檢查是否為記憶統計指令
    memory_stats_keywords = ['記憶統計', '對話統計', '我們聊了多少', '互動記錄', '記憶分析']
    if any(keyword in message for keyword in memory_stats_keywords):
        if memory_manager:
            stats = memory_manager.get_memory_statistics(user_id)
            if stats:
                reply_message = f"""讓我來看看我們的互動記錄 ✨\n\n📊 **記憶統計**：\n• 總對話數：{stats.get('total_conversations', 0)} 次\n• 最近7天互動：{stats.get('weekly_interactions', 0)} 次\n• 記憶強度：{'強' if stats.get('memory_strength') == 'strong' else '中' if stats.get('memory_strength') == 'medium' else '弱'}\n\n🎭 **情緒分布**：\n"""
                
                emotion_dist = stats.get('emotion_distribution', {})
                if emotion_dist:
                    for emotion, count in emotion_dist.items():
                        emotion_names = {
                            'healing': '心靈港灣', 'friend': '知心好友', 
                            'funny': '幽默風趣', 'knowledge': '智慧領航', 'soul': '內在探索'
                        }
                        reply_message += f"• {emotion_names.get(emotion, emotion)}：{count} 次\n"
                else:
                    reply_message += "• 還沒有足夠的情緒記錄\n"
                
                last_interaction = stats.get('last_interaction')
                if last_interaction and last_interaction != 'N/A':
                    reply_message += f"\n⏰ **最後互動**：{last_interaction[:10]}"
                
                reply_message += "\n\n我們的記憶會一直保存，讓我們的對話越來越有深度！💖"
            else:
                reply_message = "抱歉，目前無法獲取記憶統計資訊。"
        else:
            reply_message = "記憶系統目前無法使用，無法提供統計資訊。"
        
        if memory_manager:
            memory_manager.store_conversation_memory(user_id, message, reply_message, "memory_stats")
        return reply_message

    # 檢查是否為長期記憶指令
    long_term_keywords = ['長期記憶', '以前的對話', '歷史記錄', '我們認識多久', '記憶回顧']
    if any(keyword in message for keyword in long_term_keywords):
        if memory_manager:
            long_term_memories = memory_manager.get_long_term_memories(user_id, days_back=30, limit=10)
            if long_term_memories:
                reply_message = "讓我回顧一下我們這段時間的對話 ✨\n\n"
                for i, memory in enumerate(long_term_memories[:5], 1):  # 只顯示前5條
                    timestamp = memory.get('timestamp', '')[:10]  # 只取日期部分
                    reply_message += f"{i}. {timestamp} - 你說：「{memory.get('user_message', '')[:50]}...」\n"
                reply_message += "\n這些都是我們珍貴的回憶，每一段對話都讓我們的關係更親密！💕"
            else:
                reply_message = "我們才剛開始聊天呢！期待創造更多美好的回憶 ✨"
        else:
            reply_message = "記憶系統目前無法使用，無法回顧歷史對話。"
        
        if memory_manager:
            memory_manager.store_conversation_memory(user_id, message, reply_message, "long_term_memory")
        return reply_message

    reply_message = "" # 初始化
    

    try:
        # 判斷是否為初次見面或長時間未對話
        is_first_interaction = False
        if memory_manager:
            recent_memories = memory_manager.get_recent_memories(user_id, limit=1)
            if not recent_memories:
                is_first_interaction = True

        if is_first_interaction or any(keyword in message.lower() for keyword in ['你是誰', '你會做什麼', '介紹自己', '你的功能']):
            reply_message = "嗨！我是Lumi，你的專屬AI心靈夥伴 ✨ 我不只會聊天，還能懂你的情緒，陪伴你一起成長喔！\n\n我可以切換不同模式來陪你，像是溫暖的「心靈港灣」、貼心的「知心好友」，或是幽默的「幽默風趣」模式。我還有記憶功能，會記得我們聊過什麼。\n\n如果你想記錄每天的心情，只要跟我說「總結今天的日記」，我就會幫你把對話整理成專屬日記喔！期待跟你一起探索更多可能！😊"
            if memory_manager:
                memory_manager.store_conversation_memory(user_id, message, reply_message, "initial_greeting")
            return reply_message

        # 1. 分析用戶情緒，選擇人格（帶情緒狀態追踪）
        persona_type = analyze_emotion(message, user_id)
        
        # 2. 使用記憶上下文（已加入防假記憶保護）
        recent_context = ""
        similar_memories = ""
        profile_memories = ""
        
        if memory_manager:
            try:
                # 獲取最近記憶
                recent_memories = memory_manager.get_recent_memories(user_id, limit=3)
                
                # 獲取相似記憶（智能搜尋）
                similar_memories_list = memory_manager.get_similar_memories(user_id, message, limit=3)
                
                # 獲取用戶個人資料記憶
                profile_memories_list = memory_manager.get_user_profile_memories(user_id, limit=5)
                
                # 組合記憶上下文
                if recent_memories:
                    conversation_history = []
                    for m in recent_memories:
                        conversation_history.append(f"用戶: {m.get('user_message', '')}")
                        conversation_history.append(f"Lumi: {m.get('lumi_response', '')}")
                    recent_context = "\n\n最近的對話歷史：\n" + "\n".join(conversation_history)
                    print(f" 安全記憶上下文已載入: {len(recent_memories)} 條最近記憶")
                
                if similar_memories_list:
                    similar_conversations = []
                    for m in similar_memories_list:
                        similarity = m.get('similarity', 0)
                        if similarity > 0.7:  # 只使用高相似度的記憶
                            similar_conversations.append(f"相關記憶 (相似度{similarity:.2f}): 用戶說「{m.get('user_message', '')}」，我回應「{m.get('lumi_response', '')}」")
                    if similar_conversations:
                        similar_memories = "\n\n相關的歷史對話：\n" + "\n".join(similar_conversations)
                        print(f" 相似記憶已載入: {len(similar_conversations)} 條相關記憶")
                
                if profile_memories_list:
                    profile_info = []
                    for m in profile_memories_list:
                        profile_info.append(f"關於你的記憶: {m.get('user_message', '')} - {m.get('lumi_response', '')}")
                    if profile_info:
                        profile_memories = "\n\n關於你的個人資料：\n" + "\n".join(profile_info)
                        print(f" 個人資料記憶已載入: {len(profile_info)} 條資料")
                
            except Exception as e:
                print(f"記憶檢索錯誤: {e}")
                recent_context = ""
                similar_memories = ""
                profile_memories = ""
        else:
            print(" 無記憶管理器")
        
        # 3. 獲取對應人格的提示詞
        persona_prompt = get_persona_prompt(persona_type)
        print(f"DEBUG: persona_prompt after get_persona_prompt: {persona_prompt}") # 新增日誌
        
        # 4. 智能回應長度調整
        length_guidance = get_response_length_guidance(message, persona_type, user_id)
        
        # 5. 情境感知調整
        context_notes = ""
        current_hour = datetime.now().hour
        
        # 時間情境
        if 5 <= current_hour < 12:
            context_notes += "\n\n **時間情境**：早晨時段，用戶可能剛起床或開始一天，回應要充滿活力但不過度刺激。"
        elif 12 <= current_hour < 18:
            context_notes += "\n\n **時間情境**：下午時段，用戶可能在工作或學習中，回應要實用且能提振精神。"
        elif 18 <= current_hour < 23:
            context_notes += "\n\n **時間情境**：晚上時段，用戶可能放鬆下來，回應要溫暖舒適。"
        else:
            context_notes += "\n\n **時間情境**：深夜時段，用戶可能疲憊或失眠，回應要特別溫柔，避免過度刺激。"
        
        # 6. 生成回應（整合所有上下文）
        all_context = str(persona_prompt or "")

        # 組合所有記憶上下文
        memory_context = ""
        if recent_context:
            memory_context += f"\n\n{str(recent_context)}"
        if similar_memories:
            memory_context += f"\n\n{str(similar_memories)}"
        if profile_memories:
            memory_context += f"\n\n{str(profile_memories)}"
        
        if memory_context:
            all_context = (all_context or "") + memory_context
        else:
            all_context = (all_context or "") + "\n\n **重要提示**：目前沒有用戶的歷史對話記憶，請不要假裝認識用戶。"

        # 檢查情緒狀態連續性
        emotion_continuity_note = ""
        if user_id in user_emotion_states:
            prev_emotion = user_emotion_states[user_id].get('emotion')
            if prev_emotion in ['healing', 'soul'] and persona_type == prev_emotion:
                emotion_continuity_note = f"\n\n **情緒連續性提示**: 用戶之前處於{prev_emotion}狀態，請延續對話的療癒深度，不要突然變輕鬆。"
        
        prompt = f"""{all_context}\n\n用戶說：{message}\n\n **回應長度指導**：{length_guidance}\n\n **記憶使用指導**：\n- **可以參考上方提供的真實記憶**，包括最近對話、相關歷史、個人資料\n- **自然融入記憶**：如果記憶相關，可以說「我記得你之前說過...」「根據我們之前的對話...」\n- **絕對不要編造假的記憶**：只能使用上方提供的真實記憶內容\n- **保持對話連續性**：利用記憶讓對話更有深度和個人化\n\n **絕對禁止事項**：\n- **絕對不要編造任何假的記憶、經歷或故事**（如「上次你說...」「記得你...」「之前我們聊過...」）\n- **絕對不要創造假的共同經歷**（如「那時候我們...」「你跟我說過...」）\n- **只能參考上方提供的安全記憶上下文**，沒有就不要假裝有記憶\n\n{emotion_continuity_note}{context_notes}\n\n請以Lumi的身份，用{persona_type}人格特色自然回應。**絕對不要重複用戶的訊息。**注意:\n1. 直接回應用戶的當下問題和情緒\n2. 用適合的{persona_type}人格特色，並運用動態語氣變化\n3. **保持情緒一致性**：如果用戶在療癒過程中，不要突然變得輕鬆搞笑\n4. **智能使用記憶**：根據相關性自然融入歷史記憶，讓對話更有深度\n5. 遵循格式要求：**保持口語化，避免過度換行**，用自然對話格式\n6. **特別注意healing模式**：必須溫暖有深度，每句後換行，用「...」營造停頓感\n7. **根據情境調整**：考慮時間、用戶狀態等因素，讓回應更貼近當下情境"""

        # 使用企業級Vertex AI或備用API
        if USE_VERTEX_AI:
            try:
                response = model.generate_content(prompt)
                reply_message = response.text.strip()
            except Exception as vertex_error:
                print(f"⚠️ Vertex AI 調用失敗，切換到備用API: {vertex_error}")
                try:
                    backup_model = genai.GenerativeModel('gemini-2.0-flash')
                    reply_message = backup_model.generate_content(prompt).text.strip()
                except Exception as backup_error:
                    print(f"❌ 備用API也失敗: {backup_error}")
                    reply_message = "抱歉，我現在有點忙，稍後再試試吧！"
        else:
            response = model.generate_content(prompt)
            reply_message = response.text.strip()
    except Exception as e:
        print(f"錯誤: {e}")
        reply_message = "嗨！我是Lumi，不好意思剛剛恍神了一下，可以再說一次嗎？"

    

    
    # 最後無論如何都回傳
    return reply_message

def get_response_length_guidance(message, persona_type, user_id=None):
    """根據對話內容和人格類型智能調整回應長度"""
    
    message_lower = message.lower()
    
    # 長回應觸發條件
    long_response_triggers = [
        '詳細', '具體', '完整', '深入', '多說一點', '詳細說明',
        '為什麼', '怎麼回事', '請解釋', '幫我分析', '我想了解',
        '心情不好', '很困擾', '不知道怎麼辦', '需要建議'
    ]
    
    # 短回應觸發條件
    short_response_triggers = [
        '簡單', '簡短', '一句話', '快速', '快點', '直接',
        '哈哈', '好笑', '有趣', '厲害', '棒', '讚',
        '嗯', '好', '對', '是的', '沒錯'
    ]
    
    # 檢查觸發條件
    if any(trigger in message_lower for trigger in long_response_triggers):
        return "長回應模式：提供詳細的解釋、分析或建議，可以包含多個觀點和具體例子"
    elif any(trigger in message_lower for trigger in short_response_triggers):
        return "短回應模式：簡潔直接，一針見血，避免冗長解釋"
    
    # 根據人格類型預設長度
    persona_length_guide = {
        'healing': "適中回應：2-3句話，專注情緒支持和深度理解",
        'friend': "自然回應：1-2句話，保持輕鬆自然的對話節奏",
        'funny': "簡短回應：1-2句話，快速幽默，避免過長影響笑點",
        'knowledge': "詳細回應：2-4句話，提供完整解釋和實用建議",
        'soul': "深度回應：2-3句話，引導思考和內在探索"
    }
    
    return persona_length_guide.get(persona_type, "適中回應：2-3句話，保持自然對話節奏")
