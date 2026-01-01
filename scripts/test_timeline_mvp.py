"""Simple test script for TimelineStage MVP"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stages.timeline_mvp import TimelineStageMVP


def main():
    """Test TimelineStage MVP with a sample project"""
    project_id = "test_project"
    
    print("=" * 60)
    print("Testing TimelineStage MVP")
    print("=" * 60)
    
    # Initialize stage
    stage = TimelineStageMVP()
    
    # Ensure project structure
    stage.ensure_project_structure(project_id)
    
    # Create sample project config
    config_path = stage.get_configs_path(project_id) / "project.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    import json
    sample_config = {
        "movie_id": "tt0133093",
        "options": {
            "similarity_threshold": 0.75,
            "min_segment_length": 3.0,
            "preset": "standard"
        }
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, indent=2)
    
    print(f"\n✓ Project config created: {config_path}")
    
    # Run timeline stage
    try:
        print(f"\nRunning timeline stage for project: {project_id}")
        result = stage.run(project_id)
        
        timeline_path = stage.get_outputs_path(project_id) / "timeline.json"
        
        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print(f"Timeline JSON generated: {timeline_path}")
        print(f"\nYou can now test with legacy cutter:")
        print(f"  python legacy/cut_video.py")
        print(f"\n(Note: Make sure timeline.json is in the current directory)")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

