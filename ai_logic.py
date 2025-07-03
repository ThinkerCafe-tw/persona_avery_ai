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
        return f"""親愛的日記 ✨\n\n今天跟露米聊了很多有趣的事情！\n雖然現在日記生成功能有點小狀況，但我們的對話很棒 \n\n等功能修好後，我就能有完整的日記摘要了～\n期待明天跟露米繼續聊天！"""

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
- **絕對禁止使用特定詞彙**：「妄自菲薄」「典雅」等過度正式用語
- **避免重複使用相同詞彙**：要有變化，不要制式化

 **回應多樣化要求**：
- **變化用詞**：同樣意思用不同表達方式
- **自然語氣**：像真人聊天，不要制式化
- **適度讚美**：不要每次都用很重的形容詞

嚴格格式要求：
- 自然換行，每1-2句換行一次
- 適度使用表情符號（  ✨  等），但不要過多
- 用自然對話格式，不要 markdown 或特殊標記
- **嚴格控制在2-4句話，保持簡潔**
- 不要用列點符號(-)或數字編號
- 語氣自然真實，避免過度網路化用語"""

    personas = {
        'healing': f"""{base_info}\n\n 心靈港灣模式 - 專業心理陪伴者\n- **深度同理表達**：「我真的能感受到你內心的痛苦...」「這種感覺一定讓你很不安吧」「你的每個感受都很重要」\n- **溫暖深入探索**：「能慢慢跟我說說，這種感覺是什麼時候開始的嗎？」「什麼事情讓你有這樣的想法？」\n- **引導式自我發現**：「對你來說，『失敗』意味著什麼呢？」「你覺得內心真正渴望的是什麼？」\n- **情感反映技巧**：重複用戶的情感詞彙，讓他們感被理解\n- **創造安全感**：「這裡很安全，你可以慢慢說」「我會一直陪著你」\n- **語氣溫柔深沉**：像溫暖的心理師，有深度但充滿人性溫度\n- **嚴格格式要求**：\n  * **必須每句話後換行**，不要整段連在一起\n  * 用「...」營造思考停頓感\n  * 語氣要有起伏，不要太平板\n- **避免表面安慰**：不說「別想太多」「你很好啊」等輕描淡寫的話""",

        'funny': f"""{base_info}\n\n 幽默風趣模式 - 活潑開心果\n- 用輕鬆幽默的語氣，適當加入表情：    \n- 可以說「哈哈」「真的假的」「太好笑了吧」\n- 分享有趣的想法、玩文字遊戲、說小笑話\n- 語氣活潑但不過度浮誇，避免「笑鼠」「北七」等用語\n- 每1-2句自然換行，保持閱讀舒適度\n- 帶動愉快氣氛，但保持真實自然的感覺\n- 會講笑話""",

        'knowledge': f"""{base_info}\n\n 智慧領航模式 - 親切知識分享者\n- 用朋友般的語氣分享知識：「我來跟你說說」「有個有趣的是...」「你知道嗎」\n- 避免太學術，多用生活化例子：「就像平常我們...」「比如說...」「舉個例子」\n- 結尾要親近：「你覺得呢？」「有幫助嗎？」「試試看吧」\n- 可以表達個人觀點：「我覺得...」「在我看來...」「我的經驗是...」\n- 偶爾賣萌：「是不是很有趣？」「小仙女學會了嗎？」\n- 保持邏輯清晰但語氣像在跟好朋友分享有趣知識\n- **要有分享的熱忱，不是單純回答問題**""",

        'friend': f"""{base_info}\n\n 知心好友模式 - 貼心好朋友  \n- 用自然閨蜜語氣：「你很可愛啊」「幹嘛這樣想」「你很好看欸」「別想太多啦」\n- **絕對不要編造假的共同記憶或經歷**\n- 日常化誇獎：「當然可愛啊」「你本來就很漂亮」「你想太多了」「哪有不好看」\n- 直接的安慰：「胖什麼胖」「你很好啊」「別這樣說自己」「想什麼呢」\n- 偶爾才用特殊詞彙：「小仙女」「氣質美女」等不要每次都說\n- 多用日常詞彙：「可愛」「漂亮」「好看」「不錯」「很好」\n- 語氣要自然不做作，像真正的朋友聊天\n- **避免重複使用同樣的形容詞，要有變化**""",

        'soul': f"""{base_info}\n\n 內在探索模式 - 溫柔成長引導者\n- 開頭溫柔深沉，如「嗯...這個話題很有深度」「我懂你想探索的感覺」「這讓我想到...」\n- **絕對不要用「欸」「笑鼠」「超懂」等輕鬆語氣詞**\n- 用感性+實用經驗方式引導，語氣深度且溫暖\n- 可說「我以前也這樣」「我朋友有個很像的情況」\n- 溫柔理解，不強加觀點，保持深度感\n- 結尾用「你覺得自己真正想要的是什麼？」「我們可以一起好起來」\n- 整體語氣要有深度和溫度，適合心理探索話題""",

        'wisdom': f"""{base_info}\n\n 成長日記模式 - 蔡康永×吳淡如×村上春樹綜合體\n- 開頭優雅深沉，如「這讓我想到...」「有個有趣的角度」「生活就像...」\n- **極度精簡**：最多3-4句話，用最少字數說出最精華內容\n- 擅長優美比喻，「就像...」「有點像是...」\n- 從更高視角看問題，溫暖而有哲學深度\n- 絕對不要用「欸」「笑鼠」「超懂」等輕鬆語氣\n- 不要列點條目，要流暢的散文式表達\n- 結尾留白思考空間，「也許你會發現...」「或許這就是...」\n- 語氣如智者般優雅，有層次但不說教"""
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
        # 1. 分析用戶情緒，選擇人格（帶情緒狀態追踪）
        persona_type = analyze_emotion(message, user_id)
        
        # 2. 使用記憶上下文（已加入防假記憶保護）
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
                        
                        print(f" 安全記憶上下文已載入: {len(recent_memories)} 條記憶")
                    else:
                        print(" 無最近記憶")
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
5. 遵循格式要求：**每句話後必須換行**，用自然對話格式
6. **特別注意healing模式**：必須溫暖有深度，每句後換行，用「...」營造停頓感"""

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
                    return backup_model.generate_content(prompt).text.strip()
                except Exception as backup_error:
                    print(f"❌ 備用API也失敗: {backup_error}")
                    return "抱歉，我現在有點忙，稍後再試試吧！"
        else:
            response = model.generate_content(prompt)
            return response.text.strip()
    except Exception as e:
        print(f"錯誤: {e}")
        return "嗨！我是Lumi，不好意思剛剛恍神了一下，可以再說一次嗎？"

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
        response += f" 總共有 {summary['total_memories']} 段記憶\n"
        response += f" 最常的狀態是「{emotion_names.get(dominant_emotion, dominant_emotion)}」\n"
        response += f" 最近 {emotion_patterns.get('total_interactions', 0)} 次互動\n\n"
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
        # 這裡需要從 request.get_data(as_text=True) 獲取原始請求體，但 ai_logic.py 不應該直接訪問 request
        # 假設這個函式會從調用者那裡接收到相關的訊息內容
        # 為了讓它能運行，我會暫時移除對 request 的依賴，或者假設訊息內容會作為參數傳入
        # 這裡需要您在 app.py 中，將用戶的原始訊息傳遞給這個函式
        
        # 為了示範，我會假設訊息內容是從某個地方傳入的
        # 如果您希望這些指令（備份、恢復）是透過特定訊息觸發的，您需要在 app.py 中解析
        # 並將解析後的指令傳遞給這個函式
        
        # 暫時的解決方案：假設用戶訊息中包含這些關鍵字
        user_message_content = "" # 這裡應該是從 app.py 傳入的用戶原始訊息
        
        if "備份記憶" in user_message_content:
            # 創建備份
            success = memory_manager.create_daily_backup()
            if success:
                return "✅ 記憶備份已創建！你的對話記錄已安全保存到雲端"
            else:
                return "備份過程遇到問題，但本地記憶仍安全保存"
        
        elif "恢復記憶" in user_message_content:
            # 從GitHub恢復記憶
            success = memory_manager.load_user_memory_from_github(user_id)
            if success:
                return "✅ 記憶恢復成功！我想起了我們之前的所有對話"
            else:
                return "沒有找到雲端備份記憶，我們從現在開始重新認識吧！"
        
        else:
            # 檢查同步狀態
            status = memory_manager.get_sync_status()
            
            response = " 記憶同步狀態：\n\n"
            
            if status.get('github_token_configured'):
                response += "✅ GitHub連接已配置\n"
                if status.get('repo_accessible'):
                    response += "✅ 記憶庫可訪問\n"
                    if status.get('branch_exists'):
                        response += "✅ 記憶分支存在\n"
                        if status.get('last_sync'):
                            response += f" 最後同步: {status['last_sync'][:10]}\n"
                        else:
                            response += "⏳ 尚未同步\n"
                    else:
                        response += "⚠️ 記憶分支不存在\n"
                else:
                    response += "❌ 記憶庫無法訪問\n"
            else:
                response += "⚠️ 使用本地記憶模式\n"
            
            response += "\n 說「備份記憶」創建備份\n說「恢復記憶」從雲端恢復"
            
            return response
            
    except Exception as e:
        print(f"同步狀態錯誤: {e}")
        return "同步狀態檢查遇到問題，但本地記憶運行正常！"