"""Tests for OpenAI service"""
import pytest
from unittest.mock import Mock, patch
from app.services.openai_service import OpenAIService


class TestOpenAIService:
    """Test suite for OpenAIService class"""

    def test_init_invalid_api_key(self):
        """Test that invalid API key raises ValueError"""
        with patch('app.services.openai_service.OPENAI_API_KEY', ''):
            with pytest.raises(ValueError, match="Invalid OpenAI API key"):
                OpenAIService()

    def test_init_api_key_wrong_format(self):
        """Test that API key without 'sk-' prefix raises ValueError"""
        with patch('app.services.openai_service.OPENAI_API_KEY', 'invalid-key'):
            with pytest.raises(ValueError, match="Must start with 'sk-'"):
                OpenAIService()

    @pytest.mark.asyncio
    async def test_clean_transcript_success(self, sample_transcript):
        """Test successful transcript cleaning"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Cleaned transcript text."))]
        mock_response.usage = Mock(total_tokens=150)

        with patch('app.services.openai_service.OPENAI_API_KEY', 'sk-test-key'):
            service = OpenAIService()

            with patch.object(service.client.chat.completions, 'create', return_value=mock_response):
                result = await service.clean_transcript(sample_transcript)

                assert result["success"] is True
                assert result["cleaned_text"] == "Cleaned transcript text."
                assert result["tokens_used"] == 150
                assert "estimated_cost" in result
                assert result["estimated_cost"] > 0

    @pytest.mark.asyncio
    async def test_clean_transcript_empty_input(self):
        """Test cleaning empty transcript returns error"""
        with patch('app.services.openai_service.OPENAI_API_KEY', 'sk-test-key'):
            service = OpenAIService()
            result = await service.clean_transcript("")

            assert result["success"] is False
            assert "empty" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_clean_transcript_api_error(self, sample_transcript):
        """Test handling of OpenAI API errors"""
        with patch('app.services.openai_service.OPENAI_API_KEY', 'sk-test-key'):
            service = OpenAIService()

            with patch.object(service.client.chat.completions, 'create', side_effect=Exception("API Error")):
                result = await service.clean_transcript(sample_transcript)

                assert result["success"] is False
                assert "error" in result
                assert "API Error" in result["error"]

    @pytest.mark.asyncio
    async def test_clean_transcript_uses_gpt4o_mini(self, sample_transcript):
        """Test that service uses gpt-4o-mini model"""
        with patch('app.services.openai_service.OPENAI_API_KEY', 'sk-test-key'):
            service = OpenAIService()
            assert service.model == "gpt-4o-mini"
