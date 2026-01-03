"""
Cache Router

API endpoints for transcript caching and history.
"""

import logging
from typing import Optional, Any, Dict, List
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
        # Rhetorical analysis (v1.0 - 4 pillars)
        "analysis_result": result.get("analysis_result"),
        "analysis_date": result.get("analysis_date"),
        "has_analysis": result.get("analysis_result") is not None,
        # Manipulation/Trust analysis (v2.0 - 5 dimensions)
        "manipulation_result": result.get("manipulation_result"),
        "manipulation_date": result.get("manipulation_date"),
        "has_manipulation": result.get("manipulation_result") is not None,
        # Content summary
        "summary_result": result.get("summary_result"),
        "summary_date": result.get("summary_date"),
        "has_summary": result.get("summary_result") is not None,
        # Discovery analysis (Kinoshita Pattern)
        "discovery_result": result.get("discovery_result"),
        "discovery_date": result.get("discovery_date"),
        "has_discovery": result.get("discovery_result") is not None,
        # Health observation analysis
        "health_observation_result": result.get("health_observation_result"),
        "health_observation_date": result.get("health_observation_date"),
        "has_health": result.get("health_observation_result") is not None,
        # Prompt generator results
        "prompts_result": result.get("prompts_result"),
        "prompts_date": result.get("prompts_date"),
        "has_prompts": result.get("prompts_result") is not None
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


@router.post("/manipulation")
async def save_manipulation(request: SaveManipulationRequest):
    """
    Save manipulation/trust analysis results for a video.

    The video must already exist in the cache (transcript must be saved first).
    This is separate from rhetorical analysis to allow both to coexist.
    """
    cache = get_cache_service()
    success = cache.save_manipulation(request.video_id, request.manipulation_result)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Transcript not found in cache. Save the transcript first."
        )

    return {"saved": True, "video_id": request.video_id}


@router.get("/manipulation/{video_id}")
async def get_cached_manipulation(video_id: str):
    """
    Get cached manipulation/trust analysis for a video.
    """
    cache = get_cache_service()
    result = cache.get_manipulation(video_id)

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
    order_by: str = Query("last_accessed", regex="^(last_accessed|created_at|title)$")
):
    """
    Advanced search with full-text search and faceted filtering.

    - **q**: Search query (searches title, transcript, tags)
    - **content_type**: Filter by content type(s) like 'programming_technical', 'educational'
    - **has_summary**: Filter by whether video has a summary
    - **has_analysis**: Filter by whether video has been analyzed
    - **tags**: Filter by specific tags (all must match)
    - **order_by**: Sort order - 'last_accessed', 'created_at', or 'title'
    """
    cache = get_cache_service()
    items = cache.advanced_search(
        query=q,
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
    limit: int = Query(100, ge=1, le=500)
):
    """
    Get all unique tags with their counts for faceted search.

    Returns tags sorted by frequency (most used first).
    """
    cache = get_cache_service()
    tags = cache.get_all_tags(limit=limit)
    return {"tags": tags}


@router.get("/content-types")
async def get_content_types():
    """
    Get content type distribution.

    Returns count of videos per content type.
    """
    cache = get_cache_service()
    counts = cache.get_content_type_counts()
    return {"content_types": counts}


@router.get("/library/stats")
async def get_library_stats():
    """
    Get library statistics including total videos, summarized, and analyzed counts.
    """
    cache = get_cache_service()
    stats = cache.get_stats()

    return {
        "total": stats["total"],
        "with_summary": stats["with_summary"],
        "with_analysis": stats["with_analysis"],
        "with_trust": stats.get("with_trust", 0),
        "with_discovery": stats.get("with_discovery", 0)
    }


@router.post("/discovery")
async def save_discovery(request: SaveDiscoveryRequest):
    """
    Save discovery (Kinoshita Pattern) analysis results for a video.

    The video must already exist in the cache (transcript must be saved first).
    """
    cache = get_cache_service()
    success = cache.save_discovery(request.video_id, request.discovery_result)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Transcript not found in cache. Save the transcript first."
        )

    return {"saved": True, "video_id": request.video_id}


@router.get("/discovery/{video_id}")
async def get_cached_discovery(video_id: str):
    """
    Get cached discovery (Kinoshita Pattern) analysis for a video.
    """
    cache = get_cache_service()
    result = cache.get_discovery(video_id)

    if not result:
        raise HTTPException(status_code=404, detail="Discovery analysis not found in cache")

    return {
        "video_id": video_id,
        "discovery": result["discovery"],
        "discovery_date": result["discovery_date"],
        "cached": True
    }


@router.post("/fts/rebuild")
async def rebuild_fts_index():
    """
    Manually rebuild the full-text search index.

    Use this if search results seem incomplete or after data migration.
    """
    cache = get_cache_service()
    cache.rebuild_fts_index()
    return {"status": "success", "message": "FTS index rebuilt"}


@router.post("/prompts")
async def save_prompts(request: SavePromptsRequest):
    """
    Save prompt generator results for a video.

    The video must already exist in the cache (transcript must be saved first).
    """
    cache = get_cache_service()
    success = cache.save_prompts(request.video_id, request.prompts_result)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Transcript not found in cache. Save the transcript first."
        )

    return {"saved": True, "video_id": request.video_id}


@router.get("/prompts/{video_id}")
async def get_cached_prompts(video_id: str):
    """
    Get cached prompt generator results for a video.
    """
    cache = get_cache_service()
    result = cache.get_prompts(video_id)

    if not result:
        raise HTTPException(status_code=404, detail="Prompts not found in cache")

    return {
        "video_id": video_id,
        "prompts": result,
        "prompts_date": result.get("prompts_date"),
        "cached": True
    }
