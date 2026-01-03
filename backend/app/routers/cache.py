"""
Cache Router

API endpoints for transcript caching and history.
"""

import logging
from typing import Optional, Any, Dict, List
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from sqlmodel import Session

from app.services.cache_service import get_cache_service
from app.models.cache import TranscriptHistoryResponse, TranscriptHistoryItem
from app.db import get_session
from app.dependencies import get_current_user
from app.models.auth import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cache", tags=["cache"])


class SaveAnalysisRequest(BaseModel):
    video_id: str
    analysis_result: Dict[str, Any]


class SaveSummaryRequest(BaseModel):
    video_id: str
    summary_result: Dict[str, Any]


class SaveManipulationRequest(BaseModel):
    video_id: str
    manipulation_result: Dict[str, Any]


class SaveDiscoveryRequest(BaseModel):
    video_id: str
    discovery_result: Dict[str, Any]


class SavePromptsRequest(BaseModel):
    video_id: str
    prompts_result: Dict[str, Any]


@router.get("/transcript/{video_id}")
async def get_cached_transcript(
    video_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get a cached transcript by video ID.
    Returns the full transcript if cached, or 404 if not found.
    """
    cache = get_cache_service()
    result = cache.get(session, video_id, current_user.id)

    if not result:
        raise HTTPException(status_code=404, detail="Transcript not found in cache")

    # Map the dict result to the response structure.
    # The dict from _to_dict includes all fields, including multi-source metadata.
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
        # Multi-source metadata fields
        "source_type": result.get("source_type"),
        "source_url": result.get("source_url"),
        "thumbnail_url": result.get("thumbnail_url"),
        "raw_content_text": result.get("raw_content_text"),
        "word_count": result.get("word_count"),
        "character_count": result.get("character_count"),
        "page_count": result.get("page_count"),
        # Content metadata
        "content_type": result.get("content_type"),
        "keywords": result.get("keywords"),
        "tldr": result.get("tldr"),
        # Analysis results
        "analysis_result": result.get("analysis_result"),
        "analysis_date": result.get("analysis_date"),
        "has_analysis": result.get("analysis_result") is not None,
        "manipulation_result": result.get("manipulation_result"),
        "manipulation_date": result.get("manipulation_date"),
        "has_manipulation": result.get("manipulation_result") is not None,
        "summary_result": result.get("summary_result"),
        "summary_date": result.get("summary_date"),
        "has_summary": result.get("summary_result") is not None,
        "discovery_result": result.get("discovery_result"),
        "discovery_date": result.get("discovery_date"),
        "has_discovery": result.get("discovery_result") is not None,
        "health_observation_result": result.get("health_observation_result"),
        "health_observation_date": result.get("health_observation_date"),
        "has_health": result.get("health_observation_result") is not None,
        "prompts_result": result.get("prompts_result"),
        "prompts_date": result.get("prompts_date"),
        "has_prompts": result.get("prompts_result") is not None
    }


@router.get("/history", response_model=TranscriptHistoryResponse)
async def get_transcript_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get transcript download history.
    """
    cache = get_cache_service()
    items = cache.get_history(session, current_user.id, limit=limit, offset=offset)
    total = cache.get_total_count(session, current_user.id)

    return TranscriptHistoryResponse(
        items=[TranscriptHistoryItem(**item) for item in items],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/search")
async def search_transcripts(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Search cached transcripts by title or content.
    """
    cache = get_cache_service()
    items = cache.search(session, q, current_user.id, limit=limit)

    return {
        "query": q,
        "results": items,
        "count": len(items)
    }


@router.delete("/transcript/{video_id}")
async def delete_cached_transcript(
    video_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a cached transcript.
    """
    cache = get_cache_service()
    success = cache.delete(session, video_id, current_user.id)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete transcript or not found")

    return {"deleted": True, "video_id": video_id}


@router.delete("/all")
async def clear_cache(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Clear all cached transcripts.
    """
    cache = get_cache_service()
    success = cache.clear_all(session, current_user.id)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to clear cache")

    return {"cleared": True}


@router.get("/stats")
async def get_cache_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get cache statistics.
    """
    cache = get_cache_service()
    total = cache.get_total_count(session, current_user.id)

    return {
        "total_transcripts": total,
        # "storage_path": str(cache.db_path) # db_path no longer relevant in service directly
    }


@router.post("/analysis")
async def save_analysis(
    request: SaveAnalysisRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Save rhetorical analysis results for a video.
    """
    cache = get_cache_service()
    success = cache.save_analysis(session, request.video_id, request.analysis_result, current_user.id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Transcript not found in cache. Save the transcript first."
        )

    return {"saved": True, "video_id": request.video_id}


@router.get("/analysis/{video_id}")
async def get_cached_analysis(
    video_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get cached rhetorical analysis for a video.
    """
    cache = get_cache_service()
    result = cache.get_analysis(session, video_id, current_user.id)

    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found in cache")

    return {
        "video_id": video_id,
        "analysis": result["analysis"],
        "analysis_date": result["analysis_date"],
        "cached": True
    }


@router.post("/summary")
async def save_summary(
    request: SaveSummaryRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Save content summary results for a video.
    """
    cache = get_cache_service()
    success = cache.save_summary(session, request.video_id, request.summary_result, current_user.id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Transcript not found in cache. Save the transcript first."
        )

    return {"saved": True, "video_id": request.video_id}


@router.get("/summary/{video_id}")
async def get_cached_summary(
    video_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get cached content summary for a video.
    """
    cache = get_cache_service()
    result = cache.get_summary(session, video_id, current_user.id)

    if not result:
        raise HTTPException(status_code=404, detail="Summary not found in cache")

    return {
        "video_id": video_id,
        "summary": result["summary"],
        "summary_date": result["summary_date"],
        "cached": True
    }


@router.post("/manipulation")
async def save_manipulation(
    request: SaveManipulationRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Save manipulation/trust analysis results.
    """
    cache = get_cache_service()
    success = cache.save_manipulation(session, request.video_id, request.manipulation_result, current_user.id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Transcript not found in cache. Save the transcript first."
        )

    return {"saved": True, "video_id": request.video_id}


@router.get("/manipulation/{video_id}")
async def get_cached_manipulation(
    video_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get cached manipulation/trust analysis.
    """
    cache = get_cache_service()
    result = cache.get_manipulation(session, video_id, current_user.id)

    if not result:
        raise HTTPException(status_code=404, detail="Manipulation analysis not found in cache")

    return {
        "video_id": video_id,
        "manipulation": result["manipulation"],
        "manipulation_date": result["manipulation_date"],
        "cached": True
    }


@router.get("/search/advanced")
async def advanced_search(
    q: str = Query("", description="Full-text search query"),
    content_type: Optional[List[str]] = Query(None, description="Filter by content type(s)"),
    has_summary: Optional[bool] = Query(None, description="Filter by summary status"),
    has_analysis: Optional[bool] = Query(None, description="Filter by analysis status"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags (all must match)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    order_by: str = Query("last_accessed", regex="^(last_accessed|created_at|title)$"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Advanced search with auth.
    """
    cache = get_cache_service()
    items = cache.advanced_search(
        session,
        query=q,
        user_id=current_user.id,
        content_types=content_type,
        has_summary=has_summary,
        has_analysis=has_analysis,
        tags=tags,
        limit=limit,
        offset=offset,
        order_by=order_by
    )

    return {
        "query": q,
        "filters": {
            "content_type": content_type,
            "has_summary": has_summary,
            "has_analysis": has_analysis,
            "tags": tags
        },
        "results": items,
        "count": len(items)
    }


@router.get("/tags")
async def get_all_tags(
    limit: int = Query(100, ge=1, le=500),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get all unique tags for current user.
    """
    cache = get_cache_service()
    tags = cache.get_all_tags(session, limit=limit, user_id=current_user.id)
    return {"tags": tags}


@router.get("/content-types")
async def get_content_types(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get content type distribution for current user.
    """
    cache = get_cache_service()
    counts = cache.get_content_type_counts(session, user_id=current_user.id)
    return {"content_types": counts}


@router.get("/library/stats")
async def get_library_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get library statistics.
    """
    cache = get_cache_service()
    stats = cache.get_stats(session, current_user.id)

    return {
        "total": stats["total"],
        "with_summary": stats["with_summary"],
        "with_analysis": stats["with_analysis"],
        "with_trust": stats.get("with_trust", 0),
        "with_discovery": stats.get("with_discovery", 0)
    }


@router.post("/discovery")
async def save_discovery(
    request: SaveDiscoveryRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Save discovery analysis results.
    """
    cache = get_cache_service()
    success = cache.save_discovery(session, request.video_id, request.discovery_result, current_user.id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Transcript not found in cache. Save the transcript first."
        )

    return {"saved": True, "video_id": request.video_id}


@router.get("/discovery/{video_id}")
async def get_cached_discovery(
    video_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get cached discovery analysis.
    """
    cache = get_cache_service()
    result = cache.get_discovery(session, video_id, current_user.id)

    if not result:
        raise HTTPException(status_code=404, detail="Discovery analysis not found in cache")

    return {
        "video_id": video_id,
        "discovery": result["discovery"],
        "discovery_date": result["discovery_date"],
        "cached": True
    }


@router.post("/fts/rebuild")
async def rebuild_fts_index(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Manually rebuild FTS.
    """
    # Assuming only authorized users allowed? or all?
    cache = get_cache_service()
    cache.rebuild_fts_index()
    return {"status": "success", "message": "FTS index rebuilt (stub)"}


@router.post("/prompts")
async def save_prompts(
    request: SavePromptsRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Save prompt generator results.
    """
    cache = get_cache_service()
    success = cache.save_prompts(session, request.video_id, request.prompts_result, current_user.id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Transcript not found in cache. Save the transcript first."
        )

    return {"saved": True, "video_id": request.video_id}


@router.get("/prompts/{video_id}")
async def get_cached_prompts(
    video_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get cached prompt generator results.
    Returns raw PromptGeneratorResult to match frontend expectations.
    """
    cache = get_cache_service()
    result = cache.get_prompts(session, video_id, current_user.id)

    if not result:
        raise HTTPException(status_code=404, detail="Prompts not found in cache")

    # Return the raw prompts result (PromptGeneratorResult)
    # Frontend expects the result directly, not wrapped
    return result["prompts"]
