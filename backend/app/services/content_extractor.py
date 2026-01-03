"""
Content extractors for universal content ingestion.

Extracts text content from:
- YouTube videos (via existing YouTubeService)
- PDF files (via pdfplumber)
- Web URLs (via httpx + beautifulsoup)
- Plain text (passthrough)
"""

import hashlib
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List, Type
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
import html2text

from app.models.content import (
    ContentSourceType,
    ContentSegment,
    UnifiedContent,
)
from app.services.content_detector import ContentDetector
from app.services.youtube import YouTubeService

logger = logging.getLogger(__name__)


class ContentExtractor(ABC):
    """Base class for content extractors."""

    @abstractmethod
    async def extract(self, source: str) -> UnifiedContent:
        """Extract content from source."""
        pass

    @abstractmethod
    def can_handle(self, source_type: ContentSourceType) -> bool:
        """Check if this extractor can handle the given source type."""
        pass


class YouTubeExtractor(ContentExtractor):
    """Extracts content from YouTube videos using existing YouTubeService."""

    def __init__(self):
        self.youtube_service = YouTubeService()

    def can_handle(self, source_type: ContentSourceType) -> bool:
        return source_type == ContentSourceType.YOUTUBE

    async def extract(self, source: str) -> UnifiedContent:
        """Extract transcript from YouTube video."""
        video_id = ContentDetector.extract_youtube_id(source)
        if not video_id:
            raise ValueError(f"Could not extract video ID from: {source}")

        # Get transcript
        transcript_result = await self.youtube_service.get_transcript(video_id)
        if not transcript_result.get("success"):
            raise ValueError(
                f"Failed to get transcript: {transcript_result.get('error', 'Unknown error')}"
            )

        # Get metadata
        metadata_result = await self.youtube_service.get_video_metadata(video_id)

        # Convert transcript segments
        segments = []
        raw_transcript = transcript_result.get("transcript", [])
        for i, seg in enumerate(raw_transcript):
            segments.append(ContentSegment(
                text=seg.get("text", ""),
                start_time=seg.get("start"),
                duration=seg.get("duration"),
                segment_index=i
            ))

        full_text = transcript_result.get("text", "")

        return UnifiedContent(
            text=full_text,
            source_type=ContentSourceType.YOUTUBE,
            source_id=video_id,
            source_url=f"https://youtube.com/watch?v={video_id}",
            title=metadata_result.get("title", f"YouTube Video {video_id}"),
            author=metadata_result.get("author"),
            upload_date=metadata_result.get("upload_date"),
            segments=segments,
            word_count=len(full_text.split()),
            character_count=len(full_text),
            metadata={
                "transcript_segments": len(segments),
                "has_timestamps": True
            }
        )


class PDFExtractor(ContentExtractor):
    """Extracts content from PDF files using pdfplumber."""

    def can_handle(self, source_type: ContentSourceType) -> bool:
        return source_type == ContentSourceType.PDF

    async def extract(self, source: str) -> UnifiedContent:
        """Extract text from PDF file."""
        import pdfplumber

        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {source}")

        segments = []
        full_text_parts = []
        metadata = {}

        try:
            with pdfplumber.open(path) as pdf:
                metadata["page_count"] = len(pdf.pages)
                metadata["pdf_info"] = pdf.metadata or {}

                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    if text.strip():
                        segments.append(ContentSegment(
                            text=text,
                            segment_index=page_num
                        ))
                        full_text_parts.append(text)

        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise ValueError(f"Failed to extract PDF: {str(e)}")

        full_text = "\n\n".join(full_text_parts)

        # Try to extract title from PDF metadata or filename
        pdf_title = metadata.get("pdf_info", {}).get("Title")

        if pdf_title:
            title = pdf_title
        elif full_text_parts:
            # Extract title from first page text (first meaningful line)
            first_page = full_text_parts[0] if full_text_parts else ""
            lines = [line.strip() for line in first_page.split('\n') if line.strip()]

            # Skip page numbers and find first substantial line
            title_lines = []
            for line in lines[:10]:  # Check first 10 lines
                # Skip if line is just a number, too short, or all caps single word
                if len(line) > 3 and not line.isdigit():
                    title_lines.append(line)
                    if len(' '.join(title_lines)) > 50:  # Enough for a title
                        break

            title = ' '.join(title_lines[:3])  # Use first 3 meaningful lines
            title = title[:100] if title else path.stem  # Truncate to 100 chars or use filename
        else:
            title = path.stem

        # Try to extract author from PDF metadata
        pdf_author = metadata.get("pdf_info", {}).get("Author")

        return UnifiedContent(
            text=full_text,
            source_type=ContentSourceType.PDF,
            source_id=hashlib.md5(str(path).encode()).hexdigest()[:12],
            source_url=str(path),
            title=title,
            author=pdf_author,
            segments=segments,
            word_count=len(full_text.split()),
            character_count=len(full_text),
            metadata=metadata
        )


class URLExtractor(ContentExtractor):
    """Extracts content from web URLs using httpx + beautifulsoup."""

    def __init__(self):
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        self.html_converter.ignore_emphasis = False
        self.html_converter.body_width = 0  # No wrapping

    def can_handle(self, source_type: ContentSourceType) -> bool:
        return source_type == ContentSourceType.WEB_URL

    async def extract(self, source: str) -> UnifiedContent:
        """Extract article content from web URL."""
        try:
            async with httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; ContentExtractor/1.0)"
                }
            ) as client:
                response = await client.get(source)
                response.raise_for_status()
                html_content = response.text

        except httpx.HTTPError as e:
            logger.error(f"Error fetching URL: {e}")
            raise ValueError(f"Failed to fetch URL: {str(e)}")

        # Parse HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract title
        title = self._extract_title(soup)

        # Extract author
        author = self._extract_author(soup)

        # Extract main content
        main_content = self._extract_main_content(soup)

        # Convert to markdown/plain text
        text = self.html_converter.handle(str(main_content))
        text = text.strip()

        # Extract publish date
        publish_date = self._extract_date(soup)

        return UnifiedContent(
            text=text,
            source_type=ContentSourceType.WEB_URL,
            source_id=hashlib.md5(source.encode()).hexdigest()[:12],
            source_url=source,
            title=title or source,
            author=author,
            upload_date=publish_date,
            word_count=len(text.split()),
            character_count=len(text),
            metadata={
                "original_url": source,
                "extracted_method": "beautifulsoup"
            }
        )

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract title from HTML."""
        # Try og:title first
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"]

        # Try <title> tag
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text().strip()

        # Try h1
        h1 = soup.find("h1")
        if h1:
            return h1.get_text().strip()

        return None

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author from HTML."""
        # Try meta author
        meta_author = soup.find("meta", attrs={"name": "author"})
        if meta_author and meta_author.get("content"):
            return meta_author["content"]

        # Try article:author
        og_author = soup.find("meta", property="article:author")
        if og_author and og_author.get("content"):
            return og_author["content"]

        return None

    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publish date from HTML."""
        # Try article:published_time
        og_date = soup.find("meta", property="article:published_time")
        if og_date and og_date.get("content"):
            return og_date["content"][:10]  # Just the date part

        # Try datePublished
        date_meta = soup.find("meta", attrs={"itemprop": "datePublished"})
        if date_meta and date_meta.get("content"):
            return date_meta["content"][:10]

        return None

    def _extract_main_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Extract main content, removing navigation, ads, etc."""
        # Remove unwanted elements
        for element in soup.find_all([
            "nav", "header", "footer", "aside", "script", "style",
            "noscript", "iframe", "form"
        ]):
            element.decompose()

        # Remove elements by class/id patterns
        for pattern in ["nav", "menu", "sidebar", "ad", "advertisement", "comment"]:
            for element in soup.find_all(class_=lambda x: x and pattern in x.lower()):
                element.decompose()
            for element in soup.find_all(id=lambda x: x and pattern in x.lower()):
                element.decompose()

        # Try to find article content
        article = soup.find("article")
        if article:
            return article

        # Try main tag
        main = soup.find("main")
        if main:
            return main

        # Fall back to body
        body = soup.find("body")
        return body if body else soup


class PlainTextExtractor(ContentExtractor):
    """Passthrough extractor for plain text."""

    def can_handle(self, source_type: ContentSourceType) -> bool:
        return source_type in (ContentSourceType.PLAIN_TEXT, ContentSourceType.MARKDOWN)

    async def extract(self, source: str) -> UnifiedContent:
        """Create UnifiedContent from plain text."""
        # Check if it's a file path or raw text
        # A file path should be relatively short and not contain newlines
        is_likely_file_path = (
            len(source) < 500 and  # File paths are typically short
            '\n' not in source and  # File paths don't contain newlines
            not source.startswith(' ')  # File paths don't start with whitespace
        )

        if is_likely_file_path:
            try:
                path = Path(source)
                if path.exists() and path.is_file():
                    text = path.read_text(encoding="utf-8")
                    title = path.stem
                    source_id = hashlib.md5(str(path).encode()).hexdigest()[:12]
                    source_type = (
                        ContentSourceType.MARKDOWN
                        if path.suffix.lower() in (".md", ".markdown")
                        else ContentSourceType.PLAIN_TEXT
                    )
                else:
                    # Path doesn't exist, treat as raw text
                    text = source
                    title = self._generate_title(source)
                    source_id = hashlib.md5(source.encode()).hexdigest()[:12]
                    source_type = ContentSourceType.PLAIN_TEXT
            except (OSError, ValueError):
                # Path creation failed (e.g., invalid characters), treat as raw text
                text = source
                title = self._generate_title(source)
                source_id = hashlib.md5(source.encode()).hexdigest()[:12]
                source_type = ContentSourceType.PLAIN_TEXT
        else:
            # It's raw text (too long or contains newlines)
            text = source
            title = self._generate_title(source)
            source_id = hashlib.md5(source.encode()).hexdigest()[:12]
            source_type = ContentSourceType.PLAIN_TEXT

        # Split into paragraph segments
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        segments = [
            ContentSegment(text=p, segment_index=i)
            for i, p in enumerate(paragraphs)
        ]

        return UnifiedContent(
            text=text,
            source_type=source_type,
            source_id=source_id,
            title=title,
            segments=segments if len(segments) > 1 else None,
            word_count=len(text.split()),
            character_count=len(text)
        )

    def _generate_title(self, text: str) -> str:
        """Generate a title from the first line or words of text."""
        first_line = text.split("\n")[0].strip()
        if len(first_line) <= 100:
            return first_line
        return first_line[:97] + "..."


# Registry of extractors
EXTRACTORS: List[Type[ContentExtractor]] = [
    YouTubeExtractor,
    PDFExtractor,
    URLExtractor,
    PlainTextExtractor,
]


def get_extractor(source_type: ContentSourceType) -> ContentExtractor:
    """Get the appropriate extractor for a source type."""
    for extractor_class in EXTRACTORS:
        extractor = extractor_class()
        if extractor.can_handle(source_type):
            return extractor

    raise ValueError(f"No extractor found for source type: {source_type}")


async def extract_content(
    source: str,
    source_type: Optional[ContentSourceType] = None
) -> UnifiedContent:
    """
    Extract content from any source.

    Args:
        source: URL, file path, or raw text
        source_type: Optional type override. Auto-detected if not provided.

    Returns:
        UnifiedContent with extracted text and metadata
    """
    # Detect source type if not provided
    if source_type is None:
        source_type, source, _ = ContentDetector.detect(source)

    # Get appropriate extractor
    extractor = get_extractor(source_type)

    # Extract content
    try:
        content = await extractor.extract(source)
        return content
    except Exception as e:
        logger.error(f"Extraction failed for {source_type}: {e}")
        # Return error content
        return UnifiedContent(
            text="",
            source_type=source_type,
            source_id=hashlib.md5(source.encode()).hexdigest()[:12],
            title="Extraction Failed",
            word_count=0,
            character_count=0,
            extraction_success=False,
            extraction_error=str(e)
        )
