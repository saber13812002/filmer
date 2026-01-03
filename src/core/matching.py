"""Semantic matching algorithms"""

from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Match:
    """Represents a match between narration and movie segment"""
    segment_id: str
    start_time: float  # Movie segment start time
    end_time: float    # Movie segment end time
    similarity_score: float
    narration_text: str
    narration_time: Optional[float] = None  # Narration time (for sorting and copyright compliance)
    narration_file_id: Optional[str] = None  # Identifier for which narration file this match belongs to


def filter_by_similarity_threshold(
    matches: List[Match],
    threshold: float = 0.75
) -> List[Match]:
    """Filter matches by similarity threshold
    
    Args:
        matches: List of matches to filter
        threshold: Minimum similarity score (0-1)
        
    Returns:
        Filtered list of matches
    """
    return [m for m in matches if m.similarity_score >= threshold]


def detect_overlaps(matches: List[Match], overlap_threshold: float = 0.5) -> List[Tuple[Match, Match]]:
    """Detect overlapping segments
    
    Args:
        matches: List of matches
        overlap_threshold: Minimum overlap ratio to consider (0-1)
        
    Returns:
        List of tuples containing overlapping matches
    """
    overlaps = []
    sorted_matches = sorted(matches, key=lambda m: m.start_time)
    
    for i, match1 in enumerate(sorted_matches):
        for match2 in sorted_matches[i+1:]:
            # Calculate overlap
            overlap_start = max(match1.start_time, match2.start_time)
            overlap_end = min(match1.end_time, match2.end_time)
            
            if overlap_start < overlap_end:
                overlap_duration = overlap_end - overlap_start
                match1_duration = match1.end_time - match1.start_time
                match2_duration = match2.end_time - match2.start_time
                
                # Calculate overlap ratio
                overlap_ratio = overlap_duration / min(match1_duration, match2_duration)
                
                if overlap_ratio >= overlap_threshold:
                    overlaps.append((match1, match2))
    
    return overlaps


def remove_severe_overlaps(matches: List[Match], overlap_threshold: float = 0.7) -> List[Match]:
    """Remove matches with severe overlaps, keeping higher-scored ones
    
    Args:
        matches: List of matches
        overlap_threshold: Overlap ratio threshold for removal
        
    Returns:
        List of matches with severe overlaps removed
    """
    overlaps = detect_overlaps(matches, overlap_threshold)
    to_remove_ids = set()
    
    for match1, match2 in overlaps:
        # Keep the match with higher similarity score
        if match1.similarity_score >= match2.similarity_score:
            to_remove_ids.add(match2.segment_id)
        else:
            to_remove_ids.add(match1.segment_id)
    
    return [m for m in matches if m.segment_id not in to_remove_ids]

