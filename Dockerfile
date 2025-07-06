# 使用 Python 3.11 slim 映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 設定環境變數
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴檔案
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# 複製應用程式
COPY . .

# 創建非 root 用戶
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# 暴露端口
EXPOSE 8080

# 啟動應用程式 - 使用環境變數 PORT，加強日誌
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --workers=1 --log-level=debug --timeout=120 app:app"]