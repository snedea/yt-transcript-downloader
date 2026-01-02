"""
Content models for universal content ingestion.

Supports: YouTube, PDFs, web URLs, plain text
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import hashlib


class ContentSourceType(str, Enum):
    """Type of content source."""
    YOUTUBE = "youtube"
    PDF = "pdf"
    WEB_URL = "web_url"
    PLAIN_TEXT = "plain_text"
    MARKDOWN = "markdown"


class ContentSegment(BaseModel):
    """
    A segment of content with optional timing information.

    For YouTube: includes start/end times
    For PDFs: segment_index is the page number
    For other sources: just sequential segments
    """
    text: str
    start_time: Optional[float] = None  # Seconds for video, None for documents
    end_time: Optional[float] = None
    duration: Optional[float] = None
    segment_index: int = 0  # Page number for PDFs, paragraph index for text


class UnifiedContent(BaseModel):
    """
    Universal content representation for any source type.

    This model normalizes content from YouTube videos, PDFs, web pages,
    and plain text into a common format for analysis.
    """
    # Core content
    text: str = Field(..., description="Full extracted text content")

    # Source identification
    source_type: ContentSourceType
    source_id: str = Field(..., description="Unique ID: video_id, URL hash, or filename hash")
    source_url: Optional[str] = None

    # Metadata
    title: str
    author: Optional[str] = None
    upload_date: Optional[str] = None

    # Structured content (when available)
    segments: Optional[List[ContentSegment]] = None

    # Content stats
    word_count: int = 0
    character_count: int = 0

    # Source-specific metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Extraction info
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    extraction_success: bool = True
    extraction_error: Optional[str] = None

    @classmethod
    def from_text(
        cls,
        text: str,
        title: str = "Untitled",
        source_type: ContentSourceType = ContentSourceType.PLAIN_TEXT,
        source_url: Optional[str] = None,
        author: Optional[str] = None,
        segments: Optional[List[ContentSegment]] = None
    ) -> "UnifiedContent":
        """Create UnifiedContent from raw text."""
        # Generate source_id from text hash
        source_id = hashlib.md5(text.encode()).hexdigest()[:12]

        return cls(
            text=text,
            source_type=source_type,
            source_id=source_id,
            source_url=source_url,
            title=title,
            author=author,
            segments=segments,
            word_count=len(text.split()),
            character_count=len(text)
        )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "This is the full content of the video transcript...",
                "source_type": "youtube",
                "source_id": "dQw4w9WgXcQ",
                "source_url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
                "title": "Example Video Title",
                "author": "Channel Name",
                "word_count": 1500,
                "segments": [
                    {"text": "First segment", "start_time": 0.0, "segment_index": 0}
                ]
            }
        }


class ContentExtractionRequest(BaseModel):
    """Request to extract content from a source."""
    source: str = Field(..., description="URL, file path, or raw text")
    source_type: Optional[ContentSourceType] = Field(
        None,
        description="Content type. Auto-detected if not provided."
    )
    title: Optional[str] = Field(None, description="Override title")
    author: Optional[str] = Field(None, description="Override author")


class ContentUploadResponse(BaseModel):
    """Response after uploading and extracting content."""
    success: bool
    content: Optional[UnifiedContent] = None
    error: Optional[str] = None
