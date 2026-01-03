"""Pydantic models for Project configuration"""

from typing import Optional, Literal, List
from pydantic import BaseModel, Field


class ProjectOptions(BaseModel):
    """Project processing options"""
    spoiler_safe_mode: bool = Field(default=False, description="Enable spoiler filtering")
    spoiler_risk_threshold: float = Field(
        default=0.3,
        ge=0,
        le=1,
        description="Maximum allowed spoiler risk (0-1)"
    )
    max_duration: Optional[float] = Field(None, description="Maximum output video duration in seconds")
    min_segment_length: float = Field(default=3.0, description="Minimum segment length in seconds")
    similarity_threshold: float = Field(
        default=0.75,
        ge=0,
        le=1,
        description="Minimum similarity score for segment selection"
    )
    preset: Literal["quick", "standard", "spoiler_safe", "high_quality"] = Field(
        default="standard",
        description="Processing preset"
    )


class EmbeddingConfig(BaseModel):
    """Embedding model configuration"""
    model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model name"
    )


class ProjectConfig(BaseModel):
    """Project workspace configuration"""
    movie_id: str = Field(..., description="IMDb ID or custom project identifier")
    movie_duration: float = Field(..., ge=0, description="Movie duration in seconds")
    movie_language: str = Field(..., description="Original language code (e.g., 'en', 'fa')")
    movie_video_path: Optional[str] = Field(None, description="Path to movie video file (optional)")
    narration_srt_files: List[str] = Field(default_factory=list, description="List of narration SRT file paths")
    options: Optional[ProjectOptions] = None
    embedding: Optional[EmbeddingConfig] = None

    class Config:
        json_schema_extra = {
            "example": {
                "movie_id": "tt0133093",
                "movie_duration": 7200.0,
                "movie_language": "en",
                "movie_video_path": "films/input/movie.mp4",
                "narration_srt_files": [
                    "films/narration/critique1.srt",
                    "films/narration/critique2.srt"
                ],
                "options": {
                    "spoiler_safe_mode": True,
                    "max_duration": 1200,
                    "similarity_threshold": 0.75,
                    "min_segment_length": 3.0,
                    "preset": "standard"
                },
                "embedding": {
                    "model": "sentence-transformers/all-MiniLM-L6-v2"
                }
            }
        }

