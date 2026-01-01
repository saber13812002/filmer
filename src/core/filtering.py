"""Filtering logic for spoiler avoidance, scene weighting, etc."""

from typing import List, Optional
from src.core.matching import Match
from src.contracts.models.timeline import SpoilerRisk


def filter_by_spoiler_risk(
    matches: List[Match],
    spoiler_risks: dict[str, SpoilerRisk],
    risk_threshold: float = 0.3
) -> List[Match]:
    """Filter matches by spoiler risk threshold
    
    Args:
        matches: List of matches to filter
        spoiler_risks: Dictionary mapping segment_id to SpoilerRisk
        risk_threshold: Maximum allowed spoiler risk (0-1)
        
    Returns:
        Filtered list of matches
    """
    filtered = []
    for match in matches:
        risk = spoiler_risks.get(match.segment_id)
        if risk is None or risk.risk <= risk_threshold:
            filtered.append(match)
    return filtered


def apply_scene_weights(
    matches: List[Match],
    scene_weights: dict[str, float]
) -> List[Match]:
    """Apply scene weights to matches
    
    Args:
        matches: List of matches
        scene_weights: Dictionary mapping segment_id to weight
        
    Returns:
        List of matches with weights applied (stored in match metadata)
    """
    for match in matches:
        weight = scene_weights.get(match.segment_id, 1.0)
        # Store weight in match (would need to extend Match dataclass)
        # For now, this is a placeholder for future implementation
    return matches


def filter_by_priority(
    matches: List[Match],
    min_priority: int = 1
) -> List[Match]:
    """Filter matches by priority (if priority is set)
    
    Args:
        matches: List of matches
        min_priority: Minimum priority level
        
    Returns:
        Filtered list of matches
    """
    # Priority filtering would require Match to have priority field
    # This is a placeholder for future implementation
    return matches


def merge_nearby_segments(
    matches: List[Match],
    merge_threshold: float = 5.0
) -> List[Match]:
    """Merge segments that are very close together
    
    Args:
        matches: List of matches
        merge_threshold: Maximum gap in seconds to merge
        
    Returns:
        List of matches with nearby segments merged
    """
    if not matches:
        return []
    
    sorted_matches = sorted(matches, key=lambda m: m.start_time)
    merged = [sorted_matches[0]]
    
    for match in sorted_matches[1:]:
        last_match = merged[-1]
        gap = match.start_time - last_match.end_time
        
        if gap <= merge_threshold:
            # Merge: extend the last match
            merged[-1] = Match(
                segment_id=last_match.segment_id,
                start_time=last_match.start_time,
                end_time=match.end_time,
                similarity_score=max(last_match.similarity_score, match.similarity_score),
                narration_text=f"{last_match.narration_text} {match.narration_text}"
            )
        else:
            merged.append(match)
    
    return merged

