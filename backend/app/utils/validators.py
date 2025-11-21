"""Input validation utilities"""
from typing import List


def validate_video_ids(video_ids: List[str]) -> bool:
    """
    Validate that video IDs are in correct format
    
    Args:
        video_ids: List of video ID strings
        
    Returns:
        True if all IDs are valid
        
    Raises:
        ValueError: If any ID is invalid
    """
    if not video_ids:
        raise ValueError("video_ids list cannot be empty")
    
    if len(video_ids) > 100:
        raise ValueError("Maximum 100 videos allowed per bulk request")
    
    for video_id in video_ids:
        if not video_id or len(video_id) != 11:
            raise ValueError(f"Invalid video ID format: {video_id}")
    
    return True
