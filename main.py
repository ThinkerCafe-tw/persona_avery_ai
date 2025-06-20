  import os
  from flask import Flask, request, abort
  import google.generativeai as genai
  from linebot.v3 import WebhookHandler
  from linebot.v3.exceptions import InvalidSignatureError
  from linebot.v3.messaging import Configuration, ApiClient,
  MessagingApi, ReplyMessageRequest, TextMessage
  from linebot.v3.webhooks import MessageEvent, TextMessageContent

  app = Flask(__name__)

  line_bot_api = MessagingApi(ApiClient(Configuration(access_token=os.ge
  tenv('LINE_CHANNEL_ACCESS_TOKEN'))))
  handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
  genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
  model = genai.GenerativeModel('gemini-pro')

  def get_lumi_response(user_message):
      try:
          prompt = f"你是Lumi露米，一位溫暖的心靈成長夥伴。你會深度同理
  、不批判、給予支持。當有人跟你分享心情時，你會先說辛苦了，然後溫柔地回
  應。使用者說：{user_message}"
          response = model.generate_content(prompt)
          return response.text
      except:
          return "親愛的，我在這裡陪伴你 💝"

  @app.route("/webhook", methods=['POST'])
  def webhook():
      signature = request.headers['X-Line-Signature']
      body = request.get_data(as_text=True)
      try:
          handler.handle(body, signature)
      except:
          abort(400)
      return 'OK'

  @handler.add(MessageEvent, message=TextMessageContent)
  def handle_message(event):
      user_message = event.message.text
      lumi_response = get_lumi_response(user_message)
      line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.r
  eply_token, messages=[TextMessage(text=lumi_response)]))

  from flask import Flask
  app = Flask(__name__)

  @app.route("/")
  def hello():
      return "Lumi露米在這裡！"

  @app.route("/webhook", methods=['POST'])
  def webhook():
      return "OK"

  if __name__ == "__main__":
      app.run(host='0.0.0.0', port=8080)
