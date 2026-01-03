"""Convert timeline.json to legacy format (like mix/imdb123123.json)"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def convert_timeline_to_legacy(timeline_path: Path, output_path: Path = None):
    """Convert timeline.json to legacy format"""
    
    # Read timeline.json
    with open(timeline_path, 'r', encoding='utf-8') as f:
        timeline_data = json.load(f)
    
    # Convert to legacy format
    legacy_data = {
        "input": timeline_data.get("input", "").replace("/", "\\"),  # Windows path format
        "output": timeline_data.get("output", "output_cut.mp4"),
        "segments": [
            {
                "start": seg.get("start", 0),
                "end": seg.get("end", 0)
            }
            for seg in timeline_data.get("segments", [])
        ]
    }
    
    # Save output
    if output_path is None:
        output_path = timeline_path.parent / "timeline_legacy.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(legacy_data, f, indent=2)
    
    print(f"[OK] Legacy timeline saved to: {output_path}")
    print(f"  Segments: {len(legacy_data['segments'])}")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Convert timeline.json to legacy format"
    )
    parser.add_argument("--project-id", required=True, help="Project identifier")
    parser.add_argument("--output", type=Path, help="Output path (default: projects/{id}/outputs/timeline_legacy.json)")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    
    args = parser.parse_args()
    
    # Find timeline.json
    if args.project_root:
        timeline_path = args.project_root / "projects" / args.project_id / "outputs" / "timeline.json"
    else:
        timeline_path = Path("projects") / args.project_id / "outputs" / "timeline.json"
    
    if not timeline_path.exists():
        print(f"Error: Timeline file not found: {timeline_path}", file=sys.stderr)
        sys.exit(1)
    
    # Convert
    output_path = args.output
    convert_timeline_to_legacy(timeline_path, output_path)


if __name__ == "__main__":
    main()

