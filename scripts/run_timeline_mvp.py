"""CLI script for running TimelineStage MVP"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stages.timeline_mvp import TimelineStageMVP


def main():
    parser = argparse.ArgumentParser(
        description="Run TimelineStage MVP - Generate timeline.json (standalone, no dependencies)"
    )
    parser.add_argument("--project-id", required=True, help="Project identifier")
    parser.add_argument("--segments", nargs="+", type=float, help="Custom segments as start1 end1 start2 end2 ...")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    
    args = parser.parse_args()
    
    # Initialize stage
    stage = TimelineStageMVP(project_root=args.project_root)
    
    # Prepare config with custom segments if provided
    config = None
    if args.segments:
        if len(args.segments) % 2 != 0:
            print("Error: Segments must be pairs of start/end times", file=sys.stderr)
            sys.exit(1)
        
        segments = []
        for i in range(0, len(args.segments), 2):
            segments.append({
                "start": args.segments[i],
                "end": args.segments[i + 1]
            })
        config = {"segments": segments}
    
    # Run stage
    try:
        print(f"Running TimelineStage MVP for project: {args.project_id}")
        result = stage.run(args.project_id, config=config)
        
        timeline_path = stage.get_outputs_path(args.project_id) / "timeline.json"
        
        print(f"\n[OK] Timeline generated successfully!")
        print(f"  Location: {timeline_path}")
        print(f"  Segments: {len(result['segments'])}")
        print(f"\nTo use with legacy cutter, copy timeline.json to project root:")
        print(f"  copy {timeline_path} timeline.json")
        print(f"  python legacy/cut_video.py")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

