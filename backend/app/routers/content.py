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

from fastapi import APIRouter, File, UploadFile, HTTPException, Query, Depends, BackgroundTasks
from sqlmodel import Session, select
import aiofiles

from app.models.content import (
    ContentSourceType,
    UnifiedContent,
    ContentExtractionRequest,
    ContentUploadResponse,
)
from app.services.content_extractor import extract_content
from app.db import get_session
from app.dependencies import get_current_user
from app.models.auth import User
from app.services.content_detector import detect_source_type
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/content", tags=["content"])


class ContentSubmitRequest(BaseModel):
    """Request model for unified content submission"""
    content_input: str
    input_type: Optional[str] = None
    title_override: Optional[str] = None
    save_to_library: bool = True


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


@router.post("/submit")
async def submit_content_unified(
    request: ContentSubmitRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Unified content submission endpoint for URLs and plain text.

    Auto-detects:
    - YouTube URLs
    - Web article URLs
    - Plain text (when not a URL)

    Args:
        content_input: URL or plain text content
        input_type: Optional type hint ("url" or "text")
        title_override: Optional custom title
        save_to_library: Whether to save to user's library (default: True)

    Returns:
        {
            "content": UnifiedContent object,
            "library_id": source_id,
            "source_type": detected type
        }
    """
    from app.services.content_detector import detect_source_type
    from app.services.cache_service import get_cache_service

    try:
        # Detect content type
        source_type, normalized_source, video_id = detect_source_type(request.content_input)

        logger.info(f"Detected source_type: {source_type}, normalized: {normalized_source}")

        # Extract content
        content = await extract_content(
            source=normalized_source or request.content_input,
            source_type=source_type
        )

        # Override title if provided
        if request.title_override:
            content.title = request.title_override

        if not content.extraction_success:
            raise HTTPException(
                status_code=400,
                detail=f"Extraction failed: {content.extraction_error}"
            )

        # Save to library if requested
        library_id = content.source_id
        if request.save_to_library:
            cache_service = get_cache_service()

            # Prepare raw_content_text for plain text sources
            raw_content_text = None
            if source_type == ContentSourceType.PLAIN_TEXT:
                raw_content_text = request.content_input  # Store original pasted text

            success = cache_service.save(
                session=session,
                video_id=content.source_id,
                video_title=content.title,
                transcript_text=content.text,
                user_id=current_user.id,
                author=content.author,
                upload_date=content.upload_date,
                source_type=source_type.value,
                source_url=content.source_url,
                raw_content_text=raw_content_text,
                word_count=content.word_count,
                character_count=content.character_count
            )

            if not success:
                logger.warning(f"Failed to save content {content.source_id} to library")

        return {
            "success": True,
            "content": content.dict(),
            "library_id": library_id,
            "source_type": source_type.value,
            "message": f"Content captured successfully ({source_type.value})"
        }

    except ValueError as e:
        logger.error(f"Content submission error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during content submission: {e}")
        raise HTTPException(status_code=500, detail=f"Submission failed: {str(e)}")


@router.post("/upload", response_model=ContentUploadResponse)
async def upload_content(
    file: UploadFile = File(...),
    title: Optional[str] = Query(None, description="Override title"),
    author: Optional[str] = Query(None, description="Override author"),
    save_to_library: bool = Query(True, description="Save to library (default: true)"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> ContentUploadResponse:
    """
    Upload a file for content extraction.

    Supported formats:
    - PDF (.pdf) - Saved permanently to library with thumbnail generation
    - Text (.txt)
    - Markdown (.md, .markdown)

    For PDFs with save_to_library=true:
    - File is stored permanently
    - Added to your library
    - Thumbnail generated in background
    """
    from app.services.file_storage_service import get_file_storage_service
    from app.services.cache_service import get_cache_service
    from app.services.thumbnail_generator_service import get_thumbnail_generator_service

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
        # Read file content
        content_bytes = await file.read()

        # For PDFs with library save, use permanent storage
        if suffix == ".pdf" and save_to_library:
            file_storage = get_file_storage_service()
            cache_service = get_cache_service()

            # Generate unique source_id
            source_id = file_storage.generate_source_id(content_bytes, filename)

            # Save PDF permanently
            pdf_path = file_storage.save_pdf(content_bytes, source_id)
            logger.info(f"Saved PDF permanently: {pdf_path}")

            # Extract content from PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(content_bytes)
                tmp_path = tmp.name

            try:
                content = await extract_content(
                    source=tmp_path,
                    source_type=source_type
                )

                # Override metadata
                if title:
                    content.title = title
                if author:
                    content.author = author

                content.source_id = source_id
                content.source_url = filename

                if not content.extraction_success:
                    return ContentUploadResponse(
                        success=False,
                        error=content.extraction_error
                    )

                # Save to library cache
                success = cache_service.save(
                    session=session,
                    video_id=source_id,
                    video_title=content.title,
                    transcript_text=content.text,
                    user_id=current_user.id,
                    author=content.author,
                    source_type="pdf",
                    source_url=filename,
                    file_path=pdf_path,
                    word_count=content.word_count,
                    character_count=content.character_count,
                    page_count=content.metadata.get("page_count")
                )

                if not success:
                    logger.error(f"Failed to save PDF {source_id} to cache")

                # Generate thumbnail in background
                background_tasks.add_task(
                    generate_and_save_thumbnail_task,
                    pdf_path=pdf_path,
                    source_id=source_id,
                    title=content.title,
                    author=content.author,
                    user_id=current_user.id,
                    session_maker=lambda: next(get_session())
                )

                return ContentUploadResponse(
                    success=True,
                    content=content,
                    message=f"PDF uploaded successfully. Added to library with ID: {source_id}. Thumbnail generating in background."
                )

            finally:
                Path(tmp_path).unlink(missing_ok=True)

        else:
            # Original behavior for non-PDFs or when not saving to library
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
                prefix="content_upload_"
            ) as tmp:
                tmp.write(content_bytes)
                tmp_path = tmp.name

            try:
                content = await extract_content(
                    source=tmp_path,
                    source_type=source_type
                )

                if title:
                    content.title = title
                if author:
                    content.author = author

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
                Path(tmp_path).unlink(missing_ok=True)

    except Exception as e:
        logger.error(f"File upload error: {e}")
        return ContentUploadResponse(
            success=False,
            error=str(e)
        )


async def generate_and_save_thumbnail_task(
    pdf_path: str,
    source_id: str,
    title: str,
    author: Optional[str],
    user_id: str,
    session_maker
):
    """
    Background task to generate thumbnail and update cache.

    Args:
        pdf_path: Path to PDF file
        source_id: Source identifier
        title: Document title
        author: Document author
        user_id: User ID who uploaded
        session_maker: Function to create new database session
    """
    from app.services.thumbnail_generator_service import get_thumbnail_generator_service
    from app.models.cache import Transcript

    try:
        thumbnail_service = get_thumbnail_generator_service()

        # Generate thumbnail
        thumbnail_path = await thumbnail_service.generate_pdf_thumbnail(
            pdf_path=pdf_path,
            source_id=source_id,
            title=title,
            author=author
        )

        if thumbnail_path:
            # Update transcript record with thumbnail path
            session = session_maker()  # Call the function to get a session
            try:
                transcript = session.exec(
                    select(Transcript).where(
                        Transcript.video_id == source_id,
                        Transcript.user_id == user_id
                    )
                ).first()

                if transcript:
                    transcript.thumbnail_path = thumbnail_path
                    session.add(transcript)
                    session.commit()
                    logger.info(f"Thumbnail saved for {source_id}: {thumbnail_path}")
                else:
                    logger.warning(f"Transcript not found for thumbnail update: {source_id}")
            finally:
                session.close()
        else:
            logger.warning(f"Thumbnail generation returned None for {source_id}")

    except Exception as e:
        logger.error(f"Background thumbnail generation failed for {source_id}: {e}")


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
