"""
Manipulation Analysis Models

Extended data models for the comprehensive transcript manipulation analyzer.
These models support the 5-dimension analysis framework:
- Epistemic Integrity
- Argument Quality
- Manipulation Risk
- Rhetorical Craft
- Fairness/Balance
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Literal
from pydantic import BaseModel, Field


# === Enums ===

class ClaimType(str, Enum):
    """Types of claims that can be detected in a transcript."""
    FACTUAL = "factual"           # Verifiable fact claims
    CAUSAL = "causal"             # Cause-effect claims
    NORMATIVE = "normative"       # Value/moral claims
    PREDICTION = "prediction"     # Future-oriented claims
    PRESCRIPTIVE = "prescriptive" # Action-oriented claims ("you should...")


class VerificationStatus(str, Enum):
    """Status of claim verification via web search."""
    VERIFIED = "verified"         # Claim confirmed by sources
    DISPUTED = "disputed"         # Claim contradicted by sources
    UNVERIFIED = "unverified"     # No clear confirmation found
    UNVERIFIABLE = "unverifiable" # Claim cannot be fact-checked (opinion, prediction, etc.)


class AnnotationSeverity(str, Enum):
    """Severity level of detected manipulation techniques."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AnalysisMode(str, Enum):
    """Analysis depth mode."""
    QUICK = "quick"  # Single GPT call, ~15 seconds
    DEEP = "deep"    # Multi-pass pipeline, ~60 seconds


class DimensionType(str, Enum):
    """The 5 analysis dimensions."""
    EPISTEMIC_INTEGRITY = "epistemic_integrity"
    ARGUMENT_QUALITY = "argument_quality"
    MANIPULATION_RISK = "manipulation_risk"
    RHETORICAL_CRAFT = "rhetorical_craft"
    FAIRNESS_BALANCE = "fairness_balance"


# === Claim Models ===

class DetectedClaim(BaseModel):
    """A claim detected in the transcript."""
    claim_id: str = Field(default="", description="Unique identifier for the claim")
    claim_text: str = Field(..., description="The exact text of the claim")
    claim_type: ClaimType = Field(..., description="Type of claim")
    confidence: float = Field(ge=0.0, le=1.0, description="Detection confidence")
    segment_index: int = Field(ge=0, description="Index of the segment containing this claim")
    span: Tuple[int, int] = Field(default=(0, 0), description="Character positions (start, end)")
    start_time: Optional[float] = Field(None, description="Video timestamp in seconds")

    # Verification fields
    verification_status: Optional[VerificationStatus] = None
    verification_details: Optional[str] = None
    supporting_sources: List[str] = Field(default_factory=list)
    contradicting_sources: List[str] = Field(default_factory=list)


# === Annotation Models ===

class SegmentAnnotation(BaseModel):
    """An annotation marking a manipulation technique or rhetorical device in a segment."""
    annotation_id: str = Field(default="", description="Unique identifier")
    span: Tuple[int, int] = Field(..., description="Character positions (start, end)")
    label: str = Field(..., description="Technique/device label (e.g., 'fear_appeal', 'strawman')")
    category: str = Field(default="", description="Category (language, reasoning, propaganda)")
    confidence: float = Field(ge=0.0, le=1.0, description="Detection confidence")
    explanation: str = Field(..., description="Why this annotation was applied")
    severity: AnnotationSeverity = Field(default=AnnotationSeverity.MEDIUM)


class AnalyzedSegment(BaseModel):
    """A segment of the transcript with full analysis."""
    segment_index: int = Field(ge=0)
    start_time: float = Field(ge=0.0, description="Video start time in seconds")
    end_time: float = Field(ge=0.0, description="Video end time in seconds")
    text: str = Field(..., description="The segment text")

    # Analysis results for this segment
    claims: List[DetectedClaim] = Field(default_factory=list)
    annotations: List[SegmentAnnotation] = Field(default_factory=list)

    # Optional argument mapping (Toulmin model)
    toulmin_role: Optional[str] = Field(None, description="Role in argument: claim, grounds, warrant, backing, qualifier, rebuttal")
    linked_to: List[str] = Field(default_factory=list, description="IDs of related segments/claims")


# === Dimension Scoring ===

class DimensionScore(BaseModel):
    """Score for one of the 5 analysis dimensions."""
    dimension: DimensionType
    dimension_name: str = Field(default="", description="Human-readable name")
    score: int = Field(ge=0, le=100, description="Dimension score 0-100")
    confidence: float = Field(ge=0.0, le=1.0, default=0.8, description="Scoring confidence")
    explanation: str = Field(default="", description="Why this score was given")

    # Detailed breakdown
    red_flags: List[str] = Field(default_factory=list, description="Concerning patterns found")
    strengths: List[str] = Field(default_factory=list, description="Positive patterns found")
    key_examples: List[str] = Field(default_factory=list, description="Example quotes")
    contributing_techniques: List[str] = Field(default_factory=list, description="Techniques affecting this score")


# === Device/Technique Summary ===

class DeviceSummary(BaseModel):
    """Summary of a manipulation device or technique usage."""
    device_id: str
    device_name: str
    category: str  # language, reasoning, propaganda
    count: int = Field(ge=0, description="Number of occurrences")
    severity: AnnotationSeverity = Field(default=AnnotationSeverity.MEDIUM)
    examples: List[str] = Field(default_factory=list, description="Example occurrences")


# === Full Analysis Result ===

class ManipulationAnalysisResult(BaseModel):
    """
    Complete result of the manipulation analysis.
    Extends the existing AnalysisResult with new dimensions.
    """
    # === Metadata ===
    analysis_version: str = Field(default="2.0")
    analysis_mode: AnalysisMode = Field(default=AnalysisMode.QUICK)
    passes_completed: int = Field(default=1, description="Number of analysis passes run")

    # === Legacy fields (backward compatible with existing AnalysisResult) ===
    overall_score: int = Field(ge=0, le=100, description="Overall score 0-100")
    overall_grade: str = Field(default="", description="Letter grade A+ to F")

    # === The 5 Dimension Scores ===
    dimension_scores: Dict[str, DimensionScore] = Field(
        default_factory=dict,
        description="Scores for all 5 dimensions"
    )

    # === Segment-Level Analysis ===
    segments: List[AnalyzedSegment] = Field(
        default_factory=list,
        description="Per-segment analysis with annotations"
    )

    # === Claims Analysis ===
    detected_claims: List[DetectedClaim] = Field(default_factory=list)
    verified_claims: List[DetectedClaim] = Field(
        default_factory=list,
        description="Claims that were fact-checked"
    )
    total_claims: int = Field(default=0)
    claims_verified: int = Field(default=0)
    claims_disputed: int = Field(default=0)

    # === Device/Technique Summary ===
    device_summary: List[DeviceSummary] = Field(
        default_factory=list,
        description="Summary of all devices/techniques found"
    )
    most_used_devices: List[DeviceSummary] = Field(
        default_factory=list,
        description="Top 5 most frequently used manipulation devices"
    )

    # === Summary ===
    executive_summary: str = Field(default="", description="2-3 paragraph overview")
    top_concerns: List[str] = Field(default_factory=list, description="Main red flags")
    top_strengths: List[str] = Field(default_factory=list, description="Main positive aspects")

    # Interpretations
    charitable_interpretation: str = Field(
        default="",
        description="Best-case reading of the content"
    )
    concerning_interpretation: str = Field(
        default="",
        description="Most concerning reading of the content"
    )

    # === Metrics ===
    tokens_used: int = Field(default=0)
    analysis_duration_seconds: float = Field(default=0.0)
    transcript_word_count: int = Field(default=0)


# === Request Models ===

class ManipulationAnalysisRequest(BaseModel):
    """Request for manipulation analysis."""
    transcript: str = Field(..., description="The transcript text to analyze")
    transcript_data: Optional[List[dict]] = Field(
        None,
        description="Timestamped transcript segments"
    )

    # Analysis options
    analysis_mode: AnalysisMode = Field(
        default=AnalysisMode.QUICK,
        description="Quick (single call) or Deep (multi-pass)"
    )
    verify_claims: bool = Field(
        default=True,
        description="Whether to verify factual claims via web search"
    )
    verify_quotes: bool = Field(
        default=True,
        description="Whether to verify quote attributions"
    )

    # Context
    video_title: Optional[str] = None
    video_author: Optional[str] = None
    video_id: Optional[str] = None


# === Helper Functions ===

def calculate_overall_score(dimension_scores: Dict[str, DimensionScore]) -> int:
    """
    Calculate overall score from dimension scores.

    Weights:
    - Epistemic Integrity: 25%
    - Argument Quality: 25%
    - Manipulation Risk: 20% (inverted - lower risk = higher score)
    - Rhetorical Craft: 15%
    - Fairness/Balance: 15%
    """
    weights = {
        DimensionType.EPISTEMIC_INTEGRITY.value: 0.25,
        DimensionType.ARGUMENT_QUALITY.value: 0.25,
        DimensionType.MANIPULATION_RISK.value: 0.20,
        DimensionType.RHETORICAL_CRAFT.value: 0.15,
        DimensionType.FAIRNESS_BALANCE.value: 0.15,
    }

    total_score = 0.0
    total_weight = 0.0

    for dim_key, weight in weights.items():
        if dim_key in dimension_scores:
            score = dimension_scores[dim_key].score
            # Invert manipulation risk (low risk = high score contribution)
            if dim_key == DimensionType.MANIPULATION_RISK.value:
                score = 100 - score
            total_score += score * weight
            total_weight += weight

    if total_weight > 0:
        return round(total_score / total_weight)
    return 50  # Default middle score


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
