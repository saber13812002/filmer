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
        
        # Load narration SRT files to build intervals
        from src.utils.srt_parser import parse_srt_file
        narration_srt_files = ingest_data.get("narration_srt_files", [])
        if not narration_srt_files:
            narration_srt_path = ingest_data.get("narration_srt_path")
            if narration_srt_path:
                narration_srt_files = [narration_srt_path]
        
        # Parse all narration entries
        all_narration_entries = []
        for narration_file in narration_srt_files:
            entries = parse_srt_file(Path(narration_file))
            all_narration_entries.extend(entries)
        
        # Sort narration entries by time
        all_narration_entries.sort(key=lambda e: e.start_time)
        
        # Organize matches by narration entry index
        from src.core.matching import Match
        matches_by_narration = {}
        
        for match_data in search_output.matches:
            if isinstance(match_data, dict):
                chunk_index = match_data.get("chunk_index", 0)
                narration_time = match_data.get("narration_time", 0.0)
                
                # Find narration entry index
                entry_index = 0
                for i, entry in enumerate(all_narration_entries):
                    if entry.start_time <= narration_time <= entry.end_time:
                        entry_index = i
                        break
                
                match = Match(
                    segment_id=match_data["segment_id"],
                    start_time=match_data["start_time"],
                    end_time=match_data["end_time"],
                    similarity_score=match_data["similarity_score"],
                    narration_text=match_data.get("narration_text", ""),
                    narration_time=narration_time,
                    narration_file_id=match_data.get("narration_file_id")
                )
                
                if entry_index not in matches_by_narration:
                    matches_by_narration[entry_index] = []
                matches_by_narration[entry_index].append(match)
        
        # Sort matches by similarity score (best first)
        for entry_index in matches_by_narration:
            matches_by_narration[entry_index].sort(key=lambda m: m.similarity_score, reverse=True)
        
        # Apply similarity threshold
        similarity_threshold = 0.75
        if project_config and project_config.get("options"):
            similarity_threshold = project_config["options"].get("similarity_threshold", 0.75)
        
        for entry_index in matches_by_narration:
            matches_by_narration[entry_index] = [
                m for m in matches_by_narration[entry_index]
                if m.similarity_score >= similarity_threshold
            ]
        
        # Build timeline using interval-based approach
        input_video = ingest_data.get("movie_video_path", "films/input/movie.mp4")
        narration_audio = ingest_data.get("narration_audio_path") or ingest_data.get("narration_audio_files", [None])[0] or "films/narration/narration.m4a"
        output_video = str(self.get_outputs_path(project_id) / "final.mp4")
        
        timeline_options = None
        min_time_gap = 30.0
        if project_config and project_config.get("options"):
            opts = project_config["options"]
            timeline_options = TimelineOptions(
                spoiler_safe_mode=opts.get("spoiler_safe_mode", False),
                spoiler_risk_threshold=opts.get("spoiler_risk_threshold", 0.3),
                max_duration=opts.get("max_duration"),
                min_segment_length=opts.get("min_segment_length", 3.0),
                similarity_threshold=opts.get("similarity_threshold", 0.75)
            )
            # Copyright compliance time gap (can be configurable)
            min_time_gap = opts.get("copyright_min_gap", 30.0)
        
        from src.core.timeline_builder import build_timeline_for_narration_intervals
        
        timeline = build_timeline_for_narration_intervals(
            narration_entries=all_narration_entries,
            matches_by_narration=matches_by_narration,
            input_video_path=input_video,
            narration_audio_path=narration_audio,
            output_video_path=output_video,
            interval_seconds=4.0,  # 3-5 second intervals
            min_time_gap=min_time_gap,
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

