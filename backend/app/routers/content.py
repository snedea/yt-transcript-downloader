"""
Content ingestion router.

Provides endpoints for extracting content from various sources:
- YouTube URLs
- Web URLs
- PDF uploads
- Plain text
"""

import logging
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, Query
import aiofiles

from app.models.content import (
    ContentSourceType,
    UnifiedContent,
    ContentExtractionRequest,
    ContentUploadResponse,
)
from app.services.content_extractor import extract_content
from app.services.content_detector import detect_source_type

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/content", tags=["content"])


@router.post("/extract", response_model=UnifiedContent)
async def extract_content_endpoint(
    request: ContentExtractionRequest
) -> UnifiedContent:
    """
    Extract content from various sources.

    Accepts:
    - YouTube URLs: https://youtube.com/watch?v=...
    - Web URLs: https://example.com/article
    - Plain text: Any raw text content

    The source type is auto-detected if not provided.
    """
    try:
        content = await extract_content(
            source=request.source,
            source_type=request.source_type
        )

        # Override title/author if provided
        if request.title:
            content.title = request.title
        if request.author:
            content.author = request.author

        if not content.extraction_success:
            raise HTTPException(
                status_code=400,
                detail=f"Extraction failed: {content.extraction_error}"
            )

        return content

    except ValueError as e:
        logger.error(f"Content extraction error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during extraction: {e}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/upload", response_model=ContentUploadResponse)
async def upload_content(
    file: UploadFile = File(...),
    title: Optional[str] = Query(None, description="Override title"),
    author: Optional[str] = Query(None, description="Override author")
) -> ContentUploadResponse:
    """
    Upload a file for content extraction.

    Supported formats:
    - PDF (.pdf)
    - Text (.txt)
    - Markdown (.md, .markdown)
    """
    # Validate file type
    filename = file.filename or "upload"
    suffix = Path(filename).suffix.lower()

    supported_extensions = {".pdf", ".txt", ".md", ".markdown"}
    if suffix not in supported_extensions:
        return ContentUploadResponse(
            success=False,
            error=f"Unsupported file type: {suffix}. Supported: {', '.join(supported_extensions)}"
        )

    # Determine content type
    if suffix == ".pdf":
        source_type = ContentSourceType.PDF
    elif suffix in (".md", ".markdown"):
        source_type = ContentSourceType.MARKDOWN
    else:
        source_type = ContentSourceType.PLAIN_TEXT

    try:
        # Save to temporary file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
            prefix="content_upload_"
        ) as tmp:
            content_bytes = await file.read()
            tmp.write(content_bytes)
            tmp_path = tmp.name

        try:
            # Extract content
            content = await extract_content(
                source=tmp_path,
                source_type=source_type
            )

            # Override metadata if provided
            if title:
                content.title = title
            if author:
                content.author = author

            # Use original filename in source_url
            content.source_url = filename

            if not content.extraction_success:
                return ContentUploadResponse(
                    success=False,
                    error=content.extraction_error
                )

            return ContentUploadResponse(
                success=True,
                content=content
            )

        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)

    except Exception as e:
        logger.error(f"File upload error: {e}")
        return ContentUploadResponse(
            success=False,
            error=str(e)
        )


@router.get("/detect")
async def detect_content_type(
    source: str = Query(..., description="URL or text to analyze")
) -> dict:
    """
    Detect the content type of a source without extracting.

    Useful for UI to show appropriate input hints.
    """
    source_type, normalized, video_id = detect_source_type(source)

    return {
        "source_type": source_type.value,
        "normalized_source": normalized,
        "video_id": video_id,
        "is_youtube": source_type == ContentSourceType.YOUTUBE,
        "is_url": source_type in (ContentSourceType.YOUTUBE, ContentSourceType.WEB_URL),
        "is_file": source_type in (ContentSourceType.PDF, ContentSourceType.MARKDOWN),
    }
