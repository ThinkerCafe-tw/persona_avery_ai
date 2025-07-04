FROM python:3.10-slim-buster

WORKDIR /app

# 安裝 psycopg2-binary 所需的系統依賴
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT 8080
EXPOSE $PORT

CMD python3 -m gunicorn app:app --bind 0.0.0.0:$PORT --log-level debug