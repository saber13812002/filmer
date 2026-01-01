# Legacy Tools

This directory contains the original standalone video cutting tool.

## cut_video.py

Original FFmpeg-based video cutter. Can be used directly with `timeline.json` files.

### Usage

```bash
python legacy/cut_video.py
```

The script reads `timeline.json` from the current directory and processes the video according to the segments defined in it.

### Timeline JSON Format

```json
{
  "input": "path/to/video.mp4",
  "narration": "path/to/narration.m4a",
  "output": "path/to/output.mp4",
  "segments": [
    { "start": 0.5, "end": 3.2 },
    { "start": 15.0, "end": 18.4 }
  ]
}
```

This tool remains unchanged and fully functional as a standalone utility.

