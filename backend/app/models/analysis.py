"""
Pydantic models for Rhetorical Analysis feature.

These models define the request/response schemas for the rhetorical analysis API.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# Request Models

class AnalysisRequest(BaseModel):
    """Request body for rhetorical analysis endpoint."""

    transcript: str = Field(..., description="The full transcript text to analyze")
    transcript_data: Optional[List[dict]] = Field(
        None,
        description="Transcript segments with timestamps [{text, start, duration}]"
    )
    verify_quotes: bool = Field(
        True,
        description="Whether to verify potential quotes via web search"
    )
    video_title: Optional[str] = Field(None, description="Title of the video for context")
    video_author: Optional[str] = Field(None, description="Author/speaker for context")


# Response Models

class TechniqueMatch(BaseModel):
    """A detected rhetorical technique in the transcript."""

    technique_id: str = Field(..., description="Unique ID of the technique (e.g., 'anaphora')")
    technique_name: str = Field(..., description="Human-readable name of the technique")
    category: str = Field(..., description="Category of the technique (e.g., 'repetition')")
    phrase: str = Field(..., description="The exact phrase from the transcript that uses this technique")
    start_time: Optional[float] = Field(None, description="Video timestamp where phrase begins (seconds)")
    end_time: Optional[float] = Field(None, description="Video timestamp where phrase ends (seconds)")
    explanation: str = Field(..., description="Explanation of why this qualifies as this technique")
    strength: Literal["strong", "moderate", "subtle"] = Field(
        ...,
        description="How clearly this exemplifies the technique"
    )
    context: Optional[str] = Field(None, description="Surrounding context for the phrase")


class QuoteMatch(BaseModel):
    """A detected potential quote or attribution in the transcript."""

    phrase: str = Field(..., description="The phrase that may be a quote")
    is_quote: bool = Field(..., description="Whether this appears to be a quote from another source")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level (0-1)")
    source: Optional[str] = Field(
        None,
        description="Identified source (e.g., 'Bible - Romans 5:3', 'MLK - I Have a Dream')"
    )
    source_type: Optional[Literal["religious", "political", "literary", "philosophical", "scientific", "unknown"]] = Field(
        None,
        description="Category of the source"
    )
    verified: bool = Field(False, description="Whether web search confirmed the attribution")
    verification_details: Optional[str] = Field(None, description="Details from web search verification")
    start_time: Optional[float] = Field(None, description="Video timestamp where quote begins")


class PillarScore(BaseModel):
    """Score for one of the four rhetorical pillars."""

    pillar: Literal["logos", "pathos", "ethos", "kairos"] = Field(
        ...,
        description="Which pillar this score is for"
    )
    pillar_name: str = Field(..., description="Human-readable pillar name")
    score: int = Field(..., ge=0, le=100, description="Score out of 100")
    explanation: str = Field(..., description="Why this pillar received this score")
    contributing_techniques: List[str] = Field(
        default_factory=list,
        description="Technique IDs that contributed to this score"
    )
    key_examples: List[str] = Field(
        default_factory=list,
        description="Key phrases demonstrating this pillar"
    )


class TechniqueSummary(BaseModel):
    """Summary of a technique's usage in the transcript."""

    technique_id: str
    technique_name: str
    category: str
    count: int = Field(..., description="Number of times this technique was used")
    strongest_example: str = Field(..., description="Best example of this technique")


class AnalysisResult(BaseModel):
    """Complete result of rhetorical analysis."""

    # Overall Assessment
    overall_score: int = Field(..., ge=0, le=100, description="Overall rhetorical effectiveness score")
    overall_grade: Literal["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F"] = Field(
        ...,
        description="Letter grade for rhetorical effectiveness"
    )

    # Pillar Breakdown
    pillar_scores: List[PillarScore] = Field(
        ...,
        description="Scores for each of the four rhetorical pillars"
    )

    # Technique Analysis
    technique_matches: List[TechniqueMatch] = Field(
        default_factory=list,
        description="All detected rhetorical techniques"
    )
    technique_summary: List[TechniqueSummary] = Field(
        default_factory=list,
        description="Summary of techniques used"
    )
    total_techniques_found: int = Field(..., description="Total number of technique instances found")
    unique_techniques_used: int = Field(..., description="Number of distinct techniques used")

    # Quote Analysis
    quote_matches: List[QuoteMatch] = Field(
        default_factory=list,
        description="Detected quotes and attributions"
    )
    total_quotes_found: int = Field(0, description="Total number of potential quotes found")
    verified_quotes: int = Field(0, description="Number of quotes verified via web search")

    # Summary
    executive_summary: str = Field(
        ...,
        description="A 2-3 paragraph executive summary of the rhetorical analysis"
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Key rhetorical strengths of the speaker"
    )
    areas_for_improvement: List[str] = Field(
        default_factory=list,
        description="Areas where rhetorical effectiveness could improve"
    )

    # Metadata
    tokens_used: int = Field(0, description="Number of API tokens used for analysis")
    analysis_duration_seconds: float = Field(0, description="How long the analysis took")
    transcript_word_count: int = Field(0, description="Word count of the analyzed transcript")


class AnalysisError(BaseModel):
    """Error response for analysis failures."""

    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code for programmatic handling")
    details: Optional[str] = Field(None, description="Additional error details")


# Helper function to calculate grade from score
def score_to_grade(score: int) -> str:
    """Convert numeric score to letter grade."""
    if score >= 97:
        return "A+"
    elif score >= 93:
        return "A"
    elif score >= 90:
        return "A-"
    elif score >= 87:
        return "B+"
    elif score >= 83:
        return "B"
    elif score >= 80:
        return "B-"
    elif score >= 77:
        return "C+"
    elif score >= 73:
        return "C"
    elif score >= 70:
        return "C-"
    elif score >= 60:
        return "D"
    else:
        return "F"
