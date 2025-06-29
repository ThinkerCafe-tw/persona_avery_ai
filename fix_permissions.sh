#!/bin/bash

# 修復shell配置文件權限的腳本
echo "正在修復權限問題..."

# 嘗試修復文件所有權
if [ "$(id -u)" = "0" ]; then
    # 如果是root用戶運行
    chown apple:staff ~/.zshrc ~/.bash_profile
    echo "已修復文件所有權"
else
    # 如果是普通用戶，提供sudo命令
    echo "請手動運行以下命令修復權限："
    echo "sudo chown apple:staff ~/.zshrc ~/.bash_profile"
fi

# 添加UV到PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.profile
echo "已將UV添加到PATH"

# 確認UV可用
if [ -f "$HOME/.local/bin/uvx" ]; then
    echo "✅ UV已安裝並可用"
    echo "重新啟動終端或運行 'source ~/.profile' 後即可使用"
else
    echo "❌ UV未找到，請重新安裝"
fi