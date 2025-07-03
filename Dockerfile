FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT 8080
EXPOSE $PORT

CMD python3 -m gunicorn app:app --bind 0.0.0.0:$PORT --log-level debug