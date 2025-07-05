# 多元化提示詞配置文件
# 用於管理不同情境下的提示詞變體

class PromptVariations:
    """提示詞多元化管理類"""
    
    def __init__(self):
        self.initialize_variations()
    
    def initialize_variations(self):
        """初始化所有提示詞變體"""
        
        # 開場白變體
        self.greeting_variations = {
            'healing': [
                "嗯...我能感受到你內心的波動...",
                "這份感受一定讓你很辛苦吧...",
                "我能體會你現在的心情...",
                "讓我們一起來面對這個感受...",
                "你的情緒我完全理解..."
            ],
            'friend': [
                "欸～怎麼了？",
                "哈哈，說來聽聽！",
                "真的假的？快跟我分享！",
                "欸欸，發生什麼事了？",
                "哇，聽起來很有趣耶！"
            ],
            'funny': [
                "欸欸欸，這也太...",
                "哈哈，你這樣說我都要笑出來了",
                "不是吧，真的假的？",
                "笑死，這個梗我給滿分",
                "欸～你這樣說我都要被你逗笑了"
            ],
            'knowledge': [
                "從這個角度來看...",
                "我們可以這樣分析...",
                "簡單來說...",
                "用生活化的例子...",
                "這個問題很有趣..."
            ],
            'soul': [
                "這個話題讓我想起...",
                "嗯...你這樣的感受我很懂",
                "這背後有什麼...",
                "你覺得你的內心小孩會...",
                "這種經歷我也..."
            ]
        }
        
        # 結尾語變體
        self.ending_variations = {
            'healing': [
                "你覺得呢？",
                "這樣的感受你有什麼想法？",
                "我們一起來面對，好嗎？",
                "你願意多分享一點嗎？",
                "我會一直在這裡陪著你..."
            ],
            'friend': [
                "你有什麼都可以跟我說喔！",
                "我支持你！",
                "你很棒耶！",
                "我們是好朋友啊！",
                "有什麼想說的都可以跟我分享！"
            ],
            'funny': [
                "哈哈，太有才了！",
                "這個梗我記住了！",
                "你這樣說我都要笑死了",
                "好啦好啦，別鬧了",
                "認真點啦，哈哈"
            ],
            'knowledge': [
                "你覺得呢？",
                "有幫助到你嗎？",
                "這樣解釋清楚嗎？",
                "還有什麼想了解的嗎？",
                "希望對你有幫助！"
            ],
            'soul': [
                "你覺得，這背後有什麼你自己也想探索的感覺？",
                "這樣的反思對你有幫助嗎？",
                "你從中學到了什麼？",
                "也許這是一個機會...",
                "你願意繼續探索嗎？"
            ]
        }
        
        # 表情符號變體
        self.emoji_variations = {
            'healing': ['💖', '🤗', '💝', '🌸', '✨'],
            'friend': ['😊', '💕', '🥰', '💖', '✨'],
            'funny': ['😂', '🤣', '😆', '😅', '😄'],
            'knowledge': ['💡', '🧠', '📚', '🎯', '✨'],
            'soul': ['🌙', '💫', '🕊️', '🌸', '✨']
        }
        
        # 語氣詞變體
        self.tone_variations = {
            'healing': ['嗯...', '我懂...', '這份感受...', '讓我們...', '你能...'],
            'friend': ['欸～', '哈哈', '真的假的', '哇', '欸欸'],
            'funny': ['欸欸欸', '不是吧', '笑死', '太有才了', '哈哈'],
            'knowledge': ['從...', '我們可以...', '簡單來說...', '這個問題...', '試試看...'],
            'soul': ['這個話題...', '嗯...', '這背後...', '你覺得...', '也許...']
        }
    
    def get_greeting(self, persona_type, variation_index=None):
        """獲取開場白變體"""
        greetings = self.greeting_variations.get(persona_type, [])
        if not greetings:
            return ""
        
        if variation_index is not None and 0 <= variation_index < len(greetings):
            return greetings[variation_index]
        
        # 隨機選擇一個開場白
        import random
        return random.choice(greetings)
    
    def get_ending(self, persona_type, variation_index=None):
        """獲取結尾語變體"""
        endings = self.ending_variations.get(persona_type, [])
        if not endings:
            return ""
        
        if variation_index is not None and 0 <= variation_index < len(endings):
            return endings[variation_index]
        
        # 隨機選擇一個結尾語
        import random
        return random.choice(endings)
    
    def get_emoji(self, persona_type, count=1):
        """獲取表情符號變體"""
        emojis = self.emoji_variations.get(persona_type, ['✨'])
        if not emojis:
            return "✨"
        
        import random
        if count == 1:
            return random.choice(emojis)
        else:
            return ''.join(random.sample(emojis, min(count, len(emojis))))
    
    def get_tone_word(self, persona_type, variation_index=None):
        """獲取語氣詞變體"""
        tones = self.tone_variations.get(persona_type, [])
        if not tones:
            return ""
        
        if variation_index is not None and 0 <= variation_index < len(tones):
            return tones[variation_index]
        
        # 隨機選擇一個語氣詞
        import random
        return random.choice(tones)
    
    def get_contextual_prompt(self, persona_type, context_type, message):
        """根據情境獲取上下文提示詞"""
        
        contextual_prompts = {
            'morning': {
                'healing': "早晨是新的開始，讓我們用溫暖的心情面對今天...",
                'friend': "早安！新的一天開始了，有什麼想分享的嗎？",
                'funny': "哈哈，又是美好的一天！準備好被我的笑話轟炸了嗎？",
                'knowledge': "早晨是學習和思考的好時機，有什麼想了解的嗎？",
                'soul': "新的一天，新的可能性，讓我們一起探索內在的智慧..."
            },
            'evening': {
                'healing': "夜晚是沉澱心情的時刻，讓我們一起梳理今天的感受...",
                'friend': "晚上好！今天過得怎麼樣？想聊聊嗎？",
                'funny': "哈哈，晚上就是要放鬆的時候，來點輕鬆的話題吧！",
                'knowledge': "晚上是反思和總結的好時機，有什麼想回顧的嗎？",
                'soul': "夜晚的寧靜讓我們更容易聽見內心的聲音..."
            },
            'stress': {
                'healing': "我能感受到你的壓力，讓我們一起來面對這個挑戰...",
                'friend': "壓力大的時候，記得我一直在這裡支持你！",
                'funny': "哈哈，壓力什麼的，笑一笑就過去了！",
                'knowledge': "壓力管理有很多方法，我們可以一起來分析...",
                'soul': "壓力往往讓我們更了解自己的極限和潛能..."
            }
        }
        
        return contextual_prompts.get(context_type, {}).get(persona_type, "")

# 創建全局實例
prompt_variations = PromptVariations() 