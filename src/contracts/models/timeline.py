"""Pydantic models for Timeline schema v1.0"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class SpoilerRisk(BaseModel):
    """Spoiler risk assessment"""
    risk: float = Field(..., ge=0, le=1, description="Spoiler risk score (0=safe, 1=severe spoiler)")
    reason: Literal["plot_twist", "ending", "character_death", "none"] = Field(
        default="none",
        description="Reason for spoiler risk"
    )
    confidence: float = Field(default=0.0, ge=0, le=1, description="Confidence in spoiler detection")


class Transitions(BaseModel):
    """Transition effects for a segment"""
    before: Optional[Literal["cut", "fade", "dissolve", "wipe"]] = None
    after: Optional[Literal["cut", "fade", "dissolve", "wipe"]] = None
    duration: Optional[float] = Field(None, description="Transition duration in seconds")


class SegmentOverlay(BaseModel):
    """Segment-specific overlay"""
    type: Literal["logo", "text", "watermark"]
    start: Optional[float] = None
    end: Optional[float] = None
    position: Optional[str] = None
    file: Optional[str] = None


class CTAInsert(BaseModel):
    """Call-to-action insertion point"""
    enabled: bool = False
    text: Optional[str] = None
    link: Optional[str] = None


class NarrationAlignment(BaseModel):
    """Narration audio alignment settings"""
    offset: Optional[float] = Field(None, description="Audio offset in seconds")
    stretch: Optional[float] = Field(None, description="Time stretch factor")


class Segment(BaseModel):
    """Video segment definition"""
    start: float = Field(..., description="Segment start time in seconds")
    end: float = Field(..., description="Segment end time in seconds")
    score: Optional[float] = Field(None, ge=0, le=1, description="Similarity score")
    priority: Optional[int] = Field(None, ge=1, le=10, description="Clip priority")
    weight: Optional[float] = Field(None, description="Scene weight")
    spoiler: Optional[SpoilerRisk] = None
    transitions: Optional[Transitions] = None
    overlays: Optional[List[SegmentOverlay]] = None
    cta_insert: Optional[CTAInsert] = None
    narration_alignment: Optional[NarrationAlignment] = None


class GlobalOverlay(BaseModel):
    """Global overlay applied to entire video"""
    type: Literal["logo", "text", "watermark"]
    position: Literal["top-left", "top-right", "bottom-left", "bottom-right", "center"]
    file: Optional[str] = None
    opacity: Optional[float] = Field(None, ge=0, le=1)
    start_time: Optional[float] = None
    end_time: Optional[float] = None


class TimelineOptions(BaseModel):
    """Timeline generation options"""
    spoiler_safe_mode: Optional[bool] = False
    spoiler_risk_threshold: Optional[float] = Field(0.3, ge=0, le=1)
    max_duration: Optional[float] = None
    min_segment_length: Optional[float] = None
    similarity_threshold: Optional[float] = None


class TimelineMetadata(BaseModel):
    """Timeline metadata"""
    project_id: Optional[str] = None
    movie_id: Optional[str] = None
    generated_at: Optional[datetime] = None
    version: Optional[str] = "1.0"
    options: Optional[TimelineOptions] = None


class Timeline(BaseModel):
    """Timeline JSON model - matches timeline.schema.json"""
    input: str = Field(..., description="Path to input video file")
    narration: str = Field(..., description="Path to narration audio file")
    output: str = Field(..., description="Path to output video file")
    segments: List[Segment] = Field(..., description="Array of video segments")
    global_overlays: Optional[List[GlobalOverlay]] = None
    metadata: Optional[TimelineMetadata] = None

    class Config:
        json_schema_extra = {
            "example": {
                "input": "films/input/movie.mp4",
                "narration": "films/narration/narration.m4a",
                "output": "films/output/final.mp4",
                "segments": [
                    {"start": 0.5, "end": 3.2},
                    {"start": 15.0, "end": 18.4}
                ]
            }
        }

