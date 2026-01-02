"""
Discovery Mode models.

Implements the "Kinoshita Pattern" for cross-domain knowledge transfer:
1. Problems & Blockers - What challenges exist?
2. Techniques & Principles - What solutions/methods are described?
3. Cross-Domain Applications - Where else could these apply?
4. Research Trail - What sources are referenced?
5. Experiment Ideas - What concrete next steps could someone take?
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.models.content import ContentSourceType


class Problem(BaseModel):
    """A problem or goal identified in the content."""
    problem_id: str = Field(..., description="Unique identifier")
    statement: str = Field(..., description="Clear problem statement")
    context: str = Field(..., description="Background/why it matters")
    blockers: List[str] = Field(default_factory=list, description="What's preventing solution")
    domain: str = Field(..., description="Field/domain (physics, biology, etc.)")
    timestamp: Optional[float] = Field(None, description="For video content, seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "problem_id": "prob-001",
                "statement": "X-rays at 10nm are absorbed by conventional lenses",
                "context": "Needed for next-generation lithography to print smaller transistors",
                "blockers": ["Material absorption", "Vacuum requirements", "No suitable optics"],
                "domain": "Physics/Optics",
                "timestamp": 245.0
            }
        }


class Technique(BaseModel):
    """A technique or method described in the content."""
    technique_id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Technique name, e.g., 'Multilayer mirror reflection'")
    principle: str = Field(..., description="Core mechanism/why it works")
    implementation: str = Field(..., description="How it's applied")
    requirements: List[str] = Field(default_factory=list, description="What's needed to use it")
    domain: str = Field(..., description="Original domain")
    source: Optional[str] = Field(None, description="Original paper/researcher")
    timestamp: Optional[float] = Field(None, description="For video content, seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "technique_id": "tech-001",
                "name": "Multilayer Mirror Reflection",
                "principle": "Stack alternating thin layers to create constructive interference for X-rays",
                "implementation": "Tungsten-carbon layers, each lambda/4 thick",
                "requirements": ["Precise layer deposition", "High vacuum", "Curved substrate"],
                "domain": "X-ray Physics",
                "source": "Underwood & Barbee (1983)"
            }
        }


class CrossDomainApplication(BaseModel):
    """Potential application of a technique in another domain."""
    application_id: str = Field(..., description="Unique identifier")
    source_technique: str = Field(..., description="technique_id reference")
    target_domain: str = Field(..., description="Where it could apply")
    hypothesis: str = Field(..., description="'What if we applied X to Y?'")
    potential_problems_solved: List[str] = Field(
        default_factory=list,
        description="Problems this might address"
    )
    adaptation_needed: str = Field(..., description="How to modify for new domain")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="0-1, how viable this seems"
    )
    similar_existing_work: Optional[str] = Field(None, description="Known prior art")

    class Config:
        json_schema_extra = {
            "example": {
                "application_id": "app-001",
                "source_technique": "tech-001",
                "target_domain": "Medical Imaging",
                "hypothesis": "What if we applied multilayer reflection to cellular X-ray microscopy?",
                "potential_problems_solved": [
                    "Higher-resolution imaging of cell structures",
                    "Non-destructive tissue analysis"
                ],
                "adaptation_needed": "Biocompatible materials, different wavelengths, lower power",
                "confidence": 0.85,
                "similar_existing_work": "X-ray crystallography uses similar principles"
            }
        }


class ResearchReference(BaseModel):
    """A reference mentioned or implied in the content."""
    reference_id: str = Field(..., description="Unique identifier")
    title: Optional[str] = Field(None, description="Paper/book title if known")
    authors: List[str] = Field(default_factory=list, description="Author names")
    year: Optional[int] = Field(None, description="Publication year")
    domain: str = Field(..., description="Field/domain")
    relevance: str = Field(..., description="Why it's relevant to the content")
    mentioned_at: Optional[float] = Field(None, description="Timestamp in video")

    class Config:
        json_schema_extra = {
            "example": {
                "reference_id": "ref-001",
                "title": "Multilayer mirrors for 4.48nm X-rays",
                "authors": ["James Underwood", "Troy Barbee"],
                "year": 1983,
                "domain": "X-ray Optics",
                "relevance": "Original paper that Kinoshita found, enabling EUV lithography"
            }
        }


class ExperimentIdea(BaseModel):
    """A concrete experiment idea with an optimized LLM prompt for execution."""
    experiment_id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Short, actionable title")
    description: str = Field(..., description="What this experiment aims to explore")
    difficulty: str = Field(..., description="easy/medium/hard")
    time_estimate: str = Field(..., description="Rough time estimate (e.g., '2 hours', '1 week')")
    prerequisites: List[str] = Field(default_factory=list, description="What you need before starting")
    success_criteria: List[str] = Field(default_factory=list, description="How to know if it worked")
    llm_prompt: str = Field(
        ...,
        description="Optimized, copy-pasteable prompt for an LLM to help execute this experiment"
    )
    related_techniques: List[str] = Field(
        default_factory=list,
        description="technique_ids this experiment builds on"
    )
    related_problems: List[str] = Field(
        default_factory=list,
        description="problem_ids this experiment addresses"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "experiment_id": "exp-001",
                "title": "Apply multilayer reflection to your domain",
                "description": "Identify a problem in your field that has similar 'absorption/blocking' constraints and explore whether layered interference patterns could help",
                "difficulty": "medium",
                "time_estimate": "4-8 hours",
                "prerequisites": ["Basic understanding of wave interference", "A problem domain to explore"],
                "success_criteria": ["Identified 3+ analogous problems", "Sketched one adaptation approach"],
                "llm_prompt": "You are a cross-domain innovation researcher...",
                "related_techniques": ["tech-001"],
                "related_problems": ["prob-001"]
            }
        }


class DiscoveryResult(BaseModel):
    """Full discovery analysis output using the Kinoshita Pattern."""
    # Content identification
    content_title: str
    source_type: ContentSourceType
    source_id: str
    source_url: Optional[str] = None

    # The Kinoshita Pattern extractions
    problems: List[Problem] = Field(default_factory=list)
    techniques: List[Technique] = Field(default_factory=list)
    cross_domain_applications: List[CrossDomainApplication] = Field(default_factory=list)
    research_trail: List[ResearchReference] = Field(default_factory=list)

    # Synthesis
    key_insights: List[str] = Field(
        default_factory=list,
        description="Top 3-5 insights from the content"
    )
    recommended_reads: List[str] = Field(
        default_factory=list,
        description="Suggested follow-up research"
    )
    experiment_ideas: List[ExperimentIdea] = Field(
        default_factory=list,
        description="Concrete experiments with LLM prompts to try"
    )

    # Metadata
    analysis_version: str = "1.0"
    tokens_used: int = 0
    analysis_duration_seconds: float = 0.0
    analyzed_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "content_title": "The Discovery of EUV Lithography",
                "source_type": "youtube",
                "source_id": "abc123def45",
                "problems": [{"problem_id": "prob-001", "statement": "..."}],
                "techniques": [{"technique_id": "tech-001", "name": "..."}],
                "key_insights": [
                    "Cross-domain reading is essential for breakthrough discoveries",
                    "Problems in one field often have solutions in another"
                ],
                "experiment_ideas": [
                    "List problems in your field with similar blockers",
                    "Search for techniques from unrelated fields"
                ]
            }
        }


class DiscoveryRequest(BaseModel):
    """Request to perform discovery analysis on content."""
    # Content source - either provide source directly or video_id for cached content
    source: Optional[str] = Field(
        None,
        description="URL, file path, or raw text to analyze"
    )
    source_type: Optional[ContentSourceType] = Field(
        None,
        description="Content type. Auto-detected if not provided."
    )
    video_id: Optional[str] = Field(
        None,
        description="For cached YouTube content, provide video_id instead of source"
    )

    # Analysis options
    focus_domains: Optional[List[str]] = Field(
        None,
        description="Optional: domains to focus cross-domain suggestions on"
    )
    max_applications: int = Field(
        5,
        ge=1,
        le=10,
        description="Maximum number of cross-domain applications to generate"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "source": "https://youtube.com/watch?v=abc123",
                "focus_domains": ["software engineering", "machine learning"],
                "max_applications": 5
            }
        }


class DiscoverySummary(BaseModel):
    """Lightweight summary for library display."""
    source_id: str
    content_title: str
    source_type: ContentSourceType
    problem_count: int
    technique_count: int
    application_count: int
    top_insight: Optional[str] = None
    analyzed_at: str  # ISO format string
