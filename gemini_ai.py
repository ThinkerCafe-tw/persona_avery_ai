#!/usr/bin/env python3
"""
🧠 Lumi Gemini AI 對話系統
使用 Google Gemini API，簡單且經濟
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LumiGeminiAI:
    def __init__(self):
        """
        初始化 Gemini AI 系統
        """
        self.enabled = False
        self.model = None
        self.daily_usage = 0
        self.daily_limit = 50  # 免費額度
        
        try:
            # 設定 API Key
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                print("❌ 未找到 GEMINI_API_KEY")
                return
            
            genai.configure(api_key=api_key)
            
            # 初始化模型
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
            
            print("🧠 Gemini AI 系統已初始化")
            print(f"   模型: gemini-1.5-flash")
            print(f"   每日限制: {self.daily_limit} 次")
            print(f"   成本: 免費 (在限制內)")
            
        except Exception as e:
            print(f"❌ Gemini AI 初始化失敗: {e}")
            self.enabled = False
    
    def get_response(self, user_input, context=None):
        """
        獲取 AI 回應
        
        Args:
            user_input: 用戶輸入
            context: 可選的上下文資訊
        
        Returns:
            str: AI 回應，失敗返回 None
        """
        if not self.enabled:
            print("❌ Gemini AI 系統未啟用")
            return None
        
        if self.daily_usage >= self.daily_limit:
            print(f"⚠️ 已達每日使用限制 ({self.daily_limit} 次)")
            return "抱歉，今日的 AI 對話次數已用完。請明天再來聊天！"
        
        try:
            # 構建提示詞
            prompt = user_input
            
            if context:
                prompt = f"上下文: {context}\n\n用戶: {user_input}"
            
            # 生成回應
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                self.daily_usage += 1
                print(f"✅ AI 回應生成成功 (今日使用: {self.daily_usage}/{self.daily_limit})")
                return response.text.strip()
            else:
                print("⚠️ AI 回應為空")
                return None
                
        except Exception as e:
            print(f"❌ AI 回應生成失敗: {e}")
            return None
    
    def get_personalized_response(self, user_input, user_info=None):
        """
        獲取個人化的 AI 回應
        
        Args:
            user_input: 用戶輸入
            user_info: 用戶資訊 (姓名、偏好等)
        
        Returns:
            str: 個人化的 AI 回應
        """
        # 構建個人化上下文
        context = "你是 Lumi，一個友善的 AI 助手。"
        
        if user_info:
            if 'name' in user_info:
                context += f" 用戶的名字是 {user_info['name']}。"
            if 'preferences' in user_info:
                context += f" 用戶的偏好: {user_info['preferences']}。"
        
        context += " 請用溫暖、友善的語調回應，並盡量提供有用的資訊。"
        
        return self.get_response(user_input, context)
    
    def reset_daily_usage(self):
        """
        重置每日使用次數 (通常由定時任務調用)
        """
        self.daily_usage = 0
        print("🔄 每日使用次數已重置")
    
    def get_usage_info(self):
        """
        獲取使用情況資訊
        """
        return {
            "enabled": self.enabled,
            "daily_usage": self.daily_usage,
            "daily_limit": self.daily_limit,
            "remaining": self.daily_limit - self.daily_usage,
            "cost": "免費 (在限制內)",
            "model": "gemini-1.5-flash"
        }

# 創建全域實例
gemini_ai = LumiGeminiAI()

if __name__ == "__main__":
    # 測試程式
    print("🧪 Gemini AI 系統測試")
    print("=" * 40)
    
    if gemini_ai.enabled:
        print("✅ 系統正常，可以開始對話")
        
        # 顯示使用情況
        info = gemini_ai.get_usage_info()
        print(f"\n📊 使用情況:")
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        # 測試對話
        print(f"\n💬 測試對話:")
        test_input = "你好，請簡單介紹一下你自己"
        response = gemini_ai.get_response(test_input)
        
        if response:
            print(f"用戶: {test_input}")
            print(f"Lumi: {response}")
        
    else:
        print("❌ 系統初始化失敗")