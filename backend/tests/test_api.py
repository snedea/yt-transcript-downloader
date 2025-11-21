"""Integration tests for API endpoints"""
import pytest
from unittest.mock import patch, Mock, MagicMock


class TestTranscriptEndpoints:
    """Tests for /api/transcript endpoints"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_single_transcript_success(self, client):
        """Test successful single transcript fetch"""
        # Mock YouTube service
        mock_result = {
            "success": True,
            "transcript": [{"text": "Hello", "start": 0, "duration": 1}],
            "text": "Hello world"
        }
        
        with patch('app.routers.transcript.youtube_service.get_transcript', return_value=mock_result):
            with patch('app.routers.transcript.youtube_service.get_video_title', return_value="Test Video"):
                response = client.post(
                    "/api/transcript/single",
                    json={"video_url": "https://youtube.com/watch?v=test123", "clean": False}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["transcript"] == "Hello world"
                assert data["video_id"] == "test123"
    
    @pytest.mark.asyncio
    async def test_single_transcript_invalid_url(self, client):
        """Test single transcript with invalid URL"""
        response = client.post(
            "/api/transcript/single",
            json={"video_url": "https://example.com/invalid", "clean": False}
        )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_single_transcript_not_found(self, client):
        """Test single transcript when transcript not available"""
        mock_result = {
            "success": False,
            "error": "No transcript found"
        }
        
        with patch('app.routers.transcript.youtube_service.get_transcript', return_value=mock_result):
            response = client.post(
                "/api/transcript/single",
                json={"video_url": "https://youtube.com/watch?v=test123", "clean": False}
            )
            
            assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_clean_transcript(self, client):
        """Test transcript cleaning endpoint"""
        mock_result = {
            "success": True,
            "cleaned_transcript": "This is a clean transcript.",
            "tokens_used": 100
        }
        
        with patch('app.routers.transcript.openai_service.clean_transcript', return_value=mock_result):
            response = client.post(
                "/api/transcript/clean",
                json={"transcript": "this is a test transcript"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["cleaned_transcript"] == "This is a clean transcript."
            assert data["tokens_used"] == 100
    
    @pytest.mark.asyncio
    async def test_bulk_transcript_success(self, client):
        """Test successful bulk transcript fetch"""
        mock_result = {
            "success": True,
            "transcript": [{"text": "Hello", "start": 0, "duration": 1}],
            "text": "Hello world"
        }
        
        with patch('app.routers.transcript.youtube_service.get_transcript', return_value=mock_result):
            with patch('app.routers.transcript.youtube_service.get_video_title', return_value="Test Video"):
                response = client.post(
                    "/api/transcript/bulk",
                    json={"video_ids": ["test1", "test2"], "clean": False}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["total"] == 2
                assert data["successful"] == 2
                assert data["failed"] == 0
    
    @pytest.mark.asyncio
    async def test_bulk_transcript_empty_list(self, client):
        """Test bulk transcript with empty video list"""
        response = client.post(
            "/api/transcript/bulk",
            json={"video_ids": [], "clean": False}
        )
        
        assert response.status_code == 400


class TestPlaylistEndpoints:
    """Tests for /api/playlist endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_playlist_videos_success(self, client):
        """Test successful playlist video extraction"""
        mock_result = {
            "success": True,
            "videos": [
                {"id": "video1", "title": "Video 1", "thumbnail": "url1", "duration": 120},
                {"id": "video2", "title": "Video 2", "thumbnail": "url2", "duration": 180}
            ]
        }
        
        with patch('app.routers.playlist.playlist_service.get_playlist_videos', return_value=mock_result):
            response = client.post(
                "/api/playlist/videos",
                json={"playlist_url": "https://youtube.com/playlist?list=test"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["videos"]) == 2
            assert data["videos"][0]["id"] == "video1"
    
    @pytest.mark.asyncio
    async def test_get_playlist_videos_not_found(self, client):
        """Test playlist not found error"""
        mock_result = {
            "success": False,
            "error": "Playlist not found"
        }
        
        with patch('app.routers.playlist.playlist_service.get_playlist_videos', return_value=mock_result):
            response = client.post(
                "/api/playlist/videos",
                json={"playlist_url": "https://youtube.com/playlist?list=test"}
            )
            
            assert response.status_code == 404
