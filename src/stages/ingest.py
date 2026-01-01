"""Stage 1: File ingestion and validation"""

from pathlib import Path
from typing import Dict, Any, Optional
import json

from src.stages.base import BaseStage, StageExecutionError
from src.contracts.models.stage_outputs import IngestOutput
from src.contracts.models.project import ProjectConfig
from src.utils.file_utils import find_file_in_directory, ensure_directory


class IngestStage(BaseStage):
    """Ingest stage: validates and locates project files"""
    
    def run(self, project_id: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute ingest stage"""
        self.ensure_project_structure(project_id)
        data_path = self.get_data_path(project_id)
        
        # Find required files
        movie_srt = find_file_in_directory(data_path, "movie.srt")
        narration_srt = find_file_in_directory(data_path, "narration.srt")
        movie_video = find_file_in_directory(data_path, "movie.*")
        narration_audio = find_file_in_directory(data_path, "narration.*")
        
        # Filter video file (exclude .srt)
        if movie_video and movie_video.suffix == '.srt':
            movie_video = None
        
        # Filter audio file (exclude .srt)
        if narration_audio and narration_audio.suffix == '.srt':
            narration_audio = None
        
        # Validate required files
        if not movie_srt:
            raise StageExecutionError(f"Movie SRT file not found in {data_path}")
        if not narration_srt:
            raise StageExecutionError(f"Narration SRT file not found in {data_path}")
        
        output = IngestOutput(
            movie_srt_path=str(movie_srt) if movie_srt else None,
            narration_srt_path=str(narration_srt) if narration_srt else None,
            movie_video_path=str(movie_video) if movie_video else None,
            narration_audio_path=str(narration_audio) if narration_audio else None,
            validated=True
        )
        
        return output.model_dump()
    
    def load_input(self, project_id: str) -> Dict[str, Any]:
        """Load project configuration"""
        config_path = self.get_configs_path(project_id) / "project.json"
        
        if not config_path.exists():
            return {}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_output(self, project_id: str, data: Dict[str, Any]) -> Path:
        """Save ingest output"""
        output_path = self.get_outputs_path(project_id) / "ingest_output.json"
        ensure_directory(output_path.parent)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return output_path
    
    def validate(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Validate ingest configuration"""
        return True  # No specific validation needed

