#!/bin/bash

echo "🧹 開始清理不需要的檔案..."

# 刪除修復指南檔案
echo "📝 刪除修復指南檔案..."
rm -f QUICK_LINE_BOT_FIX.md
rm -f LINE_BOT_SDK_FIX.md
rm -f DOCKER_BUILD_FIX.md
rm -f VERTEX_AI_UPDATE_GUIDE.md

# 刪除測試和備用檔案
echo "🧪 刪除測試和備用檔案..."
rm -f requirements-test.txt
rm -f Dockerfile.simple
rm -f local_test_memory_storage.py

# 刪除系統檔案
echo "💻 刪除系統檔案..."
rm -f .DS_Store
rm -rf __pycache__
rm -rf venv

# 刪除舊的說明檔案
echo "📚 刪除舊的說明檔案..."
rm -f ai_team.md
rm -f package.json

echo "✅ 清理完成！"
echo ""
echo "📋 保留的核心檔案："
echo "  - app.py (主應用程式)"
echo "  - ai_logic.py (AI 邏輯)"
echo "  - simple_memory.py (記憶系統)"
echo "  - prompt_variations.py (提示詞變體)"
echo "  - requirements.txt (依賴)"
echo "  - Dockerfile (容器配置)"
echo "  - railway.json (Railway 配置)"
echo "  - README.md (專案說明)"
echo "  - *.md (部署和功能指南)"
echo "  - memory_test.py (記憶測試工具)" 