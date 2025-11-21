"""pytest fixtures and configuration"""
import pytest
import os
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def openai_api_key():
    """OpenAI API key fixture - skip test if not available"""
    key = os.getenv("OPENAI_API_KEY")
    if not key or not key.startswith("sk-"):
        pytest.skip("OpenAI API key not available")
    return key


@pytest.fixture
def sample_transcript():
    """Sample transcript text for testing"""
    return (
        "hello everyone welcome to this video today we're going to talk about "
        "artificial intelligence and machine learning um so first let me explain "
        "what AI is uh AI stands for artificial intelligence"
    )


@pytest.fixture
def sample_video_urls():
    """Sample YouTube video URLs for testing"""
    return {
        "watch": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "short": "https://youtu.be/dQw4w9WgXcQ",
        "mobile": "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
        "invalid": "https://example.com/video"
    }


@pytest.fixture
def sample_playlist_url():
    """Sample playlist URL for testing"""
    return "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
