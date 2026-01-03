"""Timeline JSON generation from matched segments"""

import json
from typing import List, Optional, Dict
from datetime import datetime
from pathlib import Path

from src.core.matching import Match
from src.utils.srt_parser import SRTEntry
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


def build_timeline_for_narration_intervals(
    narration_entries: List[SRTEntry],
    matches_by_narration: Dict[int, List[Match]],
    input_video_path: str,
    narration_audio_path: str,
    output_video_path: str,
    interval_seconds: float = 4.0,
    min_time_gap: float = 30.0,
    project_id: Optional[str] = None,
    movie_id: Optional[str] = None,
    options: Optional[TimelineOptions] = None
) -> Timeline:
    """Build timeline with segments for every 3-5 seconds of narration
    
    Creates segments that align with narration timing while ensuring
    movie segments are distributed (copyright compliance).
    
    Args:
        narration_entries: List of narration SRT entries
        matches_by_narration: Dictionary mapping narration entry index to list of matches (sorted by score)
        input_video_path: Path to input video file
        narration_audio_path: Path to narration audio file
        output_video_path: Path to output video file
        interval_seconds: Interval for creating segments (default: 4.0 seconds)
        min_time_gap: Minimum time gap between consecutive segments in movie time (default: 30.0)
        project_id: Optional project identifier
        movie_id: Optional movie identifier
        options: Optional timeline options
        
    Returns:
        Timeline object ready for JSON serialization
    """
    from src.core.filtering import prevent_consecutive_segments
    
    segments = []
    selected_matches = []
    last_movie_time = None
    
    # Process narration in intervals
    current_time = 0.0
    narration_index = 0
    
    while current_time < narration_entries[-1].end_time if narration_entries else 0:
        # Find narration entry that covers current time
        current_entry = None
        for entry in narration_entries:
            if entry.start_time <= current_time <= entry.end_time:
                current_entry = entry
                break
        
        if current_entry:
            # Get matches for this narration entry
            entry_index = narration_entries.index(current_entry)
            matches = matches_by_narration.get(entry_index, [])
            
            if matches:
                # Try to select best match that complies with copyright
                selected = None
                
                for match in matches:
                    match_center = (match.start_time + match.end_time) / 2.0
                    
                    # Check copyright compliance
                    if last_movie_time is None:
                        # First match, always use best
                        selected = match
                        break
                    else:
                        time_gap = abs(match_center - last_movie_time)
                        if time_gap >= min_time_gap:
                            selected = match
                            break
                
                # If no compliant match found, use best match anyway (log warning)
                if selected is None and matches:
                    selected = matches[0]  # Use best match
                
                if selected:
                    segment = Segment(
                        start=selected.start_time,
                        end=selected.end_time,
                        score=selected.similarity_score
                    )
                    segments.append(segment)
                    selected_matches.append(selected)
                    last_movie_time = (selected.start_time + selected.end_time) / 2.0
        
        # Move to next interval
        current_time += interval_seconds
        narration_index += 1
    
    # Apply copyright compliance filter as final check
    if selected_matches:
        from src.core.filtering import prevent_consecutive_segments
        # Build alternative matches dict for fallback
        alternative_matches = {}
        for i, match in enumerate(selected_matches):
            entry_index = None
            for idx, entry in enumerate(narration_entries):
                if hasattr(match, 'narration_time') and entry.start_time <= match.narration_time <= entry.end_time:
                    entry_index = idx
                    break
            
            if entry_index is not None:
                alt_matches = matches_by_narration.get(entry_index, [])
                if len(alt_matches) > 1:
                    alternative_matches[match.segment_id] = alt_matches[1:]  # Skip first (best)
        
        filtered_matches = prevent_consecutive_segments(
            selected_matches,
            min_time_gap=min_time_gap,
            alternative_matches=alternative_matches if alternative_matches else None
        )
        
        # Rebuild segments from filtered matches
        segments = [
            Segment(
                start=m.start_time,
                end=m.end_time,
                score=m.similarity_score
            )
            for m in filtered_matches
        ]
    
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

