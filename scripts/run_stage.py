"""CLI script for running individual pipeline stages"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stages.ingest import IngestStage
from src.stages.index import IndexStage
from src.stages.search import SearchStage
from src.stages.timeline import TimelineStage
from src.stages.render import RenderStage
from src.utils.logging_config import setup_logging


STAGES = {
    "ingest": IngestStage,
    "index": IndexStage,
    "search": SearchStage,
    "timeline": TimelineStage,
    "render": RenderStage
}


def main():
    parser = argparse.ArgumentParser(description="Run a single pipeline stage")
    parser.add_argument("stage", choices=list(STAGES.keys()), help="Stage to run")
    parser.add_argument("--project-id", required=True, help="Project identifier")
    parser.add_argument("--ffmpeg-path", help="Path to FFmpeg executable")
    parser.add_argument("--embedding-model", default="sentence-transformers/all-MiniLM-L6-v2", help="Embedding model name")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    args = parser.parse_args()
    
    # Setup logging
    log_file = None
    if args.project_root:
        log_file = args.project_root / "projects" / args.project_id / "logs" / f"{args.stage}.log"
    setup_logging(log_file=log_file, level=getattr(__import__("logging"), args.log_level))
    
    # Get stage class
    stage_class = STAGES[args.stage]
    
    # Initialize stage
    if args.stage == "render":
        stage = stage_class(project_root=args.project_root, ffmpeg_path=args.ffmpeg_path)
    elif args.stage in ["index", "search"]:
        stage = stage_class(project_root=args.project_root, embedding_model=args.embedding_model)
    else:
        stage = stage_class(project_root=args.project_root)
    
    # Run stage
    try:
        print(f"Running {args.stage} stage for project {args.project_id}...")
        result = stage.run(args.project_id)
        output_path = stage.save_output(args.project_id, result)
        print(f"Stage completed successfully. Output saved to: {output_path}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

