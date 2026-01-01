"""Pydantic models for inter-stage data contracts"""

from typing import List, Optional
from pydantic import BaseModel


class IngestOutput(BaseModel):
    """Output from ingest stage"""
    movie_srt_path: Optional[str] = None
    narration_srt_path: Optional[str] = None
    movie_video_path: Optional[str] = None
    narration_audio_path: Optional[str] = None
    validated: bool = False


class IndexOutput(BaseModel):
    """Output from index stage"""
    collection_name: str
    chunks_indexed: int
    total_duration: float


class SearchMatch(BaseModel):
    """Single search match result"""
    segment_id: str
    start_time: float
    end_time: float
    similarity_score: float
    narration_text: Optional[str] = None


class SearchOutput(BaseModel):
    """Output from search stage"""
    matches: List[SearchMatch]

