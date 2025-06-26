#!/usr/bin/env python3
"""
Railway部署調試腳本 - 簡化版露米測試
"""
import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "🤖 Lumi Debug Mode - Railway部署測試成功！"

@app.route("/webhook", methods=['POST'])
def webhook():
    return "Webhook測試成功"

@app.route("/health")
def health():
    return {
        "status": "ok",
        "message": "Lumi服務運行正常",
        "version": "debug-1.0"
    }

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)