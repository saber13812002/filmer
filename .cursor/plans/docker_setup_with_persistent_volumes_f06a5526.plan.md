---
name: Docker Setup with Persistent Volumes
overview: ایجاد Dockerfile و docker-compose.yml برای اجرای پروژه در container با persistent volumes برای فایل‌های فیلم، زیرنویس، نقد، و خروجی‌ها
todos: []
---

# Docker Setup ب

ا Persistent Volumes

## هدف

ایجاد Dockerfile و docker-compose.yml برای اجرای پروژه در container با persistent storage برای:

- فایل‌های فیلم و زیرنویس (films/)
- فایل‌های نقد (narration)
- خروجی‌ها (projects/, timeline.json)
- داده‌های ChromaDB و cache

## فایل‌های ایجاد/ویرایش

### 1. Dockerfile

**مسیر**: `Dockerfile`

- Base image: `python:3.11-slim`
- نصب FFmpeg
- نصب dependencies از requirements.txt
- تنظیم working directory
- کپی فایل‌های کد (بدون فایل‌های پرحجم)

### 2. docker-compose.yml

**مسیر**: `docker-compose.yml`

- تعریف service برای filmer
- Volume mapping برای:
- `./films:/app/films` (فیلم‌ها و زیرنویس‌ها)
- `./projects:/app/projects` (خروجی‌ها و داده‌های پروژه)
- `./mix:/app/mix` (JSON خروجی‌های legacy)
- `./timeline.json:/app/timeline.json` (timeline خروجی)

### 3. .dockerignore

**مسیر**: `.dockerignore`

- فایل‌های پرحجم که نباید در image باشند:
- `films/input/*.mp4`
- `films/narration/*.m4a`
- `films/output/*.mp4`
- `projects/` (داده‌های runtime)
- `__pycache__/`
- `.git/`

### 4. به‌روزرسانی .gitignore

**مسیر**: `.gitignore`

- اطمینان از ignore شدن فایل‌های پرحجم:
- `films/input/*.mp4`
- `films/narration/*.m4a`
- `films/output/*.mp4`
- `projects/` (داده‌های runtime)

## ساختار Volume Mapping

```javascript
Host (Linux)              Container
─────────────────────────────────────────
./films/              →   /app/films/
  input/              →     input/
    *.mp4 (persist)   →       *.mp4
    *.srt (persist)   →       *.srt
  narration/          →     narration/
    *.m4a (persist)   →       *.m4a
    *.srt (persist)   →       *.srt
  output/             →     output/
    *.mp4 (persist)   →       *.mp4

./projects/           →   /app/projects/
  {id}/               →     {id}/
    data/             →       data/
    index/chroma/     →       index/chroma/
    index/embeddings_cache/ → index/embeddings_cache/
    outputs/          →       outputs/
    configs/          →       configs/
    logs/             →       logs/

./mix/                →   /app/mix/
  *.json (persist)    →     *.json

./timeline.json       →   /app/timeline.json
```



## محتوای Dockerfile

```dockerfile
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
```



## محتوای docker-compose.yml

```yaml
version: '3.8'

services:
  filmer:
    build: .
    container_name: filmer
    volumes:
      # فایل‌های فیلم و زیرنویس
    - ./films:/app/films
      # خروجی‌ها و داده‌های پروژه
    - ./projects:/app/projects
      # JSON خروجی‌های legacy
    - ./mix:/app/mix
      # Timeline خروجی
    - ./timeline.json:/app/timeline.json
    working_dir: /app
    stdin_open: true
    tty: true
    # برای دسترسی به GPU (اختیاری)
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]
```



## محتوای .dockerignore

```javascript
# فایل‌های پرحجم
films/input/*.mp4
films/narration/*.m4a
films/output/*.mp4

# داده‌های runtime
projects/
__pycache__/
*.pyc
*.pyo
*.pyd

# Git
.git/
.gitignore

# IDE
.vscode/
.idea/

# Logs
*.log

# Test outputs
test_*.py
```



## استفاده

### Build و Run:

```bash
docker-compose build
docker-compose up -d
docker-compose exec filmer python scripts/create_project.py ...
docker-compose exec filmer python scripts/run_stage.py ...
```



### دسترسی به Shell:

```bash
docker-compose exec filmer bash
```



## مزایا

1. **Persistent Storage**: همه فایل‌ها با restart از بین نمی‌روند
2. **Separation**: فایل‌های پرحجم در image نیستند
3. **Portability**: قابل اجرا روی هر ماشین لینوکس
4. **Git-friendly**: فقط کد و فایل‌های کوچک در git

## نکات

- فایل‌های SRT کوچک می‌توانند در git باشند
- فایل‌های MP4/M4A باید از git ignore شوند