"""CLI script for running full pipeline"""

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


def main():
    parser = argparse.ArgumentParser(description="Run full pipeline")
    parser.add_argument("--project-id", required=True, help="Project identifier")
    parser.add_argument("--ffmpeg-path", help="Path to FFmpeg executable")
    parser.add_argument("--embedding-model", default="sentence-transformers/all-MiniLM-L6-v2", help="Embedding model name")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--stages", nargs="+", choices=["ingest", "index", "search", "timeline", "render"],
                       default=["ingest", "index", "search", "timeline", "render"],
                       help="Stages to run (default: all)")
    parser.add_argument("--skip-render", action="store_true", help="Skip render stage (only generate timeline.json)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    args = parser.parse_args()
    
    # Setup logging
    log_file = None
    if args.project_root:
        log_file = args.project_root / "projects" / args.project_id / "logs" / "pipeline.log"
    setup_logging(log_file=log_file, level=getattr(__import__("logging"), args.log_level))
    
    # Determine stages to run
    stages_to_run = args.stages
    if args.skip_render and "render" in stages_to_run:
        stages_to_run = [s for s in stages_to_run if s != "render"]
    
    # Initialize stages
    stages = {
        "ingest": IngestStage(project_root=args.project_root),
        "index": IndexStage(project_root=args.project_root, embedding_model=args.embedding_model),
        "search": SearchStage(project_root=args.project_root, embedding_model=args.embedding_model),
        "timeline": TimelineStage(project_root=args.project_root),
        "render": RenderStage(project_root=args.project_root, ffmpeg_path=args.ffmpeg_path)
    }
    
    # Run pipeline
    print(f"Running pipeline for project {args.project_id}...")
    print(f"Stages: {', '.join(stages_to_run)}")
    
    for stage_name in stages_to_run:
        stage = stages[stage_name]
        try:
            print(f"\n{'='*60}")
            print(f"Running {stage_name} stage...")
            print(f"{'='*60}")
            
            result = stage.run(args.project_id)
            output_path = stage.save_output(args.project_id, result)
            
            print(f"✓ {stage_name} completed successfully")
            print(f"  Output: {output_path}")
        except Exception as e:
            print(f"\n✗ {stage_name} failed: {e}", file=sys.stderr)
            sys.exit(1)
    
    print(f"\n{'='*60}")
    print("Pipeline completed successfully!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

