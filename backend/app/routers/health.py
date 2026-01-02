"""
Health Observations Router

API endpoints for health observation analysis of video content.
Extracts frames, detects human presence, and analyzes for observable features.

IMPORTANT: This is an EDUCATIONAL tool only - NOT for medical diagnosis.
"""

import logging
from fastapi import APIRouter, HTTPException

from app.models.health_observation import (
    HealthObservationRequest,
    HealthObservationResult,
    HEALTH_DISCLAIMER
)
from app.services.health_analyzer import get_health_analyzer
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health", tags=["health"])


@router.post("/observations", response_model=HealthObservationResult)
async def analyze_health_observations(
    request: HealthObservationRequest
) -> HealthObservationResult:
    """
    Extract frames from a YouTube video and analyze for observable health features.

    This endpoint:
    1. Downloads the video temporarily
    2. Extracts frames at specified intervals
    3. Filters for frames containing human presence (face, hands, body)
    4. Analyzes each frame with Claude vision for observable features
    5. Cleans up all temporary files
    6. Returns observations with timestamps (no images stored)

    IMPORTANT: This is an EDUCATIONAL tool only - NOT for medical diagnosis.
    All observations should be reviewed by a healthcare professional.

    Args:
        request: HealthObservationRequest containing:
            - video_url: YouTube video URL
            - video_id: Optional video ID (if already known)
            - video_title: Optional title (for context)
            - interval_seconds: Seconds between frame extractions (5-120, default 30)
            - max_frames: Maximum frames to analyze (1-50, default 20)
            - skip_if_cached: Return cached results if available (default True)

    Returns:
        HealthObservationResult with:
            - Observations grouped by body region
            - Timestamp links to video
            - Confidence levels and limitations
            - Mandatory medical disclaimers
    """
    # Extract video ID from URL if not provided
    video_id = request.video_id
    if not video_id and request.video_url:
        video_id = _extract_video_id(request.video_url)

    if not video_id:
        raise HTTPException(
            status_code=400,
            detail="Could not extract video ID from URL. Please provide a valid YouTube URL."
        )

    # Check cache first if requested
    if request.skip_if_cached:
        cache_service = CacheService()
        cached = cache_service.get_health_observation(video_id)
        if cached:
            logger.info(f"Returning cached health observation for {video_id}")
            return HealthObservationResult(**cached)

    # Get the health analyzer
    analyzer = get_health_analyzer()

    if not analyzer.is_available():
        raise HTTPException(
            status_code=503,
            detail="Claude CLI not available. Health observations require Claude CLI to be installed and authenticated."
        )

    try:
        # Perform analysis
        result = await analyzer.analyze_video(
            video_id=video_id,
            video_title=request.video_title or "",
            interval_seconds=request.interval_seconds,
            max_frames=request.max_frames
        )

        # Cache the result
        cache_service = CacheService()
        result_dict = result.model_dump()
        cache_service.save_health_observation(video_id, result_dict)
        logger.info(f"Saved health observation for video {video_id}")

        return result

    except Exception as e:
        logger.error(f"Health observation analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Health observation analysis failed: {str(e)}"
        )


@router.get("/observations/{video_id}", response_model=HealthObservationResult)
async def get_health_observations(video_id: str) -> HealthObservationResult:
    """
    Get cached health observations for a video.

    Args:
        video_id: YouTube video ID

    Returns:
        HealthObservationResult if cached, 404 if not found
    """
    cache_service = CacheService()
    cached = cache_service.get_health_observation(video_id)

    if not cached:
        raise HTTPException(
            status_code=404,
            detail=f"No health observations cached for video {video_id}"
        )

    return HealthObservationResult(**cached)


@router.get("/status")
async def get_health_status():
    """
    Check the status of health observation services.

    Returns:
        Dictionary with service availability status
    """
    analyzer = get_health_analyzer()

    return {
        "status": "ready" if analyzer.is_available() else "unavailable",
        "claude_cli_available": analyzer.is_available(),
        "disclaimer": HEALTH_DISCLAIMER,
        "message": (
            "Health observation analysis is available"
            if analyzer.is_available()
            else "Claude CLI not available. Install with: npm install -g @anthropic-ai/claude-code"
        )
    }


@router.get("/disclaimer")
async def get_disclaimer():
    """
    Get the full health observation disclaimer.

    Returns:
        The complete disclaimer text
    """
    return {
        "disclaimer": HEALTH_DISCLAIMER,
        "version": "1.0",
        "important_notes": [
            "This tool is for EDUCATIONAL purposes only",
            "This is NOT medical advice",
            "AI observations are NOT diagnoses",
            "Always consult a healthcare professional for medical concerns",
            "Observations are limited by video quality, lighting, and angles",
            "False positives and negatives are possible"
        ]
    }


def _extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID from various URL formats."""
    import re

    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None
