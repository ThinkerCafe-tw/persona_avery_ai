FROM python:3.10-slim-buster

# 設定工作目錄
WORKDIR /app

# 安裝 psycopg2-binary 所需的系統依賴
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案檔案
COPY . .

# 暴露 Railway 指定的 PORT（不是寫死 8080！）
EXPOSE $PORT

# 啟動指令：先印出 PORT 變數供日誌追蹤，再用 $PORT 啟動 Gunicorn
CMD [ "/bin/sh", "-c", "echo \"---> Starting on PORT: $PORT\" && python3 -m gunicorn app:app --bind 0.0.0.0:$PORT --log-level debug" ]