# telegram_bot/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot_aiogram.py .

CMD ["python", "bot_aiogram.py"]