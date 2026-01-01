# Filmer - AI-Assisted Movie Critique Video Generation

A production-ready system for generating movie critique videos using semantic search to match narration with video segments.

## Architecture

The system follows a **stage-based pipeline architecture** with clear separation of concerns:

- **Domain Logic** (`src/core/`): Business rules without external dependencies
- **Infrastructure** (`src/adapters/`): External service adapters (ChromaDB, FFmpeg, Embedding models)
- **Orchestration** (`src/stages/`): Pipeline stages implementing BaseStage interface
- **Contracts** (`src/contracts/`): Shared schemas and data models

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

1. **Create a project workspace:**
   ```bash
   mkdir -p projects/{project_id}/data
   ```

2. **Add your files:**
   - `projects/{project_id}/data/movie.srt` - Movie subtitles
   - `projects/{project_id}/data/narration.srt` - Narration subtitles
   - `projects/{project_id}/data/narration.m4a` - Narration audio (optional)
   - `projects/{project_id}/data/movie.mp4` - Reference video (optional)

3. **Create project config:**
   ```bash
   mkdir -p projects/{project_id}/configs
   ```
   Create `projects/{project_id}/configs/project.json`:
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

4. **Run the pipeline:**
   ```bash
   python scripts/run_pipeline.py --project-id tt0133093
   ```

### Running Individual Stages

```bash
# Run ingest stage
python scripts/run_stage.py ingest --project-id tt0133093

# Run index stage
python scripts/run_stage.py index --project-id tt0133093

# Run search stage
python scripts/run_stage.py search --project-id tt0133093

# Run timeline stage
python scripts/run_stage.py timeline --project-id tt0133093

# Run render stage
python scripts/run_stage.py render --project-id tt0133093 --ffmpeg-path "C:/path/to/ffmpeg.exe"
```

## Pipeline Stages

1. **Ingest**: Validates and locates project files
2. **Index**: Chunks and indexes movie subtitles in ChromaDB
3. **Search**: Semantic search for narration in movie subtitles
4. **Timeline**: Generates timeline JSON from search matches
5. **Render**: Renders final video using FFmpeg

## Legacy Support

The original `cut_video.py` tool is preserved in `legacy/` and remains fully functional. You can use it directly with `timeline.json` files:

```bash
python legacy/cut_video.py
```

## Project Structure

```
projects/{project_id}/
  data/          # Input files
  index/         # ChromaDB index
  configs/       # Project configuration
  outputs/       # Generated files (timeline.json, final.mp4)
  logs/          # Stage execution logs
```

## Timeline JSON Format

The timeline JSON format is backward compatible with the legacy format:

```json
{
  "input": "path/to/video.mp4",
  "narration": "path/to/narration.m4a",
  "output": "path/to/output.mp4",
  "segments": [
    { "start": 0.5, "end": 3.2, "score": 0.82 },
    { "start": 15.0, "end": 18.4, "score": 0.79 }
  ]
}
```

Extended fields (spoiler risk, transitions, overlays, etc.) are optional and maintain backward compatibility.

## Requirements

- Python 3.8+
- FFmpeg (for video rendering)
- ChromaDB (for vector search)
- sentence-transformers (for embeddings)

## License

[Your License Here]

