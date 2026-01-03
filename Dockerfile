FROM python:3.11-slim

# نصب FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# تنظیم working directory
WORKDIR /app

# کپی requirements و نصب dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کد (با .dockerignore فایل‌های پرحجم ignore می‌شوند)
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "scripts/run_stage.py", "--help"]

