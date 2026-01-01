# Quick Start - TimelineStage MVP

این راهنما برای تست سریع TimelineStage MVP و اثبات معماری است.

## پیش‌نیازها

- Python 3.8+
- فایل‌های پروژه در `projects/{project_id}/data/` (اختیاری برای MVP)

## گام 1: تست ساده با Mock Data

```bash
python scripts/run_timeline_mvp.py --project-id test_project
```

این دستور:
- یک پروژه تست می‌سازد
- با mock segments یک timeline.json تولید می‌کند
- خروجی را در `projects/test_project/outputs/timeline.json` ذخیره می‌کند

## گام 2: تست با Segments سفارشی

```bash
python scripts/run_timeline_mvp.py --project-id test_project --segments 0.5 3.2 15.0 18.4 110.0 113.75
```

این دستور timeline.json را با segments مشخص شده تولید می‌کند.

## گام 3: تست با Legacy Cutter

1. Timeline JSON را به root directory کپی کنید:
   ```bash
   copy projects\test_project\outputs\timeline.json timeline.json
   ```

2. Legacy cutter را اجرا کنید:
   ```bash
   python legacy/cut_video.py
   ```

3. ویدیو نهایی در مسیر مشخص شده در timeline.json تولید می‌شود.

## ساختار پروژه

```
projects/test_project/
  configs/
    project.json          # Project configuration
  outputs/
    timeline.json         # Generated timeline (compatible with legacy cutter)
  data/                   # (Optional) Input files
    movie.srt
    narration.srt
    movie.mp4
    narration.m4a
```

## مثال Project Config

```json
{
  "movie_id": "tt0133093",
  "options": {
    "similarity_threshold": 0.75,
    "min_segment_length": 3.0,
    "preset": "standard"
  }
}
```

## نکات مهم

- TimelineStage MVP می‌تواند **مستقل** کار کند (نیازی به search stage ندارد)
- Timeline JSON تولید شده **100% سازگار** با legacy cutter است
- می‌تواند از mock data، config، یا search output استفاده کند
- این MVP برای **اثبات معماری** و **تست contract** طراحی شده است

## بعد از تست موفق

وقتی timeline.json با legacy cutter کار کرد، می‌توانید:
1. بقیه stages را پیاده‌سازی کنید (ingest, index, search)
2. TimelineStage اصلی را که از search output استفاده می‌کند، فعال کنید
3. API layer را اضافه کنید

