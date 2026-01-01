"""Utility script to migrate legacy projects to new structure"""

import argparse
import json
import shutil
from pathlib import Path


def migrate_timeline_json(timeline_path: Path, project_id: str, project_root: Path):
    """Migrate legacy timeline.json to new project structure"""
    project_path = project_root / "projects" / project_id
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Read legacy timeline
    with open(timeline_path, 'r', encoding='utf-8') as f:
        timeline_data = json.load(f)
    
    # Copy timeline to outputs
    outputs_path = project_path / "outputs"
    outputs_path.mkdir(parents=True, exist_ok=True)
    
    new_timeline_path = outputs_path / "timeline.json"
    with open(new_timeline_path, 'w', encoding='utf-8') as f:
        json.dump(timeline_data, f, indent=2)
    
    print(f"Migrated timeline.json to {new_timeline_path}")


def main():
    parser = argparse.ArgumentParser(description="Migrate legacy projects")
    parser.add_argument("--project-id", required=True, help="Project identifier")
    parser.add_argument("--timeline-json", type=Path, help="Path to legacy timeline.json")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root directory")
    
    args = parser.parse_args()
    
    if args.timeline_json:
        migrate_timeline_json(args.timeline_json, args.project_id, args.project_root)
    else:
        print("No migration actions specified")


if __name__ == "__main__":
    main()

