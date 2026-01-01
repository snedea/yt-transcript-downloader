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
from app.services.rhetorical_analysis import get_analysis_service
from app.services.manipulation_pipeline import get_manipulation_pipeline
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
