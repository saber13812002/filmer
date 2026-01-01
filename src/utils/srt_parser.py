"""SRT file parsing utilities"""

from typing import List, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SRTEntry:
    """Single SRT subtitle entry"""
    index: int
    start_time: float  # in seconds
    end_time: float    # in seconds
    text: str

    @property
    def duration(self) -> float:
        """Get duration in seconds"""
        return self.end_time - self.start_time

    @property
    def word_count(self) -> int:
        """Get word count"""
        return len(self.text.split())


def parse_srt_time(time_str: str) -> float:
    """Parse SRT time format (HH:MM:SS,mmm) to seconds
    
    Args:
        time_str: Time string in format HH:MM:SS,mmm
        
    Returns:
        Time in seconds as float
    """
    time_part, millis = time_str.split(',')
    hours, minutes, seconds = map(int, time_part.split(':'))
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds + int(millis) / 1000.0


def parse_srt_file(file_path: Path) -> List[SRTEntry]:
    """Parse SRT file and return list of entries
    
    Args:
        file_path: Path to SRT file
        
    Returns:
        List of SRTEntry objects
    """
    entries = []
    
    if not file_path.exists():
        raise FileNotFoundError(f"SRT file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by double newlines to get individual entries
    blocks = content.strip().split('\n\n')
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        
        try:
            index = int(lines[0])
            time_line = lines[1]
            text = '\n'.join(lines[2:])
            
            # Parse time range (format: HH:MM:SS,mmm --> HH:MM:SS,mmm)
            start_str, end_str = time_line.split(' --> ')
            start_time = parse_srt_time(start_str.strip())
            end_time = parse_srt_time(end_str.strip())
            
            entries.append(SRTEntry(
                index=index,
                start_time=start_time,
                end_time=end_time,
                text=text
            ))
        except (ValueError, IndexError) as e:
            # Skip malformed entries
            continue
    
    return entries

