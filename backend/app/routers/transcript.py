"""Transcript API endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import asyncio
from app.services.youtube import YouTubeService
from app.services.openai_service import OpenAIService
from app.utils.url_parser import extract_video_id

router = APIRouter()

# Initialize services
youtube_service = YouTubeService()
openai_service = OpenAIService()


# Request/Response Models
class TranscriptRequest(BaseModel):
    video_url: str
    clean: bool = False


class TranscriptResponse(BaseModel):
    transcript: str
    video_title: str
    video_id: str
    tokens_used: Optional[int] = None


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
    transcript: Optional[str] = None
    error: Optional[str] = None
    tokens_used: Optional[int] = None


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
        request: Contains video_url and optional clean flag
        
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
    
    # Fetch transcript
    result = await youtube_service.get_transcript(video_id)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    transcript_text = result["text"]
    tokens_used = None
    
    # Clean transcript if requested
    if request.clean:
        clean_result = await openai_service.clean_transcript(transcript_text)
        if clean_result["success"]:
            transcript_text = clean_result["cleaned_transcript"]
            tokens_used = clean_result["tokens_used"]
        else:
            # Don't fail entire request if cleaning fails, just log warning
            print(f"Warning: Transcript cleaning failed: {clean_result['error']}")
    
    # Get video title (fallback to video ID)
    video_title = await youtube_service.get_video_title(video_id)
    
    return TranscriptResponse(
        transcript=transcript_text,
        video_title=video_title,
        video_id=video_id,
        tokens_used=tokens_used
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
    
    # Semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(5)
    
    async def fetch_single(video_id: str) -> TranscriptResult:
        """Fetch transcript for a single video with semaphore"""
        async with semaphore:
            # Fetch transcript
            result = await youtube_service.get_transcript(video_id)
            
            if not result["success"]:
                return TranscriptResult(
                    video_id=video_id,
                    title=video_id,
                    error=result["error"]
                )
            
            transcript_text = result["text"]
            tokens_used = None
            
            # Clean if requested
            if request.clean:
                clean_result = await openai_service.clean_transcript(transcript_text)
                if clean_result["success"]:
                    transcript_text = clean_result["cleaned_transcript"]
                    tokens_used = clean_result["tokens_used"]
            
            # Get title
            title = await youtube_service.get_video_title(video_id)
            
            return TranscriptResult(
                video_id=video_id,
                title=title,
                transcript=transcript_text,
                tokens_used=tokens_used
            )
    
    # Fetch all transcripts concurrently
    results = await asyncio.gather(
        *[fetch_single(vid) for vid in request.video_ids],
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
