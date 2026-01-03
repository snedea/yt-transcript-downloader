from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import Field, SQLModel, JSON, Column
from sqlalchemy import PrimaryKeyConstraint
import uuid
import json


class TranscriptBase(SQLModel):
    """Base model for transcripts - shared fields without table config"""
    video_title: str
    author: Optional[str] = None
    upload_date: Optional[str] = None
    transcript: str  # The full text

    # Store JSON strings to match existing SQLite schema for now
    # In a future refactor, we can switch to JSON type with automatic serialization
    transcript_data: Optional[str] = None  # JSON string

    tokens_used: int = 0
    is_cleaned: bool = False

    # Multi-source support fields
    source_type: str = Field(default="youtube")  # youtube, pdf, web_url, plain_text
    source_url: Optional[str] = None  # Original filename or URL
    file_path: Optional[str] = None  # Path to stored file (for PDFs)
    thumbnail_path: Optional[str] = None  # Path to thumbnail image

    # Content metadata
    word_count: int = Field(default=0)
    character_count: int = Field(default=0)
    page_count: Optional[int] = None  # For PDFs

    # Analysis fields (JSON strings)
    analysis_result: Optional[str] = None
    analysis_date: Optional[str] = None

    summary_result: Optional[str] = None
    summary_date: Optional[str] = None

    manipulation_result: Optional[str] = None
    manipulation_date: Optional[str] = None

    discovery_result: Optional[str] = None
    discovery_date: Optional[str] = None

    health_observation_result: Optional[str] = None
    health_observation_date: Optional[str] = None

    prompts_result: Optional[str] = None
    prompts_date: Optional[str] = None


class Transcript(TranscriptBase, table=True):
    """
    Transcript model with composite primary key (video_id, user_id).

    This ensures each user can have their own cached transcript for any video,
    preventing data overwrites when multiple users access the same content.
    """
    __tablename__ = "transcripts"
    __table_args__ = (
        PrimaryKeyConstraint("video_id", "user_id", name="pk_transcripts"),
    )

    # Composite Primary Key fields
    video_id: str = Field(index=True, nullable=False)
    user_id: str = Field(foreign_key="users.id", index=True, nullable=False, max_length=36)

    # Metadata fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = 1

    # We could add Relationship here, but requires importing User which might cause circular imports
    # if not careful. For now, we keep it simple.


# Pydantic models for API responses (compatible with existing frontend mostly)

class TranscriptRead(TranscriptBase):
    video_id: str
    user_id: str
    created_at: datetime
    last_accessed: datetime
    access_count: int


class TranscriptHistoryItem(SQLModel):
    video_id: str
    video_title: str
    author: Optional[str] = None
    upload_date: Optional[str] = None
    created_at: datetime
    last_accessed: datetime
    access_count: int
    tokens_used: int
    is_cleaned: bool

    # Multi-source support fields
    source_type: str = "youtube"
    source_url: Optional[str] = None
    file_path: Optional[str] = None
    thumbnail_url: Optional[str] = None  # Note: URL not path (for API response)

    # Content metadata
    word_count: int = 0
    character_count: int = 0
    page_count: Optional[int] = None

    # Flags for which analysis types are available
    has_analysis: bool = False
    has_summary: bool = False
    has_manipulation: bool = False
    has_rhetorical: bool = False
    has_discovery: bool = False
    has_health: bool = False
    has_prompts: bool = False


class TranscriptHistoryResponse(SQLModel):
    items: List[TranscriptHistoryItem]
    total: int
    limit: int
    offset: int


class TranscriptListResponse(SQLModel):
    items: List[Any]
    total: int
