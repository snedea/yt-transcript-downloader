"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import transcript, playlist, analysis, cache

# Initialize FastAPI app
app = FastAPI(
    title="YouTube Transcript Downloader API",
    description="API for downloading and cleaning YouTube video transcripts",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(transcript.router, prefix="/api/transcript", tags=["transcript"])
app.include_router(playlist.router, prefix="/api/playlist", tags=["playlist"])
app.include_router(analysis.router)  # Already has /api/analysis prefix
app.include_router(cache.router)  # Already has /api/cache prefix


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup"""
    if settings.OPENAI_API_KEY and not settings.validate_api_key():
        print("WARNING: OpenAI API key format is invalid. Expected format: sk-...")
    elif not settings.OPENAI_API_KEY:
        print("INFO: OpenAI API key not configured. Transcript cleaning will be unavailable.")
    else:
        print("INFO: OpenAI API key validated successfully")
