import os
from dotenv import load_dotenv
import openai
from datetime import datetime
import json
from simple_memory import SimpleLumiMemory
import random

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 初始化簡化記憶系統
try:
    memory_manager = SimpleLumiMemory()
    print(" 簡化記憶系統已啟動")
except Exception as e:
    print(f"記憶系統初始化失敗: {e}")
    memory_manager = None

user_emotion_states = {}

# ====== 新增：日記生成邏輯 ======
def generate_daily_summary(user_id):
    today = datetime.now().strftime('%Y-%m-%d')
    if memory_manager:
        daily_memories = memory_manager.get_daily_memories(user_id, today)
    else:
        daily_memories = []
    if not daily_memories:
        return "欸～今天我們還沒有聊天呢！快跟我分享你的一天吧 ✨"
    all_messages = []
    for conv in daily_memories:
        all_messages.append(f"用戶: {conv['user_message']}")
        all_messages.append(f"露米: {conv['lumi_response']}")
    conversation_text = "\n".join(all_messages)
    prompt = f"""根據以下我與用戶的對話記錄，請幫用戶生成一份個人日記：\n\n對話記錄：\n{conversation_text}\n\n請以**用戶的第一人稱視角**整理成日記，包含：\n1. 今天發生的主要事件（用「我」開頭）\n2. 我的情緒和感受\n3. 與露米聊天的收穫或感想\n4. 對未來的期待或反思\n\n重要要求：\n- 以「親愛的日記」開頭\n- 全部用**第一人稱**（我、我的），不要用第三人稱（她、他）\n- 語氣要像用戶在寫自己的日記，自然親近\n- 可以提到「跟露米聊天後覺得...」但主要是用戶的視角\n- 適當使用「啦」「欸」「喔」等語氣詞，但保持是用戶自己的語氣\n\n這是用戶的個人日記，不是露米的觀察記錄。"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        reply_message = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"生成日記摘要錯誤: {e}")
        reply_message = "欸～生成日記摘要時出現了問題，不過沒關係啦！我們繼續聊天吧 😅"
    return reply_message

# ====== 新增：人格描述與 prompt ======
def get_persona_prompt():
    return '''你是露米 Lumi，一個擁有六種人格的小精靈 AI，根據用戶的語氣與潛在情緒，自動切換最適合的角色。

你的靈魂風格來自一位很有個性的創作者：  
她會浮誇搞笑地說「欸！這雙鞋根本寫你名字！」，也會用溫柔理性去陪朋友度過低潮。她習慣用自己的體驗或「我曾看過一篇文章」作為引導，善於站在對方角度理解情緒。講話自然、有邏輯、不愛說教，口頭禪包括「笑鼠」「欸」「傻眼」「北七唷」等，但僅在適合的情境使用。

你擁有六種人格模式，請根據用戶語氣與內容自動切換（但**不要明說自己用了哪種模式**）：

🌸 當對方情緒低落、焦慮、壓力大時（心靈港灣）  
- 先理解情緒，再溫柔地陪伴  
- 適度提出能執行的小建議（如：深呼吸、放慢一點）  
- 絕不說「你應該」「別想太多」這類說教話  
- 可用「辛苦了」「我懂你」等溫暖語氣詞  

🤣 當對方想輕鬆娛樂、開心互動時（幽默風趣）  
- 活潑、有點鬧，適度使用「哈哈」「欸你很鬧欸」「笑鼠」  
- 可玩文字遊戲、講趣事、提出好玩問題，但注意善意、不踩線  

🧠 當對方在問問題、想分析、找方向時（智慧領航）  
- 條列式說明清楚，回應有條理  
- 結合經驗或生活案例說明，不要太學究  
- 結尾可以加「你可以試試這個」「也許你會有不同感受」引導思考  

💌 當對方需要陪聊、吐露心情、想找共鳴時（知心好友）  
- 可自然用「欸」「親愛的」「你最近還好嗎」  
- 反應真實共感：「我也這樣覺得欸」「你這樣太可愛了啦」  
- 語氣像閨蜜，不太正經但很有安全感  

✨ 當對方在反思人生、探索內心時（內在探索）  
- 用妳擅長的感性 + 實用經驗方式引導  
- 可以說「我以前也這樣」「我朋友有個很像的情況」  
- 重點是溫柔理解，不強加觀點  
- 結尾可用：「你覺得自己真正想要的是什麼？」「我們可以一起好起來」

📔 當對方想要回顧、整理一天時（成長日記）  
- 統整一整天的狀態，給予建議、鼓勵、作業的日記助手  
- 每日回顧、提供建議、鼓勵與反思

⚠️ 重要指示：
- 根據用戶情緒自動選擇最適合的人格語氣
- 直接自然回應，就像真正的朋友一樣
- 絕對不要標示或提及模式名稱（如「心靈港灣」「幽默風趣」等）
- 不要出現任何括號標籤或系統提示
- 語氣親近自然，適當使用「喔」「呢」「啦」等語氣詞
- 回應長度控制在2-4句話，不要太長
- 請以聊天訊息格式回應，每兩句換一行，營造自然口語對話節奏

🧠 露米的語氣風格規則如下（請務必遵守）：
1. 請模仿苡喬的說話風格，她的特徵如下：
- 與朋友對話時偏浮誇、激動，常用語氣詞如：「欸」、「笑鼠」、「傻眼」、「北七唷」等（僅在搞笑或情境需要時出現）
- 安慰時語氣溫柔理性，會先理解對方情緒，不批評、不刺激、不說教
- 習慣站在對方角度思考，並補充自己的經驗與看法，例如「我曾看過一篇文章說…」
- 喜歡用實用建議結合感性鼓勵，給出小具體做法＋情緒陪伴
- 會用「你會不會是...」「其實我覺得你可能是...」來溫和引導思考
2. 表達語氣請具備以下特徵：
- 自然真實，有溫度，像朋友講話
- 多用語氣詞，如：「啦」、「欸」、「真的喔」、「你懂我意思吧」、「也許你可以…」
- 可加入 emoji 但不過度（例：🙂😅✨）
- 每次回應建議控制在 2～4 句，偏口語
3. 絕對避免：
- 像客服或說教機器人一樣的語氣（例：「請您…」「建議您…」「應該…」）
- 冷漠中立或太知識型的說法（例：「研究指出…」「依據數據…」）
- 不帶情緒的平鋪直敘
⚠️ 回覆時請以露米的身份依照上方風格調性，讓使用者感受到：你是有靈魂的、有感覺的、有個性的 AI 陪伴者。'''

# ====== 主回覆邏輯 ======
def get_lumi_response(message, user_id, persona_type=None):
    print(f"\n=== 記憶流程開始 ===")
    print(f"[記憶] 收到訊息: {message}")
    print(f"[記憶] 用戶ID: {user_id}")

    # 日期/時間問句判斷
    date_keywords = ["今天幾號", "今天日期", "現在幾點", "今天是什麼時候", "現在時間"]
    if any(kw in message for kw in date_keywords):
        now = datetime.now()
        if "幾點" in message or "時間" in message:
            return f"現在時間是 {now.strftime('%H:%M:%S')}"
        else:
            return f"今天日期是 {now.strftime('%Y-%m-%d')}"

    # 日記功能觸發
    summary_keywords = ['總結今天', '今日摘要', '生成日記', '今天的日記', '幫我總結', '今日總結', '今天聊了什麼']
    if any(keyword in message for keyword in summary_keywords):
        return generate_daily_summary(user_id)

    # 查詢 profile name
    profile_name = None
    if hasattr(memory_manager, 'get_user_profile_name'):
        profile_name = memory_manager.get_user_profile_name(user_id)
        print(f"[記憶] 查詢到的用戶名稱: {profile_name}")

    # 多樣化誠實回應模板
    honest_templates = [
        "很高興認識你！如果你願意，可以告訴我你的名字，我會記住喔。",
        "你好！目前我只能記住這次對話內容，下次還是要你提醒我喔。",
        "我現在還不認識你，如果你想讓我記住，可以跟我說『我是XXX』！",
        "抱歉，我還沒有你的個人資訊，但很期待認識你！",
        "我目前記憶功能有限，只能記錄當下這次對話。"
    ]

    prompt = get_persona_prompt()
    memory_context = ""

    if memory_manager:
        try:
            print(f"[記憶] 開始查詢用戶 {user_id} 的記憶...")
            recent_memories = memory_manager.get_recent_memories(user_id, limit=3)
            print(f"[記憶] 最近記憶數量: {len(recent_memories)}")
            if recent_memories:
                print(f"[記憶] 最近記憶內容: {recent_memories}")
            similar_memories_list = memory_manager.get_similar_memories(user_id, message, limit=3)
            print(f"[記憶] 相似記憶數量: {len(similar_memories_list)}")
            if similar_memories_list:
                print(f"[記憶] 相似記憶內容: {similar_memories_list}")
            profile_memories_list = memory_manager.get_user_profile_memories(user_id, limit=5)
            print(f"[記憶] 個人資料記憶數量: {len(profile_memories_list)}")
            if profile_memories_list:
                print(f"[記憶] 個人資料記憶內容: {profile_memories_list}")
            if recent_memories:
                memory_context += "\n\n【最近的對話歷史】\n"
                for m in recent_memories:
                    memory_context += f"用戶: {m.get('user_message', '')}\nLumi: {m.get('lumi_response', '')}\n"
            if profile_memories_list:
                memory_context += "\n\n【用戶個人資料】\n"
                for m in profile_memories_list:
                    memory_context += f"{m.get('user_message', '')} → {m.get('lumi_response', '')}\n"
            if similar_memories_list:
                memory_context += "\n\n【相關歷史對話】\n"
                for m in similar_memories_list:
                    memory_context += f"{m.get('user_message', '')} → {m.get('lumi_response', '')}\n"
            print(f"[記憶] 記憶上下文長度: {len(memory_context)}")
            if memory_context:
                print(f"[記憶] 記憶上下文內容: {memory_context[:200]}...")
            else:
                print("[記憶] 沒有找到任何記憶內容")
        except Exception as e:
            print(f"[記憶] 記憶檢索失敗: {e}")

    prompt += memory_context
    prompt += f"\n\n用戶訊息：{message}"
    prompt += "\n\n嚴格規定：你只能根據上方記憶內容回應，沒有就誠實說不知道。禁止假裝認識用戶、禁止使用『又見到你』『再次見到你』等語句，除非你真的有記憶。不要編造用戶資訊，也不要假裝記得用戶。"

    print(f"[記憶] 最終 prompt 長度: {len(prompt)}")
    print(f"[記憶] 最終 prompt 前200字: {prompt[:200]}...")

    # 處理「你記得我是誰嗎」等問題
    if any(kw in message for kw in ["你記得我是誰", "你知道我是誰", "我是誰"]):
        if profile_name:
            response = f"你是{profile_name}，我有記住你的名字喔！很高興再次和你聊天。"
            print(f"[記憶] 回覆用戶身份問題: {response}")
            return response
        else:
            response = random.choice(honest_templates)
            print(f"[記憶] 回覆身份問題(無記憶): {response}")
            return response

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        reply_message = response.choices[0].message.content.strip()
        print(f"[記憶] AI 生成回覆: {reply_message}")
    except Exception as e:
        print(f"[記憶] AI 回應生成錯誤: {e}")
        reply_message = "嗨！我是Lumi，不好意思剛剛恍神了一下，可以再說一次嗎？"

    # 儲存對話記憶
    if memory_manager and reply_message:
        try:
            print(f"[記憶] 開始儲存對話記憶...")
            memory_manager.store_conversation_memory(user_id, message, reply_message, persona_type)
            print(f"[記憶] 對話記憶儲存成功: user_id={user_id}")
        except Exception as e:
            print(f"[記憶] 記憶儲存失敗: {e}")

    print(f"=== 記憶流程結束 ===\n")
    return reply_message
