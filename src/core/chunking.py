"""SRT chunking logic - time and word-based chunking"""

from typing import List
from src.utils.srt_parser import SRTEntry


class Chunk:
    """Represents a chunk of subtitle entries"""
    
    def __init__(self, entries: List[SRTEntry]):
        self.entries = entries
        self.start_time = entries[0].start_time if entries else 0.0
        self.end_time = entries[-1].end_time if entries else 0.0
        self.text = ' '.join(entry.text for entry in entries)
        self.word_count = sum(entry.word_count for entry in entries)
    
    @property
    def duration(self) -> float:
        """Get chunk duration in seconds"""
        return self.end_time - self.start_time


def chunk_srt_entries(
    entries: List[SRTEntry],
    min_duration: float = 10.0,
    max_duration: float = 20.0,
    min_words: int = 100,
    max_words: int = 200
) -> List[Chunk]:
    """Chunk SRT entries based on time and word constraints
    
    Priority is given to time-based constraints over word count.
    
    Args:
        entries: List of SRT entries to chunk
        min_duration: Minimum chunk duration in seconds (default: 10.0)
        max_duration: Maximum chunk duration in seconds (default: 20.0)
        min_words: Minimum word count per chunk (default: 100)
        max_words: Maximum word count per chunk (default: 200)
        
    Returns:
        List of Chunk objects
    """
    if not entries:
        return []
    
    chunks = []
    current_chunk = []
    current_duration = 0.0
    current_words = 0
    
    for entry in entries:
        entry_duration = entry.duration
        entry_words = entry.word_count
        
        # Check if adding this entry would exceed max constraints
        would_exceed_duration = (current_duration + entry_duration) > max_duration
        would_exceed_words = (current_words + entry_words) > max_words
        
        # Check if current chunk meets minimum requirements
        meets_min_duration = current_duration >= min_duration
        meets_min_words = current_words >= min_words
        
        # If we meet minimums and would exceed maximums, finalize chunk
        if (meets_min_duration or meets_min_words) and (would_exceed_duration or would_exceed_words):
            if current_chunk:
                chunks.append(Chunk(current_chunk))
                current_chunk = []
                current_duration = 0.0
                current_words = 0
        
        # Add entry to current chunk
        current_chunk.append(entry)
        current_duration += entry_duration
        current_words += entry_words
        
        # If we've reached max duration, finalize chunk
        if current_duration >= max_duration:
            chunks.append(Chunk(current_chunk))
            current_chunk = []
            current_duration = 0.0
            current_words = 0
    
    # Add remaining entries as final chunk
    if current_chunk:
        chunks.append(Chunk(current_chunk))
    
    return chunks


def chunk_srt_entries_3_sentence(entries: List[SRTEntry]) -> List[Chunk]:
    """Chunk SRT entries using 3-sentence window (prev + current + next)
    
    For each entry, creates a chunk containing:
    - Previous entry (if exists)
    - Current entry
    - Next entry (if exists)
    
    This provides better context for semantic matching.
    
    Args:
        entries: List of SRT entries to chunk
        
    Returns:
        List of Chunk objects, each containing 3 sentences (or fewer at boundaries)
    """
    if not entries:
        return []
    
    chunks = []
    
    for i, entry in enumerate(entries):
        chunk_entries = []
        
        # Add previous entry if exists
        if i > 0:
            chunk_entries.append(entries[i - 1])
        
        # Add current entry
        chunk_entries.append(entry)
        
        # Add next entry if exists
        if i < len(entries) - 1:
            chunk_entries.append(entries[i + 1])
        
        # Create chunk
        chunks.append(Chunk(chunk_entries))
    
    return chunks

