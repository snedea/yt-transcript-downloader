"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import settings
from app.routers import auth, transcript, playlist, analysis, cache, content, health

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
app.include_router(auth.router) # /api/auth prefix is in the router
app.include_router(transcript.router, prefix="/api/transcript", tags=["transcript"])
app.include_router(playlist.router, prefix="/api/playlist", tags=["playlist"])
app.include_router(analysis.router)  # Already has /api/analysis prefix
app.include_router(cache.router)  # Already has /api/cache prefix
app.include_router(content.router)  # Already has /api/content prefix
app.include_router(health.router)  # Already has /api/health prefix

# Mount static file directories for PDF and thumbnail serving
UPLOADS_DIR = Path("uploads")
PDF_DIR = UPLOADS_DIR / "pdfs"
THUMBNAIL_DIR = UPLOADS_DIR / "thumbnails"

# Create directories if they don't exist
PDF_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/api/files/pdf", StaticFiles(directory=str(PDF_DIR)), name="pdfs")
app.mount("/api/files/thumbnail", StaticFiles(directory=str(THUMBNAIL_DIR)), name="thumbnails")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup"""
    import sys

    # Security configuration validation
    is_valid, errors = settings.validate_security_config()

    if not is_valid:
        print("\n" + "=" * 80)
        print("SECURITY CONFIGURATION ERRORS:")
        print("=" * 80)
        for error in errors:
            print(f"  ❌ {error}")
        print("=" * 80 + "\n")

        if settings.ENVIRONMENT == "production":
            print("FATAL: Cannot start application with security errors in production mode.")
            print("Fix the errors above and restart the application.\n")
            sys.exit(1)
        else:
            print("WARNING: Security errors detected in development mode.")
            print("These MUST be fixed before deploying to production!\n")

    # OpenAI API key validation
    if settings.OPENAI_API_KEY and not settings.validate_api_key():
        print("WARNING: OpenAI API key format is invalid. Expected format: sk-...")
    elif not settings.OPENAI_API_KEY:
        print("INFO: OpenAI API key not configured. Transcript cleaning will be unavailable.")
    else:
        print("INFO: OpenAI API key validated successfully")

    # JWT Secret warning in development
    if settings.ENVIRONMENT != "production":
        default_secret = "change-this-in-production-use-openssl-rand-hex-32"
        if settings.JWT_SECRET_KEY == default_secret:
            print("INFO: Using default JWT_SECRET_KEY in development mode.")
            print("      Generate a production secret with: openssl rand -hex 32")

    print(f"\nApplication starting in {settings.ENVIRONMENT.upper()} mode...")
