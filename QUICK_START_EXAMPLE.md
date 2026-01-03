# راهنمای سریع: مثال imdb123123

## 📁 فایل‌های شما

- **فیلم**: `films/input/3034981-0-FoxandHareSavetheForest-1080.mp4`
- **زیرنویس فیلم**: `films/input/3034981-0-FoxandHareSavetheForest-1080.srt` ✅
- **نقد صوتی**: `films/narration/imdb123123.m4a` ✅
- **زیرنویس نقد**: `films/narration/imdb123123.srt` ⚠️ **نیاز دارید**

## ⚠️ مرحله 0: تهیه فایل زیرنویس نقد

اگر فایل SRT نقد ندارید، باید از فایل صوتی استخراج کنید:

### گزینه 1: استفاده از Whisper (پیشنهادی)

```bash
# نصب Whisper
pip install openai-whisper

# استخراج SRT
whisper films/narration/imdb123123.m4a --language en --output_format srt --output_dir films/narration/
```

این دستور فایل `imdb123123.srt` را در `films/narration/` ایجاد می‌کند.

### گزینه 2: استفاده از سرویس آنلاین

از سرویس‌های Speech-to-Text آنلاین استفاده کنید و فایل SRT را در `films/narration/imdb123123.srt` ذخیره کنید.

---

## 🚀 مراحل اجرا

### مرحله 1: محاسبه مدت زمان فیلم

```bash
# Windows (PowerShell)
ffprobe -i "films/input/3034981-0-FoxandHareSavetheForest-1080.mp4" -show_entries format=duration -v quiet -of csv="p=0"
```

یا از Python:
```python
import subprocess
result = subprocess.run(
    ['ffprobe', '-i', 'films/input/3034981-0-FoxandHareSavetheForest-1080.mp4', 
     '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0'],
    capture_output=True, text=True
)
duration = float(result.stdout.strip())
print(f"Duration: {duration} seconds")
```

**نکته**: مقدار `duration` را یادداشت کنید (مثلاً `3600` برای 1 ساعت).

---

### مرحله 2: ایجاد پروژه

```bash
python scripts/create_project.py \
  --project-id imdb123123 \
  --movie-duration 3600 \
  --movie-language en \
  --movie-srt films/input/3034981-0-FoxandHareSavetheForest-1080.srt \
  --narration-srt films/narration/imdb123123.srt \
  --movie-video films/input/3034981-0-FoxandHareSavetheForest-1080.mp4 \
  --embedding-model sentence-transformers/all-MiniLM-L6-v2 \
  --similarity-threshold 0.75 \
  --copyright-min-gap 30.0
```

**⚠️ مهم**: مقدار `--movie-duration` را با مدت زمان واقعی فیلم جایگزین کنید.

---

### مرحله 3: اجرای Pipeline

```bash
# مرحله 1: Ingest
python scripts/run_stage.py ingest --project-id imdb123123

# مرحله 2: Index (ایجاد Embedding و ذخیره در ChromaDB)
python scripts/run_stage.py index --project-id imdb123123 --embedding-model sentence-transformers/all-MiniLM-L6-v2

# مرحله 3: Search (جستجوی Semantic)
python scripts/run_stage.py search --project-id imdb123123 --embedding-model sentence-transformers/all-MiniLM-L6-v2

# مرحله 4: Timeline (تولید JSON)
python scripts/run_stage.py timeline --project-id imdb123123
```

---

### مرحله 4: تبدیل به فرمت Legacy (اختیاری)

اگر می‌خواهید فرمت دقیقاً مثل `mix/imdb123123.json` باشد:

```bash
python scripts/convert_timeline_to_legacy.py --project-id imdb123123
```

این دستور فایل `projects/imdb123123/outputs/timeline_legacy.json` را ایجاد می‌کند.

---

## 📄 خروجی نهایی

### فایل اصلی:
```
projects/imdb123123/outputs/timeline.json
```

### فایل Legacy (اگر تبدیل کردید):
```
projects/imdb123123/outputs/timeline_legacy.json
```

### محتوای فایل:
```json
{
  "input": "films\\3034981-0-FoxandHareSavetheForest-1080.mp4",
  "output": "output_cut.mp4",
  "segments": [
    { "start": 0.50, "end": 3.20 },
    { "start": 5.00, "end": 8.40 },
    { "start": 10.00, "end": 13.75 }
  ]
}
```

---

## 🎯 اجرای یکجا (Quick Script)

### Windows:
```bash
# ویرایش فایل scripts/quick_start_example.bat
# مقدار MOVIE_DURATION را تغییر دهید
# سپس اجرا کنید:
scripts\quick_start_example.bat
```

### Linux/Mac:
```bash
# ویرایش فایل scripts/quick_start_example.sh
# مقدار MOVIE_DURATION را تغییر دهید
# سپس اجرا کنید:
chmod +x scripts/quick_start_example.sh
./scripts/quick_start_example.sh
```

---

## 🔍 بررسی موفقیت

```bash
# بررسی خروجی
cat projects/imdb123123/outputs/timeline.json

# یا در Windows:
type projects\imdb123123\outputs\timeline.json

# بررسی تعداد segments
python -c "import json; data=json.load(open('projects/imdb123123/outputs/timeline.json')); print(f'Segments: {len(data[\"segments\"])}')"
```

---

## ⚠️ مشکلات رایج

### مشکل 1: فایل SRT نقد پیدا نمی‌شود
```
Error: Narration SRT file not found
```
**راه‌حل**: مطمئن شوید فایل `films/narration/imdb123123.srt` وجود دارد.

### مشکل 2: مدت زمان فیلم اشتباه است
**راه‌حل**: از `ffprobe` استفاده کنید و مقدار دقیق را وارد کنید.

### مشکل 3: Embedding Model دانلود نمی‌شود
**راه‌حل**: اتصال اینترنت را بررسی کنید. مدل ~90MB است.

---

## 📝 خلاصه دستورات

```bash
# 1. استخراج SRT از صدا (اگر نیاز دارید)
whisper films/narration/imdb123123.m4a --language en --output_format srt --output_dir films/narration/

# 2. محاسبه مدت زمان
ffprobe -i "films/input/3034981-0-FoxandHareSavetheForest-1080.mp4" -show_entries format=duration -v quiet -of csv="p=0"

# 3. ایجاد پروژه (duration را جایگزین کنید)
python scripts/create_project.py --project-id imdb123123 --movie-duration 3600 --movie-language en --movie-srt films/input/3034981-0-FoxandHareSavetheForest-1080.srt --narration-srt films/narration/imdb123123.srt --movie-video films/input/3034981-0-FoxandHareSavetheForest-1080.mp4

# 4. اجرای Pipeline
python scripts/run_stage.py ingest --project-id imdb123123
python scripts/run_stage.py index --project-id imdb123123
python scripts/run_stage.py search --project-id imdb123123
python scripts/run_stage.py timeline --project-id imdb123123

# 5. تبدیل به Legacy (اختیاری)
python scripts/convert_timeline_to_legacy.py --project-id imdb123123
```

---

**آماده!** 🎉

