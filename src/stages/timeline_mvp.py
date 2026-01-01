"""Stage 4: Timeline generation (MVP version - standalone, no dependencies)"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import json
from datetime import datetime

from src.stages.base import BaseStage, StageExecutionError
from src.contracts.models.timeline import Timeline, Segment, TimelineMetadata, TimelineOptions
from src.core.timeline_builder import save_timeline_json


class TimelineStageMVP(BaseStage):
    """Timeline stage MVP: generates timeline JSON from mock data or config
    
    This MVP version can work standalone without requiring search stage output.
    It's designed to prove the architecture and contract compatibility.
    """
    
    def run(self, project_id: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute timeline generation stage
        
        Can work with:
        1. Mock segments (if no search output exists)
        2. Config-based segments
        3. Search output (if available)
        """
        self.ensure_project_structure(project_id)
        
        # Try to load search output first
        search_output_path = self.get_outputs_path(project_id) / "search_output.json"
        segments_data = None
        
        if search_output_path.exists():
            # Use real search output
            segments_data = self._load_from_search_output(project_id)
        elif config and "segments" in config:
            # Use segments from config
            segments_data = config["segments"]
        else:
            # Generate mock segments for testing
            segments_data = self._generate_mock_segments()
        
        # Load project config for file paths and options
        project_config = self._load_project_config(project_id)
        
        # Get file paths
        input_video = self._get_input_video_path(project_id, project_config)
        narration_audio = self._get_narration_audio_path(project_id, project_config)
        output_video = str(self.get_outputs_path(project_id) / "final.mp4")
        
        # Build segments
        segments = []
        for seg_data in segments_data:
            if isinstance(seg_data, dict):
                segment = Segment(
                    start=seg_data["start"],
                    end=seg_data["end"],
                    score=seg_data.get("score"),
                    priority=seg_data.get("priority")
                )
            else:
                # Simple tuple/list format: (start, end)
                segment = Segment(
                    start=seg_data[0] if isinstance(seg_data, (list, tuple)) else seg_data.get("start"),
                    end=seg_data[1] if isinstance(seg_data, (list, tuple)) else seg_data.get("end")
                )
            segments.append(segment)
        
        # Build timeline options
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
        
        # Build timeline
        timeline = Timeline(
            input=input_video,
            narration=narration_audio,
            output=output_video,
            segments=segments,
            metadata=TimelineMetadata(
                project_id=project_id,
                movie_id=project_config.get("movie_id") if project_config else None,
                generated_at=datetime.now(),
                version="1.0",
                options=timeline_options
            )
        )
        
        # Save timeline JSON (full version in outputs/)
        timeline_path = self.get_outputs_path(project_id) / "timeline.json"
        save_timeline_json(timeline, timeline_path, minimal=False)
        
        # Also save a minimal copy in project root for easy access by legacy cutter
        root_timeline_path = self.get_project_path(project_id).parent.parent / "timeline.json"
        if self.project_root:
            root_timeline_path = self.project_root / "timeline.json"
        else:
            root_timeline_path = Path("timeline.json")
        
        save_timeline_json(timeline, root_timeline_path, minimal=True)
        print(f"[OK] Timeline also saved to root (minimal format): {root_timeline_path}")
        
        print(f"[OK] Timeline generated: {timeline_path}")
        print(f"  Segments: {len(segments)}")
        print(f"  Output: {output_video}")
        
        return timeline.model_dump()
    
    def _load_from_search_output(self, project_id: str) -> List[Dict[str, Any]]:
        """Load segments from search output"""
        from src.contracts.models.stage_outputs import SearchOutput
        
        search_output_path = self.get_outputs_path(project_id) / "search_output.json"
        with open(search_output_path, 'r', encoding='utf-8') as f:
            search_data = json.load(f)
        
        search_output = SearchOutput(**search_data)
        return [
            {
                "start": match["start_time"],
                "end": match["end_time"],
                "score": match["similarity_score"]
            }
            for match in search_output.matches
        ]
    
    def _load_project_config(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load project configuration"""
        config_path = self.get_configs_path(project_id) / "project.json"
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def _get_input_video_path(self, project_id: str, project_config: Optional[Dict[str, Any]]) -> str:
        """Get input video path"""
        # Try ingest output first
        ingest_output_path = self.get_outputs_path(project_id) / "ingest_output.json"
        if ingest_output_path.exists():
            with open(ingest_output_path, 'r', encoding='utf-8') as f:
                ingest_data = json.load(f)
                if ingest_data.get("movie_video_path"):
                    return ingest_data["movie_video_path"]
        
        # Try data directory
        data_path = self.get_data_path(project_id)
        video_files = list(data_path.glob("movie.*"))
        video_files = [f for f in video_files if f.suffix != '.srt']
        if video_files:
            return str(video_files[0])
        
        # Default fallback
        return "films/input/movie.mp4"
    
    def _get_narration_audio_path(self, project_id: str, project_config: Optional[Dict[str, Any]]) -> str:
        """Get narration audio path"""
        # Try ingest output first
        ingest_output_path = self.get_outputs_path(project_id) / "ingest_output.json"
        if ingest_output_path.exists():
            with open(ingest_output_path, 'r', encoding='utf-8') as f:
                ingest_data = json.load(f)
                if ingest_data.get("narration_audio_path"):
                    return ingest_data["narration_audio_path"]
        
        # Try data directory
        data_path = self.get_data_path(project_id)
        audio_files = list(data_path.glob("narration.*"))
        audio_files = [f for f in audio_files if f.suffix != '.srt']
        if audio_files:
            return str(audio_files[0])
        
        # Default fallback
        return "films/narration/narration.m4a"
    
    def _generate_mock_segments(self) -> List[Dict[str, float]]:
        """Generate mock segments for testing"""
        return [
            {"start": 0.50, "end": 3.20},
            {"start": 15.00, "end": 18.40},
            {"start": 110.00, "end": 113.75},
            {"start": 120.00, "end": 123.75}
        ]
    
    def load_input(self, project_id: str) -> Dict[str, Any]:
        """Load input (not required for MVP, but implemented for interface)"""
        return {}
    
    def save_output(self, project_id: str, data: Dict[str, Any]) -> Path:
        """Save timeline output"""
        output_path = self.get_outputs_path(project_id) / "timeline.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return output_path
    
    def validate(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Validate timeline configuration"""
        return True

