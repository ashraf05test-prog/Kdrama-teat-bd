FROM python:3.11-slim

# Combine apt commands to reduce layers and avoid cache issues
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    wget \
    gcc \
    fontconfig \
    fonts-noto \
    fonts-noto-cjk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# yt-dlp install separately (it's Python, no need in apt)
RUN pip install --no-cache-dir yt-dlp

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Font cache after copy (if any local fonts)
RUN fc-cache -fv

CMD gunicorn --timeout 3600 --workers 1 --bind 0.0.0.0:$PORT app:app
