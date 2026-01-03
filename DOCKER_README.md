# راهنمای استفاده از Docker

## ساختار Persistent Volumes

همه فایل‌های مهم به صورت volume mount شده‌اند و با restart container از بین نمی‌روند:

- `./films` → فایل‌های فیلم، زیرنویس و نقد
- `./projects` → خروجی‌ها، ChromaDB data و cache
- `./mix` → JSON خروجی‌های legacy
- `./timeline.json` → Timeline خروجی

## استفاده

### Build Image:
```bash
docker-compose build
```

### اجرای Container:
```bash
docker-compose up -d
```

### دسترسی به Shell:
```bash
docker-compose exec filmer bash
```

### اجرای دستورات:
```bash
# ایجاد پروژه
docker-compose exec filmer python scripts/create_project.py \
  --project-id imdb123123 \
  --movie-duration 3600 \
  --movie-language en \
  --movie-srt films/input/3034981-0-FoxandHareSavetheForest-1080.srt \
  --narration-srt films/narration/imdb123123.srt \
  --movie-video films/input/3034981-0-FoxandHareSavetheForest-1080.mp4

# اجرای Pipeline
docker-compose exec filmer python scripts/run_stage.py ingest --project-id imdb123123
docker-compose exec filmer python scripts/run_stage.py index --project-id imdb123123
docker-compose exec filmer python scripts/run_stage.py search --project-id imdb123123
docker-compose exec filmer python scripts/run_stage.py timeline --project-id imdb123123
```

### توقف Container:
```bash
docker-compose down
```

### مشاهده Logs:
```bash
docker-compose logs -f filmer
```

## نکات مهم

1. **فایل‌های پرحجم**: فایل‌های MP4/M4A در image نیستند، فقط در volume mount شده‌اند
2. **Persistent Data**: همه داده‌ها در `./projects/` و `./films/` persist می‌شوند
3. **Restart**: با `docker-compose restart` همه داده‌ها حفظ می‌شوند
4. **Git**: فقط فایل‌های کوچک (SRT, JSON) می‌توانند در git باشند

## ساختار Volume Mapping

```
Host Machine          Container
─────────────────────────────────────
./films/          →   /app/films/
./projects/       →   /app/projects/
./mix/            →   /app/mix/
./timeline.json   →   /app/timeline.json
```

## GPU Support (اختیاری)

اگر GPU دارید، در `docker-compose.yml` بخش GPU را uncomment کنید و nvidia-docker نصب کنید.

