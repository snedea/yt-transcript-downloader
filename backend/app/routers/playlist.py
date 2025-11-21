"""Playlist API endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.playlist import PlaylistService

router = APIRouter()

# Initialize service
playlist_service = PlaylistService()


# Request/Response Models
class PlaylistRequest(BaseModel):
    playlist_url: str


class Video(BaseModel):
    id: str
    title: str
    thumbnail: str
    duration: int


class PlaylistResponse(BaseModel):
    videos: List[Video]


@router.post("/videos", response_model=PlaylistResponse)
async def get_playlist_videos(request: PlaylistRequest):
    """
    Extract video list from YouTube playlist or channel
    
    Args:
        request: Contains playlist_url
        
    Returns:
        List of videos with metadata
        
    Raises:
        HTTPException: If playlist is invalid or unavailable
    """
    if not request.playlist_url:
        raise HTTPException(status_code=400, detail="playlist_url is required")
    
    result = await playlist_service.get_playlist_videos(request.playlist_url)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return PlaylistResponse(videos=result["videos"])
