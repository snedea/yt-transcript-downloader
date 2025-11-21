"""Tests for Playlist service"""
import pytest
from unittest.mock import Mock, patch
from app.services.playlist import PlaylistService


class TestPlaylistService:
    """Tests for PlaylistService class"""
    
    @pytest.fixture
    def playlist_service(self):
        """Create PlaylistService instance"""
        return PlaylistService()
    
    @pytest.mark.asyncio
    async def test_get_playlist_videos_success(self, playlist_service):
        """Test successful playlist video extraction"""
        # Mock yt-dlp response
        mock_info = {
            'entries': [
                {
                    'id': 'video1',
                    'title': 'Test Video 1',
                    'thumbnail': 'https://example.com/thumb1.jpg',
                    'duration': 120
                },
                {
                    'id': 'video2',
                    'title': 'Test Video 2',
                    'thumbnail': 'https://example.com/thumb2.jpg',
                    'duration': 180
                }
            ]
        }
        
        with patch('yt_dlp.YoutubeDL.extract_info', return_value=mock_info):
            result = await playlist_service.get_playlist_videos("https://youtube.com/playlist?list=test")
            
            assert result["success"] is True
            assert len(result["videos"]) == 2
            assert result["videos"][0]["id"] == "video1"
            assert result["videos"][0]["title"] == "Test Video 1"
    
    @pytest.mark.asyncio
    async def test_get_playlist_videos_empty(self, playlist_service):
        """Test handling of empty playlists"""
        mock_info = {'entries': []}
        
        with patch('yt_dlp.YoutubeDL.extract_info', return_value=mock_info):
            result = await playlist_service.get_playlist_videos("https://youtube.com/playlist?list=test")
            
            assert result["success"] is False
            assert "No videos" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_playlist_videos_private(self, playlist_service):
        """Test handling of private playlists"""
        import yt_dlp
        
        with patch('yt_dlp.YoutubeDL.extract_info', 
                  side_effect=yt_dlp.utils.DownloadError("Private video")):
            result = await playlist_service.get_playlist_videos("https://youtube.com/playlist?list=test")
            
            assert result["success"] is False
            assert "private" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_get_playlist_videos_not_found(self, playlist_service):
        """Test handling of non-existent playlists"""
        import yt_dlp
        
        with patch('yt_dlp.YoutubeDL.extract_info', 
                  side_effect=yt_dlp.utils.DownloadError("Playlist not found")):
            result = await playlist_service.get_playlist_videos("https://youtube.com/playlist?list=test")
            
            assert result["success"] is False
            assert "not found" in result["error"].lower()
