"""Test Timeline stage integration with mock search output"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stages.timeline import TimelineStage

def main():
    project_id = "test_project"
    
    print("Testing Timeline Stage Integration...")
    print("=" * 60)
    
    stage = TimelineStage()
    
    try:
        result = stage.run(project_id)
        output_path = stage.save_output(project_id, result)
        
        print(f"\n[OK] Timeline stage completed successfully!")
        print(f"  Output: {output_path}")
        print(f"  Segments: {len(result['segments'])}")
        print(f"  Input: {result['input']}")
        print(f"  Narration: {result['narration']}")
        print(f"  Output: {result['output']}")
        
        return True
    except Exception as e:
        print(f"\n[ERROR] Timeline stage failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

