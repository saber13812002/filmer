"""Filtering logic for spoiler avoidance, scene weighting, etc."""

from typing import List, Optional, Dict
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


def prevent_consecutive_segments(
    matches: List[Match],
    min_time_gap: float = 30.0,
    alternative_matches: Optional[Dict[str, List[Match]]] = None
) -> List[Match]:
    """Prevent consecutive segments from same time period (copyright compliance)
    
    Ensures segments are distributed across different parts of the movie
    to comply with copyright requirements. If a segment is too close to the
    previous one in movie time, it tries to use an alternative match.
    
    Args:
        matches: List of matches sorted by narration time
        min_time_gap: Minimum time gap between consecutive segments in movie time (seconds)
        alternative_matches: Optional dict mapping segment_id to list of alternative matches
        
    Returns:
        Filtered list with distributed segments (copyright compliant)
    """
    if not matches:
        return []
    
    # Sort by narration time (assuming matches have narration_time attribute or we use start_time)
    sorted_matches = sorted(matches, key=lambda m: getattr(m, 'narration_time', m.start_time))
    
    filtered = []
    last_movie_time = None
    
    for match in sorted_matches:
        # Calculate center time of current match in movie
        current_movie_center = (match.start_time + match.end_time) / 2.0
        
        # Check if this match is too close to previous match in movie time
        if last_movie_time is not None:
            time_gap = abs(current_movie_center - last_movie_time)
            
            if time_gap < min_time_gap:
                # Try to find alternative match with sufficient time gap
                if alternative_matches and match.segment_id in alternative_matches:
                    alternatives = alternative_matches[match.segment_id]
                    found_alternative = False
                    
                    for alt_match in alternatives:
                        alt_center = (alt_match.start_time + alt_match.end_time) / 2.0
                        alt_gap = abs(alt_center - last_movie_time)
                        
                        if alt_gap >= min_time_gap:
                            # Use alternative match
                            filtered.append(alt_match)
                            last_movie_time = alt_center
                            found_alternative = True
                            break
                    
                    if not found_alternative:
                        # Skip this match if no suitable alternative
                        continue
                else:
                    # Skip this match if no alternatives available
                    continue
            else:
                # Time gap is sufficient, use this match
                filtered.append(match)
                last_movie_time = current_movie_center
        else:
            # First match, always include
            filtered.append(match)
            last_movie_time = current_movie_center
    
    return filtered

