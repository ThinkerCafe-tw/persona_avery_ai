import os
from dotenv import load_dotenv
import openai
from datetime import datetime
import json
from simple_memory import SimpleLumiMemory
from prompt_variations import prompt_variations

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

def generate_daily_summary(user_id):
    prompt = f"請根據今天與用戶 {user_id} 的所有對話，生成一段簡短的日記摘要。"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        reply_message = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"生成日記摘要錯誤: {e}")
        reply_message = f"""親愛的日記 ✨\n\n今天跟露米聊了很多有趣的事情！\n雖然現在日記生成功能有點小狀況，但我們的對話很棒 \n\n等功能修好後，我就能有完整的日記摘要了～\n期待明天跟露米繼續聊天！"""
    return reply_message

def get_persona_prompt(persona_type):
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
    return base_info

def get_lumi_response(message, user_id, persona_type=None):
    prompt = get_persona_prompt(persona_type) or ""
    memory_context = ""
    if memory_manager:
        try:
            recent_memories = memory_manager.get_recent_memories(user_id, limit=3)
            print(f"[LOG] recent_memories: {recent_memories}")
            similar_memories_list = memory_manager.get_similar_memories(user_id, message, limit=3)
            print(f"[LOG] similar_memories_list: {similar_memories_list}")
            profile_memories_list = memory_manager.get_user_profile_memories(user_id, limit=5)
            print(f"[LOG] profile_memories_list: {profile_memories_list}")
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
        except Exception as e:
            print(f"記憶檢索失敗: {e}")
    prompt += memory_context
    prompt += f"\n\n用戶訊息：{message}"
    print(f"[LOG] 最終送給 openai 的 prompt:\n{prompt}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        reply_message = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"錯誤: {e}")
        reply_message = "嗨！我是Lumi，不好意思剛剛恍神了一下，可以再說一次嗎？"
    if memory_manager and reply_message:
        try:
            memory_manager.store_conversation_memory(user_id, message, reply_message, persona_type)
            print(f" 對話記憶已存儲: {user_id}")
        except Exception as e:
            print(f" 記憶存儲失敗: {e}")
    return reply_message
