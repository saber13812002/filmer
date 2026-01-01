"""Pydantic models for Project configuration"""

from typing import Optional, Literal
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
    options: Optional[ProjectOptions] = None
    embedding: Optional[EmbeddingConfig] = None

    class Config:
        json_schema_extra = {
            "example": {
                "movie_id": "tt0133093",
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

