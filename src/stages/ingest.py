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
        movie_video = find_file_in_directory(data_path, "movie.*")
        
        # Filter video file (exclude .srt)
        if movie_video and movie_video.suffix == '.srt':
            movie_video = None
        
        # Find multiple narration SRT files
        narration_srt_files = []
        narration_audio_files = []
        
        # Look for narration*.srt files
        if data_path.exists():
            for file in data_path.glob("narration*.srt"):
                narration_srt_files.append(str(file))
        
        # Look for narration audio files (exclude .srt)
        if data_path.exists():
            for file in data_path.glob("narration.*"):
                if file.suffix != '.srt':
                    narration_audio_files.append(str(file))
        
        # Validate required files
        if not movie_srt:
            raise StageExecutionError(f"Movie SRT file not found in {data_path}")
        if not narration_srt_files:
            raise StageExecutionError(f"No narration SRT files found in {data_path}")
        
        # Load project config to check for narration files list
        project_config = self.load_input(project_id)
        if project_config and project_config.get("narration_srt_files"):
            # Validate files from config exist
            config_files = project_config["narration_srt_files"]
            for file_path in config_files:
                if not Path(file_path).exists():
                    raise StageExecutionError(f"Narration SRT file not found: {file_path}")
            narration_srt_files = config_files
        
        output = IngestOutput(
            movie_srt_path=str(movie_srt) if movie_srt else None,
            narration_srt_path=narration_srt_files[0] if narration_srt_files else None,  # Keep for backward compatibility
            movie_video_path=str(movie_video) if movie_video else None,
            narration_audio_path=narration_audio_files[0] if narration_audio_files else None,  # Keep for backward compatibility
            validated=True
        )
        
        # Add multiple narration files to output
        output_dict = output.model_dump()
        output_dict["narration_srt_files"] = narration_srt_files
        output_dict["narration_audio_files"] = narration_audio_files
        
        return output_dict
    
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

