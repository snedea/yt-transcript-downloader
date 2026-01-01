"""
Cache Router

API endpoints for transcript caching and history.
"""

import logging
from typing import Optional, Any, Dict
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.cache_service import get_cache_service
from app.models.cache import TranscriptHistoryResponse, TranscriptHistoryItem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cache", tags=["cache"])


class SaveAnalysisRequest(BaseModel):
    video_id: str
    analysis_result: Dict[str, Any]


class SaveSummaryRequest(BaseModel):
    video_id: str
    summary_result: Dict[str, Any]


@router.get("/transcript/{video_id}")
async def get_cached_transcript(video_id: str):
    """
    Get a cached transcript by video ID.

    Returns the full transcript if cached, or 404 if not found.
    Includes cached analysis if available.
    """
    cache = get_cache_service()
    result = cache.get(video_id)

    if not result:
        raise HTTPException(status_code=404, detail="Transcript not found in cache")

    return {
        "cached": True,
        "video_id": result["video_id"],
        "video_title": result["video_title"],
        "author": result.get("author"),
        "upload_date": result.get("upload_date"),
        "transcript": result["transcript"],
        "transcript_data": result.get("transcript_data"),
        "tokens_used": result.get("tokens_used", 0),
        "is_cleaned": result.get("is_cleaned", False),
        "created_at": result["created_at"],
        "last_accessed": result["last_accessed"],
        "access_count": result["access_count"],
        "analysis_result": result.get("analysis_result"),
        "analysis_date": result.get("analysis_date"),
        "has_analysis": result.get("analysis_result") is not None,
        "summary_result": result.get("summary_result"),
        "summary_date": result.get("summary_date"),
        "has_summary": result.get("summary_result") is not None
    }


@router.get("/history", response_model=TranscriptHistoryResponse)
async def get_transcript_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """
    Get transcript download history.

    Returns a list of previously downloaded transcripts, ordered by last accessed.
    """
    cache = get_cache_service()
    items = cache.get_history(limit=limit, offset=offset)
    total = cache.get_total_count()

    return TranscriptHistoryResponse(
        items=[TranscriptHistoryItem(**item) for item in items],
        total=total
    )


@router.get("/search")
async def search_transcripts(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Search cached transcripts by title or content.
    """
    cache = get_cache_service()
    items = cache.search(query=q, limit=limit)

    return {
        "query": q,
        "results": items,
        "count": len(items)
    }


@router.delete("/transcript/{video_id}")
async def delete_cached_transcript(video_id: str):
    """
    Delete a cached transcript.
    """
    cache = get_cache_service()
    success = cache.delete(video_id)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete transcript")

    return {"deleted": True, "video_id": video_id}


@router.delete("/all")
async def clear_cache():
    """
    Clear all cached transcripts.

    Warning: This cannot be undone!
    """
    cache = get_cache_service()
    success = cache.clear_all()

    if not success:
        raise HTTPException(status_code=500, detail="Failed to clear cache")

    return {"cleared": True}


@router.get("/stats")
async def get_cache_stats():
    """
    Get cache statistics.
    """
    cache = get_cache_service()
    total = cache.get_total_count()

    return {
        "total_transcripts": total,
        "storage_path": str(cache.db_path)
    }


@router.post("/analysis")
async def save_analysis(request: SaveAnalysisRequest):
    """
    Save rhetorical analysis results for a video.

    The video must already exist in the cache (transcript must be saved first).
    """
    cache = get_cache_service()
    success = cache.save_analysis(request.video_id, request.analysis_result)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Transcript not found in cache. Save the transcript first."
        )

    return {"saved": True, "video_id": request.video_id}


@router.get("/analysis/{video_id}")
async def get_cached_analysis(video_id: str):
    """
    Get cached rhetorical analysis for a video.
    """
    cache = get_cache_service()
    result = cache.get_analysis(video_id)

    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found in cache")

    return {
        "video_id": video_id,
        "analysis": result["analysis"],
        "analysis_date": result["analysis_date"],
        "cached": True
    }


@router.post("/summary")
async def save_summary(request: SaveSummaryRequest):
    """
    Save content summary results for a video.

    The video must already exist in the cache (transcript must be saved first).
    """
    cache = get_cache_service()
    success = cache.save_summary(request.video_id, request.summary_result)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Transcript not found in cache. Save the transcript first."
        )

    return {"saved": True, "video_id": request.video_id}


@router.get("/summary/{video_id}")
async def get_cached_summary(video_id: str):
    """
    Get cached content summary for a video.
    """
    cache = get_cache_service()
    result = cache.get_summary(video_id)

    if not result:
        raise HTTPException(status_code=404, detail="Summary not found in cache")

    return {
        "video_id": video_id,
        "summary": result["summary"],
        "summary_date": result["summary_date"],
        "cached": True
    }
