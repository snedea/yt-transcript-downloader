"""Transcript API endpoints"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
from app.services.youtube import YouTubeService
from app.services.openai_service import OpenAIService
from app.services.cache_service import get_cache_service
from app.utils.url_parser import extract_video_id

router = APIRouter()

# Initialize services
youtube_service = YouTubeService()
openai_service = OpenAIService()


# Request/Response Models
class TranscriptRequest(BaseModel):
    video_url: str
    clean: bool = False
    use_cache: bool = True  # Check cache first, default True


class TranscriptResponse(BaseModel):
    transcript: str
    video_title: str
    video_id: str
    author: str = "Unknown"
    upload_date: str = ""
    tokens_used: Optional[int] = None
    transcript_data: Optional[List[Dict[str, Any]]] = None
    cached: bool = False  # Whether this came from cache


class CleanRequest(BaseModel):
    transcript: str


class CleanResponse(BaseModel):
    cleaned_transcript: str
    tokens_used: int


class BulkTranscriptRequest(BaseModel):
    video_ids: List[str]
    clean: bool = False


class TranscriptResult(BaseModel):
    video_id: str
    title: str
    author: str = "Unknown"
    upload_date: str = ""
    transcript: Optional[str] = None
    error: Optional[str] = None
    tokens_used: Optional[int] = None
    transcript_data: Optional[List[Dict[str, Any]]] = None


class BulkTranscriptResponse(BaseModel):
    results: List[TranscriptResult]
    total: int
    successful: int
    failed: int


@router.post("/single", response_model=TranscriptResponse)
async def get_single_transcript(request: TranscriptRequest):
    """
    Fetch transcript for a single YouTube video

    Args:
        request: Contains video_url, optional clean flag, and use_cache flag

    Returns:
        Transcript data with video metadata

    Raises:
        HTTPException: If URL is invalid or transcript unavailable
    """
    try:
        # Extract video ID from URL
        video_id = extract_video_id(request.video_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    cache = get_cache_service()

    # Check cache first if enabled
    if request.use_cache:
        cached = cache.get(video_id)
        if cached:
            # For cached results, check if cleaning was requested but cache has uncleaned
            if request.clean and not cached.get('is_cleaned'):
                # Need to re-fetch and clean
                pass
            else:
                # Return cached result
                return TranscriptResponse(
                    transcript=cached["transcript"],
                    video_title=cached["video_title"],
                    video_id=video_id,
                    author=cached.get("author", "Unknown"),
                    upload_date=cached.get("upload_date", ""),
                    tokens_used=cached.get("tokens_used"),
                    transcript_data=cached.get("transcript_data"),
                    cached=True
                )

    # Fetch transcript from YouTube
    result = await youtube_service.get_transcript(video_id)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])

    transcript_text = result["text"]
    transcript_data = result.get("transcript")
    tokens_used = None
    is_cleaned = False

    # Clean transcript if requested
    if request.clean:
        clean_result = await openai_service.clean_transcript(transcript_text)
        if clean_result["success"]:
            transcript_text = clean_result["cleaned_transcript"]
            tokens_used = clean_result["tokens_used"]
            is_cleaned = True
        else:
            # Don't fail entire request if cleaning fails, just log warning
            print(f"Warning: Transcript cleaning failed: {clean_result['error']}")

    # Get video metadata (title, author, upload date)
    metadata = await youtube_service.get_video_metadata(video_id)
    video_title = metadata.get("title", video_id)
    author = metadata.get("author", "Unknown")
    upload_date = metadata.get("upload_date", "")

    # Save to cache
    cache.save(
        video_id=video_id,
        video_title=video_title,
        transcript=transcript_text,
        author=author,
        upload_date=upload_date,
        transcript_data=transcript_data,
        tokens_used=tokens_used or 0,
        is_cleaned=is_cleaned
    )

    return TranscriptResponse(
        transcript=transcript_text,
        video_title=video_title,
        video_id=video_id,
        author=author,
        upload_date=upload_date,
        tokens_used=tokens_used,
        transcript_data=transcript_data,
        cached=False
    )


@router.post("/clean", response_model=CleanResponse)
async def clean_transcript(request: CleanRequest):
    """
    Clean a transcript using GPT-4o-mini
    
    Args:
        request: Contains raw transcript text
        
    Returns:
        Cleaned transcript with token usage
        
    Raises:
        HTTPException: If cleaning fails
    """
    result = await openai_service.clean_transcript(request.transcript)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return CleanResponse(
        cleaned_transcript=result["cleaned_transcript"],
        tokens_used=result["tokens_used"]
    )


@router.post("/bulk", response_model=BulkTranscriptResponse)
async def get_bulk_transcripts(request: BulkTranscriptRequest):
    """
    Fetch transcripts for multiple videos concurrently
    
    Args:
        request: Contains list of video IDs and optional clean flag
        
    Returns:
        Results for each video with success/failure status
    """
    if not request.video_ids:
        raise HTTPException(status_code=400, detail="video_ids list cannot be empty")
    
    if len(request.video_ids) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 videos allowed")
    
    # Semaphore to limit concurrent requests (only 1 at a time to avoid rate limiting)
    semaphore = asyncio.Semaphore(1)

    async def fetch_single(video_id: str, index: int) -> TranscriptResult:
        """Fetch transcript for a single video with semaphore and delay"""
        async with semaphore:
            # Add aggressive delay between requests to avoid triggering YouTube's anti-spam
            # 2-3 seconds between each request
            if index > 0:
                await asyncio.sleep(2.5)  # Fixed 2.5 second delay between requests

            # Fetch transcript
            result = await youtube_service.get_transcript(video_id)
            
            if not result["success"]:
                return TranscriptResult(
                    video_id=video_id,
                    title=video_id,
                    error=result["error"]
                )
            
            transcript_text = result["text"]
            transcript_data = result.get("transcript")
            tokens_used = None
            
            # Clean if requested
            if request.clean:
                clean_result = await openai_service.clean_transcript(transcript_text)
                if clean_result["success"]:
                    transcript_text = clean_result["cleaned_transcript"]
                    tokens_used = clean_result["tokens_used"]
            
            # Get metadata
            metadata = await youtube_service.get_video_metadata(video_id)
            
            return TranscriptResult(
                video_id=video_id,
                title=metadata.get("title", video_id),
                author=metadata.get("author", "Unknown"),
                upload_date=metadata.get("upload_date", ""),
                transcript=transcript_text,
                tokens_used=tokens_used,
                transcript_data=transcript_data
            )
    
    # Fetch all transcripts concurrently with staggered delays
    results = await asyncio.gather(
        *[fetch_single(vid, idx) for idx, vid in enumerate(request.video_ids)],
        return_exceptions=True
    )
    
    # Process results
    transcript_results = []
    successful = 0
    failed = 0
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            # Handle exceptions
            transcript_results.append(TranscriptResult(
                video_id=request.video_ids[i],
                title=request.video_ids[i],
                error=str(result)
            ))
            failed += 1
        elif result.error:
            transcript_results.append(result)
            failed += 1
        else:
            transcript_results.append(result)
            successful += 1
    
    return BulkTranscriptResponse(
        results=transcript_results,
        total=len(request.video_ids),
        successful=successful,
        failed=failed
    )
