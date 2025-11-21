"""YouTube transcript fetching service"""
from typing import Dict, List
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    RequestBlocked,
    HTTPError,
    YouTubeRequestFailed
)


class YouTubeService:
    """Service for fetching YouTube video transcripts"""
    
    def __init__(self):
        """Initialize YouTube transcript API"""
        self.api = YouTubeTranscriptApi()
    
    async def get_transcript(self, video_id: str) -> Dict:
        """
        Fetch transcript for a YouTube video using instance-based API

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary with success status, transcript data, and full text
            Format: {
                "success": bool,
                "transcript": List[Dict] (if success),
                "text": str (if success),
                "error": str (if failure)
            }
        """
        try:
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
        except RequestBlocked:
            return {
                "success": False,
                "error": "Request blocked by YouTube. Please try again later."
            }
        except HTTPError as e:
            return {
                "success": False,
                "error": f"HTTP error occurred: {str(e)}"
            }
        except YouTubeRequestFailed as e:
            return {
                "success": False,
                "error": f"YouTube request failed: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    async def get_video_title(self, video_id: str) -> str:
        """
        Get video title (fallback method using video ID)
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Video title or video ID if title unavailable
        """
        # For now, return video ID as title
        # In production, could use yt-dlp or YouTube Data API
        return video_id
