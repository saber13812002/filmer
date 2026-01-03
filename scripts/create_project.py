"""CLI tool for creating new projects with all required fields"""

import argparse
import sys
import json
from pathlib import Path
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.contracts.models.project import ProjectConfig, ProjectOptions, EmbeddingConfig
from src.stages.base import BaseStage


def main():
    parser = argparse.ArgumentParser(
        description="Create a new project with movie metadata and SRT files"
    )
    parser.add_argument("--project-id", required=True, help="Project identifier (IMDb ID or custom)")
    parser.add_argument("--movie-duration", type=float, required=True, help="Movie duration in seconds")
    parser.add_argument("--movie-language", required=True, help="Original language code (e.g., 'en', 'fa')")
    parser.add_argument("--movie-srt", required=True, help="Path to movie SRT file")
    parser.add_argument("--narration-srt", action="append", required=True, help="Path to narration SRT file (can be specified multiple times)")
    parser.add_argument("--movie-video", help="Path to movie video file (optional)")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--similarity-threshold", type=float, default=0.75, help="Similarity threshold (default: 0.75)")
    parser.add_argument("--copyright-min-gap", type=float, default=30.0, help="Minimum time gap for copyright compliance (default: 30.0 seconds)")
    parser.add_argument("--embedding-model", default="sentence-transformers/all-MiniLM-L6-v2", help="Embedding model name")
    
    args = parser.parse_args()
    
    # Validate files exist
    movie_srt_path = Path(args.movie_srt)
    if not movie_srt_path.exists():
        print(f"Error: Movie SRT file not found: {movie_srt_path}", file=sys.stderr)
        sys.exit(1)
    
    for narration_srt in args.narration_srt:
        narration_path = Path(narration_srt)
        if not narration_path.exists():
            print(f"Error: Narration SRT file not found: {narration_path}", file=sys.stderr)
            sys.exit(1)
    
    if args.movie_video:
        video_path = Path(args.movie_video)
        if not video_path.exists():
            print(f"Error: Movie video file not found: {video_path}", file=sys.stderr)
            sys.exit(1)
    
    # Create project structure
    stage = BaseStage(project_root=args.project_root)
    stage.ensure_project_structure(args.project_id)
    
    # Copy files to project data directory
    data_path = stage.get_data_path(args.project_id)
    
    import shutil
    # Copy movie SRT
    dest_movie_srt = data_path / "movie.srt"
    shutil.copy2(movie_srt_path, dest_movie_srt)
    print(f"[OK] Copied movie SRT: {dest_movie_srt}")
    
    # Copy narration SRT files
    narration_paths_in_project = []
    for i, narration_srt in enumerate(args.narration_srt):
        source_path = Path(narration_srt)
        dest_name = f"narration_{i+1}.srt" if len(args.narration_srt) > 1 else "narration.srt"
        dest_path = data_path / dest_name
        shutil.copy2(source_path, dest_path)
        narration_paths_in_project.append(str(dest_path))
        print(f"[OK] Copied narration SRT {i+1}: {dest_path}")
    
    # Copy movie video if provided
    if args.movie_video:
        video_path = Path(args.movie_video)
        dest_video = data_path / video_path.name
        shutil.copy2(video_path, dest_video)
        print(f"[OK] Copied movie video: {dest_video}")
    
    # Create project config
    project_config = ProjectConfig(
        movie_id=args.project_id,
        movie_duration=args.movie_duration,
        movie_language=args.movie_language,
        movie_video_path=str(data_path / Path(args.movie_video).name) if args.movie_video else None,
        narration_srt_files=narration_paths_in_project,
        options=ProjectOptions(
            similarity_threshold=args.similarity_threshold,
            min_segment_length=3.0,
            preset="standard"
        ),
        embedding=EmbeddingConfig(
            model=args.embedding_model
        )
    )
    
    # Save project config
    config_path = stage.get_configs_path(args.project_id) / "project.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(project_config.model_dump_json(indent=2))
    
    print(f"\n[OK] Project created successfully!")
    print(f"  Project ID: {args.project_id}")
    print(f"  Movie Duration: {args.movie_duration}s")
    print(f"  Language: {args.movie_language}")
    print(f"  Narration Files: {len(args.narration_srt)}")
    print(f"  Config: {config_path}")
    print(f"\nNext steps:")
    print(f"  1. Run ingest: python scripts/run_stage.py ingest --project-id {args.project_id}")
    print(f"  2. Run index: python scripts/run_stage.py index --project-id {args.project_id}")
    print(f"  3. Run search: python scripts/run_stage.py search --project-id {args.project_id}")
    print(f"  4. Run timeline: python scripts/run_stage.py timeline --project-id {args.project_id}")


if __name__ == "__main__":
    main()

