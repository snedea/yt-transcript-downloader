"""
Analysis Router

API endpoints for rhetorical analysis and manipulation analysis of transcripts.

Supports two analysis modes:
- v1.0 Rhetorical Analysis: 4 pillars (Logos, Pathos, Ethos, Kairos) + technique detection
- v2.0 Manipulation Analysis: 5 dimensions + claim verification + segment annotations
"""

import logging
from fastapi import APIRouter, HTTPException

from app.models.analysis import AnalysisRequest, AnalysisResult, AnalysisError
from app.models.manipulation_analysis import (
    ManipulationAnalysisRequest,
    ManipulationAnalysisResult,
    AnalysisMode
)
from app.models.summary_analysis import (
    ContentSummaryRequest,
    ContentSummaryResult
)
from app.models.discovery import (
    DiscoveryRequest,
    DiscoveryResult
)
from app.models.content import UnifiedContent
from app.services.rhetorical_analysis import get_analysis_service
from app.services.manipulation_pipeline import get_manipulation_pipeline
from app.services.summary_service import get_summary_service
from app.services.discovery_service import DiscoveryService
from app.services.content_extractor import extract_content
from app.services.cache_service import CacheService
from app.data.rhetorical_toolkit import (
    RHETORICAL_TECHNIQUES,
    RHETORICAL_PILLARS,
    TECHNIQUE_CATEGORIES,
    get_toolkit_summary
)
from app.data.manipulation_toolkit import (
    DIMENSION_DEFINITIONS,
    MANIPULATION_TECHNIQUES,
    TECHNIQUE_CATEGORIES as MANIPULATION_CATEGORIES,
    get_manipulation_toolkit_summary
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/rhetorical", response_model=AnalysisResult)
async def analyze_rhetoric(request: AnalysisRequest) -> AnalysisResult:
    """
    Analyze a transcript for rhetorical techniques.

    This endpoint uses AI (GPT-4) to identify rhetorical techniques,
    score the four pillars of rhetoric (Logos, Pathos, Ethos, Kairos),
    and optionally verify potential quotes via web search.

    Args:
        request: AnalysisRequest containing:
            - transcript: The full text to analyze
            - transcript_data: Optional list of segments with timestamps
            - verify_quotes: Whether to verify quotes via web search (default: True)
            - video_title: Optional title for context
            - video_author: Optional author/speaker for context

    Returns:
        AnalysisResult with complete rhetorical analysis including:
            - Overall score and grade
            - Pillar scores (Logos, Pathos, Ethos, Kairos)
            - All detected techniques with explanations
            - Quote attributions (verified if requested)
            - Executive summary and recommendations
    """
    if not request.transcript or len(request.transcript.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Transcript must be at least 50 characters long for meaningful analysis"
        )

    analysis_service = get_analysis_service()

    try:
        result = await analysis_service.analyze_transcript(request)
        return result

    except ValueError as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/manipulation", response_model=ManipulationAnalysisResult)
async def analyze_manipulation(request: ManipulationAnalysisRequest) -> ManipulationAnalysisResult:
    """
    Analyze a transcript for manipulation techniques using the 5-dimension framework.

    This endpoint provides enhanced analysis with:
    - 5 Dimensions: Epistemic Integrity, Argument Quality, Manipulation Risk,
      Rhetorical Craft, and Fairness/Balance
    - Claim Detection: Identifies factual, causal, normative, prediction, and
      prescriptive claims
    - Claim Verification: Optionally fact-checks claims via web search
    - Technique Detection: Identifies 34 manipulation techniques across language,
      reasoning, and propaganda categories

    Args:
        request: ManipulationAnalysisRequest containing:
            - transcript: The full text to analyze
            - transcript_data: Optional list of segments with timestamps
            - analysis_mode: "quick" (~15s single call) or "deep" (~60s multi-pass)
            - verify_claims: Whether to verify factual claims via web search
            - verify_quotes: Whether to verify quote attributions
            - video_title: Optional title for context
            - video_author: Optional author/speaker for context

    Returns:
        ManipulationAnalysisResult with complete 5-dimension analysis including:
            - Overall score and grade
            - Dimension scores with explanations
            - Detected claims with verification status
            - Manipulation technique annotations
            - Executive summary with dual interpretations
    """
    if not request.transcript or len(request.transcript.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Transcript must be at least 50 characters long for meaningful analysis"
        )

    pipeline = get_manipulation_pipeline()

    if not pipeline.is_available():
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key not configured. Manipulation analysis requires OpenAI."
        )

    try:
        result = await pipeline.analyze(request)
        return result

    except ValueError as e:
        logger.error(f"Manipulation analysis error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error during manipulation analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Manipulation analysis failed: {str(e)}"
        )


@router.get("/status")
async def get_analysis_status():
    """
    Check the status of analysis services.

    Returns:
        Dictionary with service availability status
    """
    analysis_service = get_analysis_service()
    status = await analysis_service.check_services()

    return {
        "status": "ready" if status["ready"] else "unavailable",
        "services": status,
        "message": (
            "All services are available"
            if status["ready"]
            else "OpenAI API is required for analysis"
        )
    }


@router.get("/toolkit")
async def get_toolkit_reference():
    """
    Get the complete rhetorical toolkit reference.

    Returns all techniques, pillars, and categories that the
    analysis engine looks for.
    """
    return {
        "pillars": RHETORICAL_PILLARS,
        "techniques": RHETORICAL_TECHNIQUES,
        "categories": TECHNIQUE_CATEGORIES,
        "total_techniques": len(RHETORICAL_TECHNIQUES),
        "total_categories": len(TECHNIQUE_CATEGORIES)
    }


@router.get("/toolkit/summary")
async def get_toolkit_summary_text():
    """
    Get a text summary of the rhetorical toolkit.

    Useful for understanding what the analysis looks for
    without the full structured data.
    """
    return {
        "summary": get_toolkit_summary()
    }


@router.get("/techniques/{technique_id}")
async def get_technique_details(technique_id: str):
    """
    Get details about a specific rhetorical technique.

    Args:
        technique_id: The ID of the technique (e.g., "anaphora", "chiasmus")

    Returns:
        Full details about the technique including examples
    """
    if technique_id not in RHETORICAL_TECHNIQUES:
        raise HTTPException(
            status_code=404,
            detail=f"Technique '{technique_id}' not found. Use /api/analysis/toolkit to see all techniques."
        )

    return RHETORICAL_TECHNIQUES[technique_id]


@router.get("/pillars/{pillar_id}")
async def get_pillar_details(pillar_id: str):
    """
    Get details about a specific rhetorical pillar.

    Args:
        pillar_id: The ID of the pillar (logos, pathos, ethos, kairos)

    Returns:
        Full details about the pillar
    """
    if pillar_id not in RHETORICAL_PILLARS:
        raise HTTPException(
            status_code=404,
            detail=f"Pillar '{pillar_id}' not found. Valid pillars: logos, pathos, ethos, kairos"
        )

    return RHETORICAL_PILLARS[pillar_id]


# =========================================================================
# MANIPULATION ANALYSIS ENDPOINTS (v2.0)
# =========================================================================

@router.get("/manipulation/toolkit")
async def get_manipulation_toolkit_reference():
    """
    Get the complete manipulation analysis toolkit reference.

    Returns all dimensions, techniques, and categories that the
    manipulation analysis engine uses.
    """
    return {
        "dimensions": DIMENSION_DEFINITIONS,
        "techniques": MANIPULATION_TECHNIQUES,
        "categories": MANIPULATION_CATEGORIES,
        "total_techniques": len(MANIPULATION_TECHNIQUES),
        "total_dimensions": len(DIMENSION_DEFINITIONS)
    }


@router.get("/manipulation/toolkit/summary")
async def get_manipulation_toolkit_summary_text():
    """
    Get a text summary of the manipulation analysis toolkit.

    Useful for understanding what the analysis looks for
    without the full structured data.
    """
    return {
        "summary": get_manipulation_toolkit_summary()
    }


@router.get("/manipulation/dimensions/{dimension_id}")
async def get_dimension_details(dimension_id: str):
    """
    Get details about a specific analysis dimension.

    Args:
        dimension_id: The ID of the dimension (e.g., "epistemic_integrity")

    Returns:
        Full details about the dimension
    """
    if dimension_id not in DIMENSION_DEFINITIONS:
        raise HTTPException(
            status_code=404,
            detail=f"Dimension '{dimension_id}' not found. Use /api/analysis/manipulation/toolkit to see all dimensions."
        )

    return DIMENSION_DEFINITIONS[dimension_id]


@router.get("/manipulation/techniques/{technique_id}")
async def get_manipulation_technique_details(technique_id: str):
    """
    Get details about a specific manipulation technique.

    Args:
        technique_id: The ID of the technique (e.g., "strawman", "fear_salvation")

    Returns:
        Full details about the technique including examples
    """
    if technique_id not in MANIPULATION_TECHNIQUES:
        raise HTTPException(
            status_code=404,
            detail=f"Technique '{technique_id}' not found. Use /api/analysis/manipulation/toolkit to see all techniques."
        )

    return MANIPULATION_TECHNIQUES[technique_id]


# =========================================================================
# CONTENT SUMMARY ENDPOINTS (v3.0)
# =========================================================================

@router.post("/summary", response_model=ContentSummaryResult)
async def analyze_summary(request: ContentSummaryRequest) -> ContentSummaryResult:
    """
    Generate a content summary with key concepts, TLDR, and actionable takeaways.

    This is a fast (~10 second) analysis optimized for note-taking and knowledge
    management. Ideal for exporting to Obsidian or other note-taking apps.

    Features:
    - Content Type Detection: Identifies if content is programming, tutorial,
      news, educational, entertainment, etc.
    - TLDR: 2-3 sentence summary
    - Key Concepts: Main ideas with brief explanations
    - Technical Details: For programming content, extracts code, libraries, commands
    - Action Items: Practical takeaways with priority levels
    - Keywords/Tags: For organization (Obsidian-compatible)
    - Key Moments: Important timestamps for quick navigation

    Args:
        request: ContentSummaryRequest containing:
            - transcript: The full text to analyze
            - transcript_data: Optional list of segments with timestamps
            - video_title: Optional title for context
            - video_author: Optional author/speaker for context
            - video_id: Optional YouTube video ID
            - video_url: Optional full URL for export linking

    Returns:
        ContentSummaryResult with complete content summary including:
            - Detected content type with confidence
            - TLDR summary
            - Key concepts with explanations
            - Technical details (if applicable)
            - Action items with priorities
            - Keywords and Obsidian tags
            - Key moments with timestamps
    """
    if not request.transcript or len(request.transcript.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Transcript must be at least 50 characters long for meaningful analysis"
        )

    service = get_summary_service()

    if not service.is_available():
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key not configured. Content summary requires OpenAI."
        )

    try:
        result = await service.analyze(request)
        return result

    except ValueError as e:
        logger.error(f"Content summary error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error during content summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Content summary failed: {str(e)}"
        )


# =========================================================================
# DISCOVERY MODE ENDPOINTS (v4.0 - Kinoshita Pattern)
# =========================================================================

@router.post("/discovery", response_model=DiscoveryResult)
async def analyze_discovery(request: DiscoveryRequest) -> DiscoveryResult:
    """
    Perform Discovery Mode analysis using the Kinoshita Pattern.

    This analysis extracts cross-domain knowledge transfer opportunities
    inspired by how Hiroo Kinoshita discovered EUV lithography by reading
    papers from other fields.

    Features:
    - Problem Extraction: Identifies problems, goals, and blockers
    - Technique Identification: Extracts methods, principles, and mechanisms
    - Cross-Domain Applications: Generates hypotheses for applying techniques elsewhere
    - Research Trail: Captures references and sources mentioned
    - Experiment Ideas: Concrete next steps for exploration

    Accepts content from multiple sources:
    - YouTube URLs (extracts transcript)
    - Web URLs (extracts article content)
    - PDF files (extracts text)
    - Plain text (direct analysis)
    - Cached video_id (uses existing transcript)

    Args:
        request: DiscoveryRequest containing:
            - source: URL, file path, or raw text (optional if video_id provided)
            - source_type: Content type (auto-detected if not provided)
            - video_id: For cached YouTube content
            - focus_domains: Optional domains to prioritize for suggestions
            - max_applications: Maximum cross-domain applications (1-10)

    Returns:
        DiscoveryResult with complete Kinoshita Pattern analysis including:
            - Problems with blockers and context
            - Techniques with principles and requirements
            - Cross-domain applications with confidence scores
            - Research references
            - Key insights, recommended reads, and experiment ideas
    """
    discovery_service = DiscoveryService()

    if not discovery_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key not configured. Discovery analysis requires OpenAI."
        )

    # Get content - either from source or cached video
    content: UnifiedContent

    if request.video_id:
        # Load from cache
        cache_service = CacheService()
        cached = cache_service.get_transcript(request.video_id)

        if not cached:
            raise HTTPException(
                status_code=404,
                detail=f"Video {request.video_id} not found in cache"
            )

        # Build UnifiedContent from cached data
        from app.models.content import ContentSourceType, ContentSegment

        transcript_text = cached.get("cleaned_transcript") or cached.get("transcript", "")
        if not transcript_text:
            raise HTTPException(
                status_code=400,
                detail=f"No transcript available for video {request.video_id}"
            )

        content = UnifiedContent(
            text=transcript_text,
            source_type=ContentSourceType.YOUTUBE,
            source_id=request.video_id,
            source_url=f"https://youtube.com/watch?v={request.video_id}",
            title=cached.get("title", f"Video {request.video_id}"),
            author=cached.get("author"),
            word_count=len(transcript_text.split()),
            character_count=len(transcript_text)
        )

    elif request.source:
        # Extract from provided source
        try:
            content = await extract_content(
                source=request.source,
                source_type=request.source_type
            )

            if not content.extraction_success:
                raise HTTPException(
                    status_code=400,
                    detail=f"Content extraction failed: {content.extraction_error}"
                )

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    else:
        raise HTTPException(
            status_code=400,
            detail="Either 'source' or 'video_id' must be provided"
        )

    # Validate content length
    if content.word_count < 50:
        raise HTTPException(
            status_code=400,
            detail="Content must be at least 50 words for meaningful analysis"
        )

    # Perform discovery analysis
    try:
        result = await discovery_service.analyze(
            content=content,
            focus_domains=request.focus_domains,
            max_applications=request.max_applications
        )

        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Discovery analysis failed")
            )

        discovery_result = result["result"]

        # Save to cache if this was a YouTube video
        if request.video_id:
            cache_service = CacheService()
            # Convert DiscoveryResult to dict for storage
            result_dict = discovery_result.model_dump() if hasattr(discovery_result, 'model_dump') else discovery_result.dict()
            cache_service.save_discovery(request.video_id, result_dict)
            logger.info(f"Saved discovery result for video {request.video_id}")

        return discovery_result

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Unexpected error during discovery analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Discovery analysis failed: {str(e)}"
        )
