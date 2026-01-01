"""
SQLite database models for transcript caching.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CachedTranscript(BaseModel):
    """A cached transcript stored in the database."""

    video_id: str = Field(..., description="YouTube video ID")
    video_title: str = Field(..., description="Video title")
    author: Optional[str] = Field(None, description="Channel/author name")
    upload_date: Optional[str] = Field(None, description="Upload date")
    transcript: str = Field(..., description="Full transcript text")
    transcript_data: Optional[str] = Field(None, description="JSON string of transcript segments with timestamps")
    tokens_used: int = Field(0, description="Tokens used for cleaning (if any)")
    is_cleaned: bool = Field(False, description="Whether transcript was cleaned with AI")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = Field(1, description="Number of times this transcript was accessed")


class TranscriptHistoryItem(BaseModel):
    """Summary item for transcript history list."""

    video_id: str
    video_title: str
    author: Optional[str]
    is_cleaned: bool
    has_analysis: bool = False
    created_at: datetime
    last_accessed: datetime
    access_count: int


class TranscriptHistoryResponse(BaseModel):
    """Response for transcript history endpoint."""

    items: List[TranscriptHistoryItem]
    total: int
