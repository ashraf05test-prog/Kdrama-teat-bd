FROM python:3.11-slim

RUN sed -i 's/deb.debian.org/httpredir.debian.org/g' /etc/apt/sources.list

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    ffmpeg wget gcc fontconfig && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    fonts-noto fonts-noto-cjk && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /var/cache/apt/* && \
    fc-cache -fv

RUN pip install --no-cache-dir yt-dlp

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--timeout", "3600", "--workers", "1", "--bind", "0.0.0.0:$PORT", "app:app"]
