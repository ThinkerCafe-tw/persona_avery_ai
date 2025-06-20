  import os
  from flask import Flask, request, abort
  import google.generativeai as genai
  from linebot.v3 import WebhookHandler
  from linebot.v3.exceptions import InvalidSignatureError
  from linebot.v3.messaging import (
      Configuration, ApiClient, MessagingApi,
      ReplyMessageRequest, TextMessage
  )
  from linebot.v3.webhooks import MessageEvent, TextMessageContent

  app = Flask(__name__)

  # 設定
  LINE_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
  LINE_SECRET = os.getenv('LINE_CHANNEL_SECRET')
  GEMINI_KEY = os.getenv('GEMINI_API_KEY')

  line_bot_api =
  MessagingApi(ApiClient(Configuration(access_token=LINE_ACCESS_TOKEN)))
  handler = WebhookHandler(LINE_SECRET)

  # Gemini 設定
  genai.configure(api_key=GEMINI_KEY)
  model = genai.GenerativeModel('gemini-pro')

  def get_lumi_response(message):
      try:
          prompt = f"""你是Lumi露米，溫暖的心靈成長夥伴。
          使用者說：{message}
          請溫暖回應，給予支持和陪伴。"""

          response = model.generate_content(prompt)
          return response.text
      except:
          return "親愛的，我在這裡陪伴你 💝"

  @app.route("/")
  def home():
      return "✨ Lumi露米在這裡陪伴你 ✨"

  @app.route("/webhook", methods=['POST'])
  def webhook():
      signature = request.headers.get('X-Line-Signature', '')
      body = request.get_data(as_text=True)

      try:
          handler.handle(body, signature)
      except InvalidSignatureError:
          abort(400)
      return 'OK'

  @handler.add(MessageEvent, message=TextMessageContent)
  def handle_message(event):
      user_message = event.message.text
      reply = get_lumi_response(user_message)

      line_bot_api.reply_message(
          ReplyMessageRequest(
              reply_token=event.reply_token,
              messages=[TextMessage(text=reply)]
          )
      )

  if __name__ == "__main__":
      port = int(os.getenv('PORT', 8080))
      app.run(host='0.0.0.0', port=port, debug=False)
