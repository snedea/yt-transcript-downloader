"""Tests for YouTube service"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.youtube import YouTubeService


class TestYouTubeService:
    """Tests for YouTubeService class"""
    
    @pytest.fixture
    def youtube_service(self):
        """Create YouTubeService instance"""
        return YouTubeService()
    
    @pytest.mark.asyncio
    async def test_get_transcript_success(self, youtube_service):
        """Test successful transcript fetching"""
        # Mock the API response
        mock_transcript = [
            {"text": "Hello", "start": 0.0, "duration": 1.5},
            {"text": "World", "start": 1.5, "duration": 1.5}
        ]
        
        with patch.object(youtube_service.api, 'get_transcript', return_value=mock_transcript):
            result = await youtube_service.get_transcript("test_video_id")
            
            assert result["success"] is True
            assert len(result["transcript"]) == 2
            assert result["text"] == "Hello World"
            assert result["transcript"][0]["text"] == "Hello"
    
    @pytest.mark.asyncio
    async def test_get_transcript_disabled(self, youtube_service):
        """Test handling of disabled transcripts"""
        from youtube_transcript_api._errors import TranscriptsDisabled
        
        with patch.object(youtube_service.api, 'get_transcript', side_effect=TranscriptsDisabled("test")):
            result = await youtube_service.get_transcript("test_video_id")
            
            assert result["success"] is False
            assert "disabled" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_get_transcript_not_found(self, youtube_service):
        """Test handling of missing transcripts"""
        from youtube_transcript_api._errors import NoTranscriptFound
        
        with patch.object(youtube_service.api, 'get_transcript', side_effect=NoTranscriptFound("test", "test", [])):
            result = await youtube_service.get_transcript("test_video_id")
            
            assert result["success"] is False
            assert "not found" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_get_transcript_video_unavailable(self, youtube_service):
        """Test handling of unavailable videos"""
        from youtube_transcript_api._errors import VideoUnavailable
        
        with patch.object(youtube_service.api, 'get_transcript', side_effect=VideoUnavailable("test")):
            result = await youtube_service.get_transcript("test_video_id")
            
            assert result["success"] is False
            assert "unavailable" in result["error"].lower()
