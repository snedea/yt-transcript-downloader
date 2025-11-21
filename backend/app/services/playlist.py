"""YouTube playlist and channel video extraction service"""
from typing import Dict, List
import yt_dlp


class PlaylistService:
    """Service for extracting video lists from playlists and channels"""
    
    def __init__(self):
        """Initialize yt-dlp options"""
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # Don't download, just extract metadata
            'skip_download': True,
        }
    
    async def get_playlist_videos(self, playlist_url: str) -> Dict:
        """
        Extract video list from YouTube playlist or channel
        
        Args:
            playlist_url: YouTube playlist or channel URL
            
        Returns:
            Dictionary with success status and video list
            Format: {
                "success": bool,
                "videos": List[Dict] (if success),
                "error": str (if failure)
            }
            
            Each video dict contains:
            - id: Video ID
            - title: Video title
            - thumbnail: Thumbnail URL
            - duration: Duration in seconds
        """
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Extract playlist info
                info = ydl.extract_info(playlist_url, download=False)
                
                if not info:
                    return {
                        "success": False,
                        "error": "Could not extract playlist information"
                    }
                
                # Get entries (videos)
                entries = info.get('entries', [])
                
                if not entries:
                    return {
                        "success": False,
                        "error": "No videos found in playlist"
                    }
                
                # Format video data
                videos = []
                for entry in entries:
                    if entry:  # Skip None entries (deleted videos)
                        video = {
                            "id": entry.get('id', ''),
                            "title": entry.get('title', 'Unknown Title'),
                            "thumbnail": entry.get('thumbnail', ''),
                            "duration": entry.get('duration', 0)
                        }
                        videos.append(video)
                
                return {
                    "success": True,
                    "videos": videos
                }
                
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if 'Private video' in error_msg:
                return {
                    "success": False,
                    "error": "Playlist is private or unavailable"
                }
            elif 'not found' in error_msg.lower():
                return {
                    "success": False,
                    "error": "Playlist not found"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to extract playlist: {error_msg}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
