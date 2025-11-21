"""Tests for OpenAI service"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.openai_service import OpenAIService


class TestOpenAIService:
    """Tests for OpenAIService class"""
    
    @pytest.fixture
    def openai_service(self):
        """Create OpenAIService instance with mocked client"""
        service = OpenAIService()
        # Mock the client
        service.client = Mock()
        return service
    
    @pytest.mark.asyncio
    async def test_clean_transcript_success(self, openai_service, sample_transcript):
        """Test successful transcript cleaning"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello everyone! Welcome to this video."
        mock_response.usage.total_tokens = 150
        
        openai_service.client.chat.completions.create = Mock(return_value=mock_response)
        
        result = await openai_service.clean_transcript(sample_transcript)
        
        assert result["success"] is True
        assert "cleaned_transcript" in result
        assert result["tokens_used"] == 150
    
    @pytest.mark.asyncio
    async def test_clean_transcript_no_client(self):
        """Test error when OpenAI client not configured"""
        service = OpenAIService()
        service.client = None
        
        result = await service.clean_transcript("test transcript")
        
        assert result["success"] is False
        assert "not configured" in result["error"]
    
    @pytest.mark.asyncio
    async def test_clean_transcript_authentication_error(self, openai_service, sample_transcript):
        """Test handling of authentication errors"""
        from openai import AuthenticationError
        
        openai_service.client.chat.completions.create = Mock(
            side_effect=AuthenticationError("Invalid API key", response=Mock(), body=None)
        )
        
        result = await openai_service.clean_transcript(sample_transcript)
        
        assert result["success"] is False
        assert "Invalid" in result["error"]
    
    @pytest.mark.asyncio
    async def test_clean_transcript_rate_limit_error(self, openai_service, sample_transcript):
        """Test handling of rate limit errors"""
        from openai import RateLimitError
        
        openai_service.client.chat.completions.create = Mock(
            side_effect=RateLimitError("Rate limit exceeded", response=Mock(), body=None)
        )
        
        result = await openai_service.clean_transcript(sample_transcript)
        
        assert result["success"] is False
        assert "rate limit" in result["error"].lower()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_live_openai_cleaning(self, openai_api_key, sample_transcript):
        """Test with real OpenAI API (requires API key)"""
        service = OpenAIService()
        
        if not service.client:
            pytest.skip("OpenAI client not initialized")
        
        result = await service.clean_transcript(sample_transcript)
        
        assert result["success"] is True
        assert len(result["cleaned_transcript"]) > 0
        assert result["tokens_used"] > 0
