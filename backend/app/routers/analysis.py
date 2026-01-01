"""
Analysis Router

API endpoints for rhetorical analysis of transcripts.
"""

import logging
from fastapi import APIRouter, HTTPException

from app.models.analysis import AnalysisRequest, AnalysisResult, AnalysisError
from app.services.rhetorical_analysis import get_analysis_service
from app.data.rhetorical_toolkit import (
    RHETORICAL_TECHNIQUES,
    RHETORICAL_PILLARS,
    TECHNIQUE_CATEGORIES,
    get_toolkit_summary
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
