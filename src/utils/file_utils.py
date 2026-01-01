"""File operation utilities"""

from pathlib import Path
from typing import Optional


def ensure_directory(path: Path) -> None:
    """Ensure directory exists, create if it doesn't"""
    path.mkdir(parents=True, exist_ok=True)


def find_file_in_directory(directory: Path, pattern: str) -> Optional[Path]:
    """Find first file matching pattern in directory
    
    Args:
        directory: Directory to search
        pattern: File pattern (e.g., "*.srt", "movie.*")
        
    Returns:
        Path to first matching file, or None if not found
    """
    if not directory.exists():
        return None
    
    matches = list(directory.glob(pattern))
    return matches[0] if matches else None

