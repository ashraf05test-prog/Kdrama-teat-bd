FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    fonts-noto \
    fonts-noto-cjk \
    wget \
    gcc \
    fontconfig \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install yt-dlp

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN fc-cache -fv

CMD gunicorn --timeout 3600 --workers 1 --bind 0.0.0.0:$PORT app:app
