"""Stage 4: Timeline generation"""

from pathlib import Path
from typing import Dict, Any, Optional
import json

from src.stages.base import BaseStage, StageExecutionError
from src.contracts.models.timeline import Timeline, TimelineOptions
from src.contracts.models.stage_outputs import SearchOutput, SearchMatch
from src.core.matching import filter_by_similarity_threshold, remove_severe_overlaps
from src.core.filtering import merge_nearby_segments
from src.core.timeline_builder import build_timeline, save_timeline_json


class TimelineStage(BaseStage):
    """Timeline stage: generates timeline JSON from search matches"""
    
    def run(self, project_id: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute timeline generation stage"""
        # Load search output
        search_data = self.load_input(project_id)
        search_output = SearchOutput(**search_data)
        
        # Load ingest output for file paths
        ingest_output_path = self.get_outputs_path(project_id) / "ingest_output.json"
        with open(ingest_output_path, 'r', encoding='utf-8') as f:
            ingest_data = json.load(f)
        
        # Load project config for options
        project_config_path = self.get_configs_path(project_id) / "project.json"
        project_config = None
        if project_config_path.exists():
            with open(project_config_path, 'r', encoding='utf-8') as f:
                project_config = json.load(f)
        
        # Convert search matches to Match objects
        from src.core.matching import Match
        matches = [
            Match(
                segment_id=match.segment_id if hasattr(match, 'segment_id') else match["segment_id"],
                start_time=match.start_time if hasattr(match, 'start_time') else match["start_time"],
                end_time=match.end_time if hasattr(match, 'end_time') else match["end_time"],
                similarity_score=match.similarity_score if hasattr(match, 'similarity_score') else match["similarity_score"],
                narration_text=getattr(match, 'narration_text', None) or match.get("narration_text", "") if isinstance(match, dict) else (match.narration_text if hasattr(match, 'narration_text') else "")
            )
            for match in search_output.matches
        ]
        
        # Apply filtering
        similarity_threshold = 0.75
        if project_config and project_config.get("options"):
            similarity_threshold = project_config["options"].get("similarity_threshold", 0.75)
        
        matches = filter_by_similarity_threshold(matches, similarity_threshold)
        matches = remove_severe_overlaps(matches, overlap_threshold=0.7)
        matches = merge_nearby_segments(matches, merge_threshold=5.0)
        
        # Build timeline
        input_video = ingest_data.get("movie_video_path", "films/input/movie.mp4")
        narration_audio = ingest_data.get("narration_audio_path", "films/narration/narration.m4a")
        output_video = str(self.get_outputs_path(project_id) / "final.mp4")
        
        timeline_options = None
        if project_config and project_config.get("options"):
            opts = project_config["options"]
            timeline_options = TimelineOptions(
                spoiler_safe_mode=opts.get("spoiler_safe_mode", False),
                spoiler_risk_threshold=opts.get("spoiler_risk_threshold", 0.3),
                max_duration=opts.get("max_duration"),
                min_segment_length=opts.get("min_segment_length", 3.0),
                similarity_threshold=opts.get("similarity_threshold", 0.75)
            )
        
        timeline = build_timeline(
            matches=matches,
            input_video_path=input_video,
            narration_audio_path=narration_audio,
            output_video_path=output_video,
            project_id=project_id,
            movie_id=project_config.get("movie_id") if project_config else None,
            options=timeline_options
        )
        
        # Save timeline JSON
        timeline_path = self.get_outputs_path(project_id) / "timeline.json"
        save_timeline_json(timeline, timeline_path)
        
        return timeline.model_dump()
    
    def load_input(self, project_id: str) -> Dict[str, Any]:
        """Load search output"""
        search_output_path = self.get_outputs_path(project_id) / "search_output.json"
        
        if not search_output_path.exists():
            raise StageExecutionError(f"Search output not found: {search_output_path}")
        
        with open(search_output_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_output(self, project_id: str, data: Dict[str, Any]) -> Path:
        """Save timeline output"""
        output_path = self.get_outputs_path(project_id) / "outputs" / "timeline.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use Pydantic's JSON serialization which handles datetime
        from src.contracts.models.timeline import Timeline
        timeline = Timeline(**data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(timeline.model_dump_json(indent=2, exclude_none=True))
        
        return output_path
    
    def validate(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Validate timeline configuration"""
        return True

