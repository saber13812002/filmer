# راهنمای کامل Pipeline: از ایجاد پروژه تا خروجی نهایی

## 📋 فهرست مطالب

1. [پیش‌نیازها](#پیش‌نیازها)
2. [نصب وابستگی‌ها](#نصب-وابستگی‌ها)
3. [تنظیم ChromaDB](#تنظیم-chromadb)
4. [تنظیم Embedding Model](#تنظیم-embedding-model)
5. [ایجاد پروژه](#ایجاد-پروژه)
6. [اجرای Pipeline](#اجرای-pipeline)
7. [دیباگ و Troubleshooting](#دیباگ-و-troubleshooting)
8. [بررسی موفقیت](#بررسی-موفقیت)

---

## پیش‌نیازها

### فایل‌های مورد نیاز:
- `movie.srt` - زیرنویس کامل فیلم (2 ساعت)
- `narration1.srt` - فایل نقد اول (10-20 دقیقه)
- `narration2.srt` - فایل نقد دوم (اختیاری)
- `movie.mp4` - فایل ویدیو (اختیاری)

### ساختار فایل‌ها:
```
your_files/
├── movie.srt
├── narration1.srt
└── narration2.srt (اختیاری)
```

---

## نصب وابستگی‌ها

```bash
# نصب پکیج‌های اصلی
pip install pydantic>=2.0.0 chromadb>=0.4.0 sentence-transformers>=2.2.0 numpy>=1.24.0

# بررسی نصب
python -c "import chromadb; import sentence_transformers; print('[OK] All packages installed')"
```

---

## تنظیم ChromaDB

ChromaDB به صورت **خودکار** تنظیم می‌شود. تنظیمات:

- **مسیر ذخیره‌سازی**: `projects/{project_id}/index/chroma/`
- **نوع**: Persistent (ذخیره دائمی در دیسک)
- **Telemetry**: غیرفعال

### بررسی ChromaDB:
```bash
python -c "import chromadb; print(f'ChromaDB version: {chromadb.__version__}')"
```

---

## تنظیم Embedding Model

### گزینه A: مدل آفلاین (پیشنهادی)

**مدل پیش‌فرض:**
```bash
sentence-transformers/all-MiniLM-L6-v2
```
- حجم: ~90 MB
- دقت: خوب برای انگلیسی
- دانلود: خودکار در اولین استفاده

**مدل‌های جایگزین:**
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (چندزبانه)
- `sentence-transformers/all-mpnet-base-v2` (دقت بالاتر)

### گزینه B: مدل آنلاین (API)

برای استفاده از API (مثلاً OpenAI)، فایل `src/adapters/embedding_adapter.py` را ویرایش کنید.

---

## ایجاد پروژه

### دستور کامل:
```bash
python scripts/create_project.py \
  --project-id tt0133093 \
  --movie-duration 7200 \
  --movie-language en \
  --movie-srt path/to/movie.srt \
  --narration-srt path/to/narration1.srt \
  --narration-srt path/to/narration2.srt \
  --movie-video path/to/movie.mp4 \
  --embedding-model sentence-transformers/all-MiniLM-L6-v2 \
  --similarity-threshold 0.75 \
  --copyright-min-gap 30.0
```

### پارامترها:
- `--project-id`: شناسه پروژه (IMDb ID یا نام دلخواه)
- `--movie-duration`: مدت زمان فیلم به ثانیه
- `--movie-language`: کد زبان (en, fa, ...)
- `--movie-srt`: مسیر فایل SRT فیلم
- `--narration-srt`: مسیر فایل SRT نقد (قابل تکرار)
- `--movie-video`: مسیر فایل ویدیو (اختیاری)
- `--embedding-model`: نام مدل embedding
- `--similarity-threshold`: حد آستانه similarity (0-1)
- `--copyright-min-gap`: حداقل فاصله زمانی برای کپی‌رایت (ثانیه)

### خروجی موفق:
```
[OK] Copied movie SRT: projects/tt0133093/data/movie.srt
[OK] Copied narration SRT 1: projects/tt0133093/data/narration1.srt
[OK] Project created successfully!
```

---

## اجرای Pipeline

### مرحله 1: Ingest (اعتبارسنجی فایل‌ها)

```bash
python scripts/run_stage.py ingest --project-id tt0133093
```

**خروجی:**
- `projects/tt0133093/outputs/ingest_output.json`

**بررسی:**
```bash
cat projects/tt0133093/outputs/ingest_output.json
```

---

### مرحله 2: Index (ایجاد Embedding و ذخیره در ChromaDB)

```bash
python scripts/run_stage.py index \
  --project-id tt0133093 \
  --embedding-model sentence-transformers/all-MiniLM-L6-v2 \
  --log-level DEBUG
```

**این مرحله:**
1. SRT فیلم را parse می‌کند
2. با 3-sentence chunking تقسیم می‌کند
3. برای هر chunk embedding می‌سازد
4. در ChromaDB ذخیره می‌کند

**خروجی:**
- `projects/tt0133093/outputs/index_output.json`
- `projects/tt0133093/index/chroma/` (ChromaDB data)

**بررسی:**
```bash
cat projects/tt0133093/outputs/index_output.json
ls -la projects/tt0133093/index/chroma/
```

---

### مرحله 3: Search (جستجوی Semantic)

```bash
python scripts/run_stage.py search \
  --project-id tt0133093 \
  --embedding-model sentence-transformers/all-MiniLM-L6-v2 \
  --log-level DEBUG
```

**این مرحله:**
1. فایل‌های narration را parse می‌کند
2. با 3-sentence window chunking می‌کند
3. برای هر chunk embedding می‌سازد
4. در ChromaDB جستجو می‌کند
5. top 3 matches را برمی‌گرداند

**خروجی:**
- `projects/tt0133093/outputs/search_output.json`

**بررسی:**
```bash
cat projects/tt0133093/outputs/search_output.json | head -50
```

---

### مرحله 4: Timeline (تولید timeline.json)

```bash
python scripts/run_stage.py timeline --project-id tt0133093
```

**این مرحله:**
1. نتایج search را می‌خواند
2. Copyright compliance اعمال می‌کند
3. Timeline با بازه‌های 3-5 ثانیه‌ای می‌سازد
4. `timeline.json` تولید می‌کند

**خروجی:**
- `projects/tt0133093/outputs/timeline.json`

**بررسی:**
```bash
cat projects/tt0133093/outputs/timeline.json
```

---

## اجرای یکجا (Script)

فایل `run_full_pipeline.sh` ایجاد کنید:

```bash
#!/bin/bash
PROJECT_ID="tt0133093"

echo "=== Step 1: Ingest ==="
python scripts/run_stage.py ingest --project-id $PROJECT_ID || exit 1

echo "=== Step 2: Index ==="
python scripts/run_stage.py index --project-id $PROJECT_ID || exit 1

echo "=== Step 3: Search ==="
python scripts/run_stage.py search --project-id $PROJECT_ID || exit 1

echo "=== Step 4: Timeline ==="
python scripts/run_stage.py timeline --project-id $PROJECT_ID || exit 1

echo "=== [OK] Pipeline completed! ==="
```

اجرا:
```bash
chmod +x run_full_pipeline.sh
./run_full_pipeline.sh
```

---

## دیباگ و Troubleshooting

### مشکل 1: خطای Import

**خطا:**
```
ModuleNotFoundError: No module named 'chromadb'
```

**راه‌حل:**
```bash
pip install chromadb sentence-transformers
```

---

### مشکل 2: خطای Embedding Model

**خطا:**
```
OSError: Can't load tokenizer
```

**راه‌حل:**
```bash
# دانلود دستی مدل
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

---

### مشکل 3: خطای ChromaDB

**خطا:**
```
Permission denied در chroma/
```

**راه‌حل:**
```bash
chmod -R 755 projects/tt0133093/index/chroma/
```

---

### مشکل 4: خطای SRT Parse

**بررسی فرمت SRT:**
```bash
head -20 path/to/movie.srt
```

**فرمت صحیح:**
```
1
00:00:01,000 --> 00:00:03,500
متن زیرنویس

2
00:00:03,500 --> 00:00:06,000
متن بعدی
```

---

### مشکل 5: Embedding خیلی کند

**Cache به صورت خودکار فعال است:**
- مسیر: `projects/{id}/index/embeddings_cache/`
- بررسی: `ls -la projects/tt0133093/index/embeddings_cache/ | wc -l`

---

## بررسی موفقیت

### تست Embedding Model

فایل `test_embedding.py`:

```python
from src.adapters.embedding_adapter import EmbeddingAdapter
from pathlib import Path
import numpy as np

adapter = EmbeddingAdapter(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_dir=Path("test_cache")
)

text1 = "This is a test sentence"
text2 = "This is another test sentence"
text3 = "Completely different topic"

emb1 = adapter.embed_text(text1)
emb2 = adapter.embed_text(text2)
emb3 = adapter.embed_text(text3)

print(f"Embedding dimension: {len(emb1)}")
print(f"Model loaded: {adapter._model is not None}")

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

sim_12 = cosine_similarity(emb1, emb2)
sim_13 = cosine_similarity(emb1, emb3)

print(f"Similarity 1-2 (should be high): {sim_12:.3f}")
print(f"Similarity 1-3 (should be low): {sim_13:.3f}")

if sim_12 > 0.7 and sim_13 < 0.5:
    print("[OK] Embedding model is working correctly!")
```

اجرا:
```bash
python test_embedding.py
```

---

### تست ChromaDB

فایل `test_chromadb.py`:

```python
from src.adapters.chromadb_adapter import ChromaDBAdapter
from pathlib import Path

adapter = ChromaDBAdapter(persist_directory=Path("test_chroma"))
collection = adapter.get_or_create_collection("test_collection")

adapter.add_chunks(
    collection_name="test_collection",
    chunks=["This is a test document"],
    embeddings=[[0.1] * 384],
    metadatas=[{"test": True}],
    ids=["test_1"]
)

results = adapter.query(
    collection_name="test_collection",
    query_embeddings=[[0.1] * 384],
    n_results=1
)

print(f"Collection created: {collection is not None}")
print(f"Query results: {len(results.get('ids', [[]])[0])} results")
print("[OK] ChromaDB is working correctly!")
```

اجرا:
```bash
python test_chromadb.py
```

---

### بررسی نهایی

```bash
# بررسی همه خروجی‌ها
ls -lh projects/tt0133093/outputs/

# بررسی timeline
cat projects/tt0133093/outputs/timeline.json | jq '.segments | length'

# بررسی ChromaDB
du -sh projects/tt0133093/index/chroma/

# بررسی Cache
du -sh projects/tt0133093/index/embeddings_cache/
```

---

## نکات مهم

1. **Embedding Model**: برای اولین بار دانلود می‌شود (~90MB)
2. **ChromaDB**: به صورت خودکار در `projects/{id}/index/chroma/` ذخیره می‌شود
3. **Cache**: Embeddings در `projects/{id}/index/embeddings_cache/` cache می‌شوند
4. **Logs**: لاگ‌ها در `projects/{id}/logs/` ذخیره می‌شوند
5. **Copyright Compliance**: حداقل 30 ثانیه فاصله بین segments

---

## ساختار پروژه نهایی

```
projects/tt0133093/
├── data/
│   ├── movie.srt
│   ├── narration1.srt
│   └── movie.mp4
├── index/
│   ├── chroma/          # ChromaDB data
│   └── embeddings_cache/ # Embedding cache
├── configs/
│   └── project.json
├── outputs/
│   ├── ingest_output.json
│   ├── index_output.json
│   ├── search_output.json
│   └── timeline.json     # خروجی نهایی
└── logs/
    ├── ingest.log
    ├── index.log
    ├── search.log
    └── timeline.log
```

---

## پشتیبانی

اگر خطایی رخ داد:
1. خروجی کامل خطا را بررسی کنید
2. لاگ‌ها را در `projects/{id}/logs/` چک کنید
3. فایل‌های خروجی هر stage را بررسی کنید

---

**آخرین به‌روزرسانی**: 2026-01-01

