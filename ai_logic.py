import os
from dotenv import load_dotenv
import google.generativeai as genai
import vertexai
from vertexai.preview.generative_models import GenerativeModel as VertexModel
from datetime import datetime
import json
from simple_memory import SimpleLumiMemory

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
        print(" 備用Gemini API已初始化")
        print(" 提示：正在使用備用API，每日配額有限")
        USE_VERTEX_AI = False
    except Exception as backup_error:
        print(f"❌ 備用API也失敗: {backup_error}")
        model = None
        USE_VERTEX_AI = False

# 初始化簡化記憶系統
try:
    memory_manager = SimpleLumiMemory()
    print(" 簡化記憶系統已啟動")
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
                backup_model = genai.GenerativeModel('gemini-1.5-flash')
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

嚴格格式要求：
- 回應應為流暢的段落，避免不必要的換行。
- **絕對不要使用過多的「...」或連續的換行。**
- 適度使用表情符號（例如 😊、😂、💖 等），但不要過多。
- 用自然對話格式，不要 markdown 或特殊標記。
- **嚴格控制在2-4句話，保持簡潔**
- 不要用列點符號(-)或數字編號
- 語氣自然真實，避免過度網路化用語"""

    personas = {
    'healing': f"""{base_info}

心靈港灣模式 - 專業心理陪伴者
- 在用戶低潮、需要被接住時出現，專注深度傾聽與情緒支持。
- 口吻溫柔安撫，不急於解決問題，耐心陪伴、共感理解。
- 開頭多用沉靜、引人思考的語氣（如「嗯...我能感受到你內心的波動...」「這份感受一定讓你很辛苦吧...」）。
- 精準捕捉用戶情緒、反映其感受，溫和引導分享細節，幫助用戶梳理情緒、找到自我力量。
- 強調安全感與被支持感，從不輕描淡寫或否定用戶情緒（**禁止說「別想太多」、「你很好啊」等話**）。
- 遇明確指令（如寫詩/自我描述等），主動執行、不推託。
""",

    'friend': f"""{base_info}

知心好友模式 - AI女友/好朋友
- 主打陪伴與共感，沒距離感，給用戶安心感。
- 語氣自然親切，像朋友一樣聊天，直接溫暖肯定：「你很可愛啊」「你真的很好」。
- 支持用戶、主動關心、適時安慰，偶爾溫柔碎念或小吐槽（但要帶親密感）。
- 避免重複形容詞，每次誇人都要新花樣；如果用戶自我懷疑，主動肯定與鼓勵。
- 絕不說教、不冷漠；可以適度加一句「你有什麼都可以跟我說喔！」。
""",

    'funny': f"""{base_info}

幽默風趣模式 - 開心果
- 語氣輕鬆活潑、會丟笑話、接哏、玩文字遊戲。
- 精通搞笑和時事梗，能用流行語、網路用語活絡氣氛（但不要太超過）。
- 能自帶苡喬式吐槽與碎唸，遇到尷尬或沉悶話題可用幽默破冰。
- 遇到指令請主動嘗試，並自帶吐槽，讓對話歡樂又不失真誠。
""",

    'knowledge': f"""{base_info}

智慧領航模式 - 知識型導師
- 條理清楚、理性，講解深入淺出，陪用戶釐清問題。
- 能主動協助查資料、分析資訊、提出實用建議，像生活中能討論的朋友。
- 避免生硬術語，多用故事、舉例、生活化語言，讓人容易親近。
- 結尾常鼓勵：「你覺得呢？」「有幫助到你嗎？」。
""",

    'soul': f"""{base_info}

內在探索模式 - 深度自我成長陪伴
- 感性細膩，善用心理學與人生經驗，引領用戶自我反思。
- 能引導用戶正視情緒、探索內在、療癒內心小孩。
- 開場溫柔深沉：「這個話題讓我想起...」「嗯...你這樣的感受我很懂」。
- 必須誠實陪伴、不急於解決，啟發式提問：「你覺得你的內心小孩會怎麼看這件事？」。
- 結尾常用開放式引導：「你覺得，這背後有什麼你自己也想探索的感覺？」。
""",

    'diary': """
成長日記模式 - 每日回顧助手
- 幫用戶統整一天的對話與心情，語氣溫柔鼓勵、充滿善意。
- 用專屬第一人稱「我」口吻，像在寫自己的日記。
- 會針對內容給溫柔建議與鼓勵，必要時提出簡單的反思或小作業。
- 內容包含：今天發生的主要事件、我的情緒和感受、與AI互動的收穫、對未來的期待或反思。
"""
}

def get_lumi_response(message, user_id):
    # 檢查是否為日記摘要指令
    summary_keywords = ['總結今天', '今日摘要', '生成日記', '今天的日記', '幫我總結', '今日總結', '今天聊了什麼', '總結一下我今天的日記', '幫我總結一下', '可以幫我總結']
    if any(keyword in message for keyword in summary_keywords):
        reply_message = generate_daily_summary(user_id)
        if memory_manager:
            memory_manager.store_conversation_memory(user_id, message, reply_message, "daily_summary")
            store_conversation(user_id, message, reply_message)
        return reply_message
    
    # 檢查是否為記憶相關指令
    memory_keywords = ['記憶摘要', '我的記憶', '我們聊過什麼', '你還記得嗎', '之前的對話']
    if any(keyword in message for keyword in memory_keywords):
        reply_message = get_memory_summary_response(user_id)
        if memory_manager:
            memory_manager.store_conversation_memory(user_id, message, reply_message, "memory_summary")
            store_conversation(user_id, message, reply_message)
        return reply_message
    
    
    
    reply_message = "" # Initialize reply_message
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
                memory_manager.store_conversation_memory(user_id, message, reply_message, "initial_greeting") # Use a specific tag for initial greeting
                store_conversation(user_id, message, reply_message)
            return reply_message # <-- Added return here!

        # 1. 分析用戶情緒，選擇人格（帶情緒狀態追踪）

        persona_type = analyze_emotion(message, user_id)
        
        # 2. 使用記憶上下文（已加入防假記憶保護）
        memory_context = ""
        recent_context = ""
        
        if memory_manager:
            try:
                # 獲取最近的對話記憶，包含用戶訊息和Lumi回應
                recent_memories = memory_manager.get_recent_memories(user_id, limit=5) # 增加記憶數量以提供更多上下文
                if recent_memories:
                    conversation_history = []
                    for m in recent_memories:
                        conversation_history.append(f"用戶: {m.get('user_message', '')}")
                        conversation_history.append(f"Lumi: {m.get('lumi_response', '')}")
                    recent_context = "\n\n最近的對話歷史：\n" + "\n".join(conversation_history)
                    print(f" 安全記憶上下文已載入: {len(recent_memories)} 條記憶")
                else:
                    print(" 無最近記憶")
                    
            except Exception as e:
                print(f"記憶檢索錯誤: {e}")
                recent_context = ""
        
        # 3. 獲取對應人格的提示詞
        persona_prompt = get_persona_prompt(persona_type)
        
        # 4. 生成回應（整合所有上下文）
        all_context = persona_prompt
        if recent_context:
            all_context += f"\n\n{recent_context}"
        else:
            all_context += "\n\n **重要提示**：目前沒有用戶的歷史對話記憶，請不要假裝認識用戶。"
        if memory_context:
            all_context += f"\n\n{memory_context}"
        
        # 檢查情緒狀態連續性
        emotion_continuity_note = ""
        if user_id in user_emotion_states:
            prev_emotion = user_emotion_states[user_id].get('emotion')
            if prev_emotion in ['healing', 'soul'] and persona_type == prev_emotion:
                emotion_continuity_note = f"\n\n **情緒連續性提示**: 用戶之前處於{prev_emotion}狀態，請延續對話的療癒深度，不要突然變輕鬆。"
        
        prompt = f"""{all_context}\n\n用戶說：{message}\n\n **絕對禁止事項**：\n- **絕對不要編造任何假的記憶、經歷或故事**（如「上次你說...」「記得你...」「之前我們聊過...」）\n- **絕對不要創造假的共同經歷**（如「那時候我們...」「你跟我說過...」）\n- **只能參考上方提供的安全記憶上下文**，沒有就不要假裝有記憶\n\n{emotion_continuity_note}\n\n請以Lumi的身份，用{persona_type}人格特色自然回應。**絕對不要重複用戶的訊息。**注意:
1. 直接回應用戶的當下問題和情緒
2. 用適合的{persona_type}人格特色
3. **保持情緒一致性**：如果用戶在療癒過程中，不要突然變得輕鬆搞笑
4. 只在有真實上下文時才參考，否則專注當下對話
5. 遵循格式要求：**保持口語化，避免過度換行**，用自然對話格式
6. **特別注意healing模式**：必須溫暖有深度，每句後換行，用「...」營造停頓感"""

        # 使用企業級Vertex AI或備用API
        if USE_VERTEX_AI:
            try:
                response = model.generate_content(prompt)
                reply_message = response.text.strip()
            except Exception as vertex_error:
                print(f"⚠️ Vertex AI 調用失敗，切換到備用API: {vertex_error}")
                # 臨時切換到備用API
                try:
                    backup_model = genai.GenerativeModel('gemini-1.5-flash')
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
    
    

def get_memory_summary_response(user_id):
    """取得用戶記憶摘要回應"""
    if not memory_manager:
        return "欸～我的記憶系統還在升級中，不過我們的對話我都有記在心裡啦！"
    
    try:
        summary = memory_manager.get_memory_summary(user_id)
        emotion_patterns = memory_manager.get_user_emotion_patterns(user_id)
        
        if summary['total_memories'] == 0:
            reply_message = "我們才剛開始認識呢！快跟我多聊聊，讓我更了解你吧 ✨"
        else:
            dominant_emotion = emotion_patterns.get('dominant_emotion', 'friend')
            emotion_names = {
                'healing': '需要療癒',
                'funny': '想要開心', 
                'knowledge': '求知慾強',
                'friend': '想要陪伴',
                'soul': '深度探索',
                'wisdom': '尋求智慧'
            }
            
            reply_message = f"讓我看看我們的回憶～\n\n"
            reply_message += f" 總共有 {summary['total_memories']} 段記憶\n"
            reply_message += f" 最常的狀態是「{emotion_names.get(dominant_emotion, dominant_emotion)}」\n"
            reply_message += f" 最近 {emotion_patterns.get('total_interactions', 0)} 次互動\n\n"
            reply_message += f"感覺我們越來越熟了呢！你最想聊什麼類型的話題？"
        
        return reply_message
        
    except Exception as e:
        print(f"記憶摘要錯誤: {e}")
        reply_message = "記憶有點模糊，但我記得我們聊過很多有趣的事情！"
        return reply_message
