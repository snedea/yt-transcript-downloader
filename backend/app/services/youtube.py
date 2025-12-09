"""YouTube transcript fetching service"""
from typing import Dict, List, Optional
import asyncio
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    RequestBlocked,
    HTTPError,
    YouTubeRequestFailed
)
import yt_dlp


class YouTubeService:
    """Service for fetching YouTube video transcripts"""
    
    def __init__(self):
        """Initialize YouTube transcript API"""
        self.api = YouTubeTranscriptApi()
    
    async def get_transcript(self, video_id: str, max_retries: int = 3) -> Dict:
        """
        Fetch transcript for a YouTube video using instance-based API with retry logic

        Args:
            video_id: YouTube video ID
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            Dictionary with success status, transcript data, and full text
            Format: {
                "success": bool,
                "transcript": List[Dict] (if success),
                "text": str (if success),
                "error": str (if failure)
            }
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                # Add delay before retry attempts (exponential backoff)
                if attempt > 0:
                    delay = 2 ** attempt  # 2s, 4s, 8s
                    await asyncio.sleep(delay)

                # CRITICAL: Use instance.fetch(), modern API pattern (v1.2.3+)
                # Returns FetchedTranscript with FetchedTranscriptSnippet objects
                fetched_transcript = self.api.fetch(video_id)

                # Format transcript snippets (iterate over FetchedTranscript)
                transcript = [
                    {
                        "text": snippet.text,
                        "start": snippet.start,
                        "duration": snippet.duration
                    }
                    for snippet in fetched_transcript
                ]

                # Combine into full text
                full_text = " ".join([s["text"] for s in transcript])

                return {
                    "success": True,
                    "transcript": transcript,
                    "text": full_text
                }

            except TranscriptsDisabled:
                return {
                    "success": False,
                    "error": "Transcripts are disabled for this video"
                }
            except NoTranscriptFound:
                return {
                    "success": False,
                    "error": "No transcript found for this video"
                }
            except VideoUnavailable:
                return {
                    "success": False,
                    "error": "Video is unavailable or does not exist"
                }
            except RequestBlocked as e:
                last_error = e
                # Retry on RequestBlocked errors
                if attempt < max_retries - 1:
                    continue
                return {
                    "success": False,
                    "error": "Request blocked by YouTube. Please try again later."
                }
            except HTTPError as e:
                last_error = e
                # Retry on HTTP errors (might be temporary)
                if attempt < max_retries - 1:
                    continue
                return {
                    "success": False,
                    "error": f"HTTP error occurred: {str(e)}"
                }
            except YouTubeRequestFailed as e:
                last_error = e
                # Retry on general request failures
                if attempt < max_retries - 1:
                    continue
                return {
                    "success": False,
                    "error": f"YouTube request failed: {str(e)}"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}"
                }

        # If all retries failed
        return {
            "success": False,
            "error": f"Failed after {max_retries} attempts: {str(last_error)}"
        }
    
    async def get_video_metadata(self, video_id: str) -> Dict:
        """
        Get comprehensive video metadata using yt-dlp
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary with video metadata:
            {
                "title": str,
                "author": str,
                "upload_date": str (YYYYMMDD format),
                "success": bool
            }
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }
            
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                if not info:
                    return {
                        "success": False,
                        "title": video_id,
                        "author": "Unknown",
                        "upload_date": ""
                    }
                
                return {
                    "success": True,
                    "title": info.get('title', video_id),
                    "author": info.get('uploader', info.get('channel', 'Unknown')),
                    "upload_date": info.get('upload_date', '')
                }
                
        except Exception as e:
            # Fallback to video ID if metadata fetch fails
            return {
                "success": False,
                "title": video_id,
                "author": "Unknown",
                "upload_date": ""
            }
    
    async def get_video_title(self, video_id: str) -> str:
        """
        Get video title (wrapper for backward compatibility)
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Video title or video ID if title unavailable
        """
        metadata = await self.get_video_metadata(video_id)
        return metadata.get("title", video_id)

