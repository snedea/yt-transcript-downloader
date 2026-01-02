"""
Content source type detection.

Automatically detects whether input is a YouTube URL, web URL, file path, or plain text.
"""

import re
from pathlib import Path
from typing import Tuple, Optional
from app.models.content import ContentSourceType


class ContentDetector:
    """Detects content source type from string input."""

    # YouTube URL patterns
    YOUTUBE_PATTERNS = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
    ]

    # File extension mappings
    FILE_EXTENSIONS = {
        '.pdf': ContentSourceType.PDF,
        '.txt': ContentSourceType.PLAIN_TEXT,
        '.md': ContentSourceType.MARKDOWN,
        '.markdown': ContentSourceType.MARKDOWN,
    }

    @classmethod
    def detect(cls, source: str) -> Tuple[ContentSourceType, str, Optional[str]]:
        """
        Detect content source type from string input.

        Args:
            source: URL, file path, or raw text

        Returns:
            Tuple of (ContentSourceType, normalized_source, optional_video_id)

        Examples:
            >>> detect("https://youtube.com/watch?v=abc123def45")
            (ContentSourceType.YOUTUBE, "https://youtube.com/watch?v=abc123def45", "abc123def45")

            >>> detect("https://example.com/article")
            (ContentSourceType.WEB_URL, "https://example.com/article", None)

            >>> detect("/path/to/file.pdf")
            (ContentSourceType.PDF, "/path/to/file.pdf", None)

            >>> detect("This is plain text content...")
            (ContentSourceType.PLAIN_TEXT, "This is plain text content...", None)
        """
        source = source.strip()

        # Check for YouTube URL first
        video_id = cls.extract_youtube_id(source)
        if video_id:
            return ContentSourceType.YOUTUBE, source, video_id

        # Check for HTTP(S) URL
        if cls.is_web_url(source):
            return ContentSourceType.WEB_URL, source, None

        # Check for file path
        file_type = cls.detect_file_type(source)
        if file_type:
            return file_type, source, None

        # Default to plain text
        return ContentSourceType.PLAIN_TEXT, source, None

    @classmethod
    def extract_youtube_id(cls, url: str) -> Optional[str]:
        """
        Extract YouTube video ID from URL.

        Returns None if not a YouTube URL.
        """
        for pattern in cls.YOUTUBE_PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    @classmethod
    def is_web_url(cls, source: str) -> bool:
        """Check if source is an HTTP(S) URL."""
        return bool(re.match(r'^https?://', source, re.IGNORECASE))

    @classmethod
    def detect_file_type(cls, source: str) -> Optional[ContentSourceType]:
        """
        Detect file type from path.

        Returns None if path doesn't exist or has unknown extension.
        """
        try:
            path = Path(source)

            # Check if it looks like a file path (has extension or exists)
            if path.suffix:
                suffix = path.suffix.lower()
                if suffix in cls.FILE_EXTENSIONS:
                    return cls.FILE_EXTENSIONS[suffix]

            # Check if path exists on disk
            if path.exists() and path.is_file():
                suffix = path.suffix.lower()
                return cls.FILE_EXTENSIONS.get(suffix, ContentSourceType.PLAIN_TEXT)

        except (OSError, ValueError):
            # Not a valid path
            pass

        return None

    @classmethod
    def is_youtube_url(cls, url: str) -> bool:
        """Quick check if URL is a YouTube URL."""
        return cls.extract_youtube_id(url) is not None

    @classmethod
    def looks_like_url(cls, source: str) -> bool:
        """Check if source looks like any kind of URL."""
        return bool(re.match(r'^https?://', source, re.IGNORECASE))

    @classmethod
    def looks_like_file_path(cls, source: str) -> bool:
        """Check if source looks like a file path."""
        # Starts with / or ./ or contains typical path separators
        if source.startswith('/') or source.startswith('./') or source.startswith('..'):
            return True

        # Has a file extension we recognize
        path = Path(source)
        return path.suffix.lower() in cls.FILE_EXTENSIONS


def detect_source_type(source: str) -> Tuple[ContentSourceType, str, Optional[str]]:
    """
    Convenience function to detect source type.

    Returns: (ContentSourceType, normalized_source, optional_video_id)
    """
    return ContentDetector.detect(source)
