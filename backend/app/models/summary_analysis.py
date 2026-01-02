"""
Content Summary Analysis Models

Models for the Content Summary feature that extracts key concepts,
TLDR, technical details, and action items from YouTube transcripts.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """Types of content that can be detected in transcripts."""
    PROGRAMMING_TECHNICAL = "programming_technical"
    TUTORIAL_HOWTO = "tutorial_howto"
    NEWS_CURRENT_EVENTS = "news_current_events"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    DISCUSSION_OPINION = "discussion_opinion"
    REVIEW = "review"
    INTERVIEW = "interview"
    OTHER = "other"


class TechnicalCategory(str, Enum):
    """Categories for technical details."""
    CODE_SNIPPET = "code_snippet"
    LIBRARY = "library"
    FRAMEWORK = "framework"
    COMMAND = "command"
    TOOL = "tool"
    API = "api"
    CONCEPT = "concept"


class Priority(str, Enum):
    """Priority levels for action items and concepts."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class KeyConcept(BaseModel):
    """A key concept extracted from the content."""
    concept: str = Field(..., description="Name/title of the concept")
    explanation: str = Field(..., description="Brief 1-2 sentence explanation")
    importance: Priority = Field(default=Priority.MEDIUM, description="Importance level")
    timestamp: Optional[float] = Field(None, description="Video timestamp in seconds")


class TechnicalDetail(BaseModel):
    """Technical details for programming/technical content."""
    category: TechnicalCategory = Field(..., description="Type of technical item")
    name: str = Field(..., description="Name of the item")
    description: Optional[str] = Field(None, description="Brief description if relevant")
    code: Optional[str] = Field(None, description="Actual code snippet if applicable")
    timestamp: Optional[float] = Field(None, description="Video timestamp in seconds")


class ActionItem(BaseModel):
    """Actionable takeaway from the content."""
    action: str = Field(..., description="The action or takeaway")
    context: Optional[str] = Field(None, description="When/why this is relevant")
    priority: Priority = Field(default=Priority.MEDIUM, description="Priority level")


class KeyMoment(BaseModel):
    """A significant moment in the video."""
    timestamp: float = Field(..., description="Video timestamp in seconds")
    title: str = Field(..., description="Brief title for this moment")
    description: str = Field(..., description="What happens at this moment")


class ScholarlyFigure(BaseModel):
    """A named figure mentioned in scholarly/educational content."""
    name: str = Field(..., description="Name of the figure")
    role: Optional[str] = Field(None, description="Role or title")
    period: Optional[str] = Field(None, description="Time period or dates")
    relationships: Optional[str] = Field(None, description="Relationships to other figures")
    significance: Optional[str] = Field(None, description="Why this figure is important")


class ScholarlySource(BaseModel):
    """A source or text discussed in scholarly content."""
    name: str = Field(..., description="Name of the source")
    type: Optional[str] = Field(None, description="Type of source (text, manuscript, etc.)")
    description: Optional[str] = Field(None, description="What this source is")
    significance: Optional[str] = Field(None, description="Why this source matters")


class ScholarlyDebate(BaseModel):
    """A scholarly debate or contested topic."""
    topic: str = Field(..., description="The topic being debated")
    positions: List[str] = Field(default_factory=list, description="Different scholarly positions")
    evidence: Optional[str] = Field(None, description="Evidence supporting different positions")
    consensus: Optional[str] = Field(None, description="Current scholarly consensus if any")


class EvidenceType(BaseModel):
    """A type of evidence mentioned in the content."""
    type: str = Field(..., description="Type of evidence (archaeological, textual, etc.)")
    examples: List[str] = Field(default_factory=list, description="Specific examples mentioned")
    significance: Optional[str] = Field(None, description="What this evidence shows")


class TimePeriod(BaseModel):
    """A historical time period discussed."""
    period: str = Field(..., description="Name of the period")
    dates: Optional[str] = Field(None, description="Approximate dates")
    context: Optional[str] = Field(None, description="Relevant historical context")


class ScholarlyContext(BaseModel):
    """Scholarly context for educational content."""
    figures: List[ScholarlyFigure] = Field(
        default_factory=list,
        description="Named figures discussed"
    )
    sources: List[ScholarlySource] = Field(
        default_factory=list,
        description="Sources and texts mentioned"
    )
    debates: List[ScholarlyDebate] = Field(
        default_factory=list,
        description="Scholarly debates presented"
    )
    evidence_types: List[EvidenceType] = Field(
        default_factory=list,
        description="Types of evidence discussed"
    )
    methodology: List[str] = Field(
        default_factory=list,
        description="Methodological approaches used"
    )
    time_periods: List[TimePeriod] = Field(
        default_factory=list,
        description="Historical periods discussed"
    )


class ContentSummaryResult(BaseModel):
    """Complete result of the content summary analysis."""

    # Content Type Detection
    content_type: ContentType = Field(..., description="Detected content type")
    content_type_confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence in content type detection"
    )
    content_type_reasoning: str = Field(
        default="",
        description="Brief explanation for content type classification"
    )

    # TLDR Summary
    tldr: str = Field(..., description="2-3 sentence summary of the content")

    # Key Concepts
    key_concepts: List[KeyConcept] = Field(
        default_factory=list,
        description="Main ideas and concepts from the content"
    )

    # Technical Details (populated for technical content)
    technical_details: List[TechnicalDetail] = Field(
        default_factory=list,
        description="Technical items like code, libraries, commands"
    )
    has_technical_content: bool = Field(
        default=False,
        description="Whether technical content was detected"
    )

    # Action Items / Takeaways
    action_items: List[ActionItem] = Field(
        default_factory=list,
        description="Actionable takeaways from the content"
    )

    # Keywords/Tags for Obsidian
    keywords: List[str] = Field(
        default_factory=list,
        description="Keywords/tags for organization (lowercase, no spaces)"
    )
    suggested_obsidian_tags: List[str] = Field(
        default_factory=list,
        description="Same as keywords but prefixed with #"
    )

    # Key Moments with Timestamps
    key_moments: List[KeyMoment] = Field(
        default_factory=list,
        description="Important moments with timestamps"
    )

    # Scholarly Context (for educational content)
    scholarly_context: Optional[ScholarlyContext] = Field(
        None,
        description="Scholarly context for educational/academic content"
    )

    # Metadata
    tokens_used: int = Field(default=0, description="Tokens used for analysis")
    analysis_duration_seconds: float = Field(
        default=0.0,
        description="Time taken for analysis"
    )
    transcript_word_count: int = Field(
        default=0,
        description="Word count of analyzed transcript"
    )


class ContentSummaryRequest(BaseModel):
    """Request for content summary analysis."""
    transcript: str = Field(..., description="The transcript text to analyze")
    transcript_data: Optional[List[dict]] = Field(
        None,
        description="Timestamped transcript segments"
    )
    video_title: Optional[str] = Field(None, description="Title of the video")
    video_author: Optional[str] = Field(None, description="Channel/author name")
    video_id: Optional[str] = Field(None, description="YouTube video ID")
    video_url: Optional[str] = Field(None, description="Full YouTube URL for export linking")
