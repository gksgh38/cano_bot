FROM python:3.9-slim

# 필수 패키지 및 폰트 설치 (NanumGothic + FFmpeg)
RUN apt-get update && \
    apt-get install -y fonts-nanum ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 복사 후 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 파일들 복사
COPY . .

# 봇 실행
CMD ["python", "bot.py"]
