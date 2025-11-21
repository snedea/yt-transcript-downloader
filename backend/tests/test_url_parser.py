"""Tests for URL parsing utilities"""
import pytest
from app.utils.url_parser import extract_video_id, extract_playlist_id, parse_youtube_url


class TestExtractVideoId:
    """Tests for extract_video_id function"""
    
    def test_extract_from_watch_url(self):
        """Test extraction from youtube.com/watch?v=ID format"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_extract_from_short_url(self):
        """Test extraction from youtu.be/ID format"""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_extract_from_mobile_url(self):
        """Test extraction from mobile URL"""
        url = "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_invalid_url_raises_error(self):
        """Test that invalid URL raises ValueError"""
        url = "https://example.com/video"
        with pytest.raises(ValueError):
            extract_video_id(url)


class TestExtractPlaylistId:
    """Tests for extract_playlist_id function"""
    
    def test_extract_from_playlist_url(self):
        """Test extraction from playlist URL"""
        url = "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        result = extract_playlist_id(url)
        assert result == "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
    
    def test_invalid_url_raises_error(self):
        """Test that invalid URL raises ValueError"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        with pytest.raises(ValueError):
            extract_playlist_id(url)


class TestParseYoutubeUrl:
    """Tests for parse_youtube_url function"""
    
    def test_parse_video_url(self):
        """Test parsing video URL"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = parse_youtube_url(url)
        assert result["type"] == "video"
        assert result["id"] == "dQw4w9WgXcQ"
    
    def test_parse_playlist_url(self):
        """Test parsing playlist URL"""
        url = "https://www.youtube.com/playlist?list=PLtest123"
        result = parse_youtube_url(url)
        assert result["type"] == "playlist"
        assert result["id"] == "PLtest123"
    
    def test_parse_channel_url_with_at_symbol(self):
        """Test parsing channel URL with @ symbol"""
        url = "https://www.youtube.com/@channelname"
        result = parse_youtube_url(url)
        assert result["type"] == "channel"
        assert result["id"] == "channelname"
    
    def test_parse_channel_url_with_channel_id(self):
        """Test parsing channel URL with channel ID"""
        url = "https://www.youtube.com/channel/UCtest123"
        result = parse_youtube_url(url)
        assert result["type"] == "channel"
        assert result["id"] == "UCtest123"
    
    def test_invalid_url_raises_error(self):
        """Test that invalid URL raises ValueError"""
        url = "https://example.com/video"
        with pytest.raises(ValueError):
            parse_youtube_url(url)
