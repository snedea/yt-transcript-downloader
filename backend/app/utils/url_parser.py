"""YouTube URL parsing utilities"""
import re
from typing import Dict, Literal


def extract_video_id(url: str) -> str:
    """
    Extract video ID from various YouTube URL formats
    
    Supported formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    
    Args:
        url: YouTube video URL
        
    Returns:
        Video ID string
        
    Raises:
        ValueError: If URL format is invalid or video ID cannot be extracted
    """
    # Pattern for youtube.com/watch?v=ID format
    watch_pattern = r'(?:youtube\.com|m\.youtube\.com)/watch\?v=([a-zA-Z0-9_-]{11})'
    # Pattern for youtu.be/ID format
    short_pattern = r'youtu\.be/([a-zA-Z0-9_-]{11})'
    
    match = re.search(watch_pattern, url) or re.search(short_pattern, url)
    
    if match:
        return match.group(1)
    
    raise ValueError(f"Could not extract video ID from URL: {url}")


def extract_playlist_id(url: str) -> str:
    """
    Extract playlist ID from YouTube playlist URL
    
    Supported formats:
    - https://www.youtube.com/playlist?list=PLAYLIST_ID
    - https://youtube.com/playlist?list=PLAYLIST_ID
    
    Args:
        url: YouTube playlist URL
        
    Returns:
        Playlist ID string
        
    Raises:
        ValueError: If URL format is invalid or playlist ID cannot be extracted
    """
    pattern = r'[?&]list=([a-zA-Z0-9_-]+)'
    match = re.search(pattern, url)
    
    if match:
        return match.group(1)
    
    raise ValueError(f"Could not extract playlist ID from URL: {url}")


def parse_youtube_url(url: str) -> Dict[str, str]:
    """
    Parse YouTube URL and determine its type (video, playlist, or channel)
    
    Args:
        url: YouTube URL
        
    Returns:
        Dictionary with 'type' and 'id' keys
        
    Raises:
        ValueError: If URL format is invalid
    """
    # Check for playlist
    if 'list=' in url:
        return {
            'type': 'playlist',
            'id': extract_playlist_id(url)
        }
    
    # Check for channel (e.g., youtube.com/@username or youtube.com/channel/ID)
    channel_pattern = r'youtube\.com/(?:@([a-zA-Z0-9_-]+)|channel/([a-zA-Z0-9_-]+))'
    channel_match = re.search(channel_pattern, url)
    if channel_match:
        channel_id = channel_match.group(1) or channel_match.group(2)
        return {
            'type': 'channel',
            'id': channel_id
        }
    
    # Default to video
    try:
        return {
            'type': 'video',
            'id': extract_video_id(url)
        }
    except ValueError:
        raise ValueError(f"Invalid YouTube URL: {url}")
