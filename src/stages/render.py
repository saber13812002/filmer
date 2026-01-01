"""Stage 5: Video rendering"""

from pathlib import Path
from typing import Dict, Any, Optional
import json

from src.stages.base import BaseStage, StageExecutionError
from src.contracts.models.timeline import Timeline
from src.adapters.ffmpeg_adapter import FFmpegAdapter


class RenderStage(BaseStage):
    """Render stage: renders final video using FFmpeg"""
    
    def __init__(self, project_root: Optional[Path] = None, ffmpeg_path: Optional[str] = None):
        super().__init__(project_root)
        self.ffmpeg_path = ffmpeg_path
    
    def run(self, project_id: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute render stage"""
        # Load timeline
        timeline_data = self.load_input(project_id)
        timeline = Timeline(**timeline_data)
        
        # Initialize FFmpeg adapter
        ffmpeg_adapter = FFmpegAdapter(ffmpeg_path=self.ffmpeg_path)
        
        # Check FFmpeg availability
        if not ffmpeg_adapter.check_ffmpeg_available():
            raise StageExecutionError("FFmpeg is not available. Please install FFmpeg.")
        
        # Render video
        try:
            ffmpeg_adapter.cut_and_concat_video(timeline, overwrite=True)
        except Exception as e:
            raise StageExecutionError(f"FFmpeg rendering failed: {str(e)}")
        
        return {
            "status": "success",
            "output_file": timeline.output,
            "segments_processed": len(timeline.segments)
        }
    
    def load_input(self, project_id: str) -> Dict[str, Any]:
        """Load timeline JSON"""
        timeline_path = self.get_outputs_path(project_id) / "timeline.json"
        
        if not timeline_path.exists():
            raise StageExecutionError(f"Timeline not found: {timeline_path}")
        
        with open(timeline_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_output(self, project_id: str, data: Dict[str, Any]) -> Path:
        """Save render output"""
        output_path = self.get_outputs_path(project_id) / "outputs" / "render_output.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return output_path
    
    def validate(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Validate render configuration"""
        return True

