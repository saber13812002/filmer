"""Timeline JSON generation from matched segments"""

import json
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from src.core.matching import Match
from src.contracts.models.timeline import (
    Timeline,
    Segment,
    TimelineMetadata,
    TimelineOptions
)


def build_timeline(
    matches: List[Match],
    input_video_path: str,
    narration_audio_path: str,
    output_video_path: str,
    project_id: Optional[str] = None,
    movie_id: Optional[str] = None,
    options: Optional[TimelineOptions] = None
) -> Timeline:
    """Build Timeline JSON from matched segments
    
    Args:
        matches: List of matched segments
        input_video_path: Path to input video file
        narration_audio_path: Path to narration audio file
        output_video_path: Path to output video file
        project_id: Optional project identifier
        movie_id: Optional movie identifier
        options: Optional timeline options
        
    Returns:
        Timeline object ready for JSON serialization
    """
    segments = []
    
    for match in matches:
        segment = Segment(
            start=match.start_time,
            end=match.end_time,
            score=match.similarity_score
        )
        segments.append(segment)
    
    metadata = None
    if project_id or movie_id or options:
        metadata = TimelineMetadata(
            project_id=project_id,
            movie_id=movie_id,
            generated_at=datetime.now(),
            version="1.0",
            options=options
        )
    
    timeline = Timeline(
        input=input_video_path,
        narration=narration_audio_path,
        output=output_video_path,
        segments=segments,
        metadata=metadata
    )
    
    return timeline


def save_timeline_json(timeline: Timeline, output_path: Path, minimal: bool = False) -> None:
    """Save timeline to JSON file
    
    Args:
        timeline: Timeline object
        output_path: Path to save JSON file
        minimal: If True, only include essential fields (backward compatible)
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if minimal:
        # Create minimal version for legacy compatibility
        minimal_data = {
            "input": timeline.input,
            "narration": timeline.narration,
            "output": timeline.output,
            "segments": [
                {
                    "start": seg.start,
                    "end": seg.end
                }
                for seg in timeline.segments
            ]
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(minimal_data, f, indent=2)
    else:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(timeline.model_dump_json(indent=2, exclude_none=True))

