"""
Health Observation Models

Data models for the health observation analysis feature.
Extracts frames from YouTube videos, filters for human presence,
and uses Claude vision to identify observable health-related features.

IMPORTANT: This is an EDUCATIONAL tool only - NOT for medical diagnosis.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# === Constants ===

HEALTH_DISCLAIMER = """EDUCATIONAL TOOL ONLY - NOT MEDICAL ADVICE

This analysis identifies visual observations that MAY warrant professional medical evaluation. This tool:

- Does NOT diagnose medical conditions
- Does NOT replace healthcare professionals
- Does NOT account for lighting, camera quality, makeup, or angles
- Should NEVER be used for treatment decisions
- May produce false positives due to image quality/lighting

AI observations are NOT determinative. If you have health concerns, please consult a licensed healthcare provider."""


CLAUDE_HEALTH_PROMPT = """You are analyzing a video frame for EDUCATIONAL purposes only.
You are NOT providing medical diagnosis - only observations.

## Your Role
You are like a friend pointing out "hey, you might want to ask a doctor about that" - NOT a doctor yourself.

## Frame Context
- Timestamp: {timestamp} seconds ({formatted_time})
- Body regions visible: {regions}
- Video: {video_title}

## Your Task
Examine the visible human(s) and note any observable features that MIGHT be worth mentioning to a healthcare provider. Focus on:

1. **Eyes**: Drooping, discoloration, puffiness, asymmetry
2. **Skin**: Color changes, texture, visible marks
3. **Face**: Asymmetry, swelling, unusual features
4. **Hands**: Swelling, nail changes, joint appearance
5. **Neck**: Swelling, visible masses
6. **Posture**: Asymmetry, unusual positioning

## Critical Rules
- NEVER diagnose - only describe what you observe
- ALWAYS note limitations (lighting, quality, angle)
- ALWAYS include confidence percentage (0.0 to 1.0)
- Rate severity: informational / worth_mentioning / consider_checkup
- Reference medical literature when relevant
- Note skin color observation limitations due to lighting
- If nothing notable is observed, return an empty observations array

## Output Format
Return ONLY valid JSON (no markdown, no explanation):
{{
  "observations": [
    {{
      "body_region": "eyes",
      "observation": "Slight asymmetry in eyelid position, left appears lower",
      "reasoning": "Eyelid asymmetry can sometimes be normal variation or worth checking",
      "confidence": 0.6,
      "limitations": ["Camera angle may exaggerate asymmetry", "Single frame - could be mid-blink"],
      "severity": "informational",
      "related_conditions": ["Ptosis (educational context only)"],
      "references": ["General ophthalmology reference"]
    }}
  ],
  "image_quality_notes": ["Good lighting", "Medium resolution"],
  "overall_notes": "Limited observations possible from single frame"
}}"""


# === Enums ===

class BodyRegion(str, Enum):
    """Body regions that can be observed in video frames."""
    FACE = "face"
    EYES = "eyes"
    SKIN = "skin"
    HANDS = "hands"
    NECK = "neck"
    POSTURE = "posture"
    OTHER = "other"


class ObservationSeverity(str, Enum):
    """Severity level of an observation."""
    INFORMATIONAL = "informational"      # Just noting what's visible
    WORTH_MENTIONING = "worth_mentioning" # Might want to be aware
    CONSIDER_CHECKUP = "consider_checkup" # Consider asking a doctor


# === Core Models ===

class HealthObservation(BaseModel):
    """A single observable feature from a frame."""
    observation_id: str = Field(default="", description="Unique identifier for this observation")
    timestamp: float = Field(ge=0.0, description="Seconds into video where observation was made")
    body_region: BodyRegion = Field(..., description="Body region where observation was made")
    observation: str = Field(..., description="What was observed (descriptive, not diagnostic)")
    reasoning: str = Field(default="", description="Why this might be notable")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the observation (0-1)")
    limitations: List[str] = Field(default_factory=list, description="Why this might be wrong")
    severity: ObservationSeverity = Field(default=ObservationSeverity.INFORMATIONAL)
    related_conditions: List[str] = Field(
        default_factory=list,
        description="What a doctor might consider (educational context only)"
    )
    references: List[str] = Field(default_factory=list, description="Medical literature references")


class FrameAnalysis(BaseModel):
    """Analysis of a single video frame."""
    frame_id: str = Field(default="", description="Unique identifier for this frame")
    timestamp: float = Field(ge=0.0, description="Seconds into video")
    humans_detected: int = Field(ge=0, description="Number of humans detected in frame")
    body_regions_visible: List[BodyRegion] = Field(
        default_factory=list,
        description="Which body regions are visible in this frame"
    )
    observations: List[HealthObservation] = Field(default_factory=list)
    image_quality_notes: List[str] = Field(
        default_factory=list,
        description="Notes about image quality (lighting, blur, etc.)"
    )


class ExtractedFrame(BaseModel):
    """A frame extracted from a video."""
    frame_path: str = Field(..., description="Path to the extracted frame file")
    timestamp: float = Field(ge=0.0, description="Seconds into video")
    frame_index: int = Field(ge=0, description="Sequential frame number")


class HumanDetectionResult(BaseModel):
    """Result of human detection on a single frame."""
    has_human: bool = Field(default=False, description="Whether a human was detected")
    face_detected: bool = Field(default=False)
    hands_detected: bool = Field(default=False)
    body_detected: bool = Field(default=False)
    body_regions: List[BodyRegion] = Field(
        default_factory=list,
        description="Which body regions were detected"
    )
    detection_confidence: float = Field(ge=0.0, le=1.0, default=0.0)


# === Full Result Models ===

class HealthObservationResult(BaseModel):
    """Complete analysis result for a video."""
    video_id: str = Field(..., description="YouTube video ID")
    video_title: str = Field(default="", description="Video title")
    video_url: str = Field(default="", description="Full YouTube URL")

    # Analysis metadata
    frames_extracted: int = Field(ge=0, default=0, description="Total frames extracted from video")
    frames_with_humans: int = Field(ge=0, default=0, description="Frames that contained humans")
    frames_analyzed: int = Field(ge=0, default=0, description="Frames analyzed by Claude vision")

    # Results
    observations: List[HealthObservation] = Field(
        default_factory=list,
        description="All observations found across frames"
    )
    summary: str = Field(default="", description="Overall summary of observations")

    # Grouped by body region for UI
    observations_by_region: Dict[str, List[HealthObservation]] = Field(
        default_factory=dict,
        description="Observations grouped by body region"
    )

    # Frame analyses (individual frame results)
    frame_analyses: List[FrameAnalysis] = Field(
        default_factory=list,
        description="Analysis results for each frame"
    )

    # Important notes
    limitations: List[str] = Field(
        default_factory=list,
        description="General limitations of the analysis"
    )
    disclaimer: str = Field(
        default=HEALTH_DISCLAIMER,
        description="Medical disclaimer (always included)"
    )

    # Metadata
    analysis_duration_seconds: float = Field(ge=0.0, default=0.0)
    analyzed_at: str = Field(default="", description="ISO timestamp of when analysis was performed")
    interval_seconds: int = Field(default=30, description="Interval between extracted frames")
    model_used: str = Field(default="claude-sonnet-4-20250514", description="Vision model used")


# === Request Models ===

class HealthObservationRequest(BaseModel):
    """Request for health observation analysis."""
    video_url: str = Field(..., description="YouTube video URL")
    video_id: Optional[str] = Field(None, description="YouTube video ID (if known)")
    video_title: Optional[str] = Field(None, description="Video title (if known)")

    # Extraction options
    interval_seconds: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Extract a frame every N seconds"
    )
    max_frames: int = Field(
        default=20,
        ge=1,
        le=50,
        description="Maximum frames to analyze"
    )

    # Analysis options
    skip_if_cached: bool = Field(
        default=True,
        description="Return cached results if available"
    )


# === Helper Functions ===

def format_timestamp(seconds: float) -> str:
    """Format seconds as MM:SS or HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def group_observations_by_region(
    observations: List[HealthObservation]
) -> Dict[str, List[HealthObservation]]:
    """Group observations by body region for UI display."""
    grouped: Dict[str, List[HealthObservation]] = {}
    for obs in observations:
        region = obs.body_region.value
        if region not in grouped:
            grouped[region] = []
        grouped[region].append(obs)
    return grouped
