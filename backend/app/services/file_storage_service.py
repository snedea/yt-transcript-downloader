"""
File Storage Service

Handles permanent storage of uploaded PDFs and generated thumbnails.
Provides file path management and URL generation for static file serving.
"""

import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class FileStorageService:
    """
    Service for storing and retrieving files (PDFs, thumbnails).

    Directory Structure:
    - uploads/pdfs/          Original PDF files
    - uploads/thumbnails/    Generated thumbnail images
    - uploads/temp/          Temporary uploads (auto-cleanup)
    """

    UPLOADS_DIR = Path("uploads")
    PDF_DIR = UPLOADS_DIR / "pdfs"
    THUMBNAIL_DIR = UPLOADS_DIR / "thumbnails"
    TEMP_DIR = UPLOADS_DIR / "temp"

    def __init__(self):
        """Initialize service and create directory structure."""
        self._create_directories()

    def _create_directories(self):
        """Create uploads directory structure if it doesn't exist."""
        for directory in [self.PDF_DIR, self.THUMBNAIL_DIR, self.TEMP_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {directory}")

    def generate_source_id(self, file_content: bytes, filename: str) -> str:
        """
        Generate unique source_id from file content hash.

        Args:
            file_content: Raw file bytes
            filename: Original filename (for additional entropy)

        Returns:
            16-character hex string (MD5 hash)

        Example:
            'a1b2c3d4e5f6g7h8'
        """
        timestamp = datetime.utcnow().isoformat()
        hash_input = file_content + timestamp.encode() + filename.encode()
        return hashlib.md5(hash_input).hexdigest()[:16]

    def save_pdf(self, file_content: bytes, source_id: str) -> str:
        """
        Save PDF file permanently to uploads/pdfs/.

        Args:
            file_content: PDF file bytes
            source_id: Unique identifier for this PDF

        Returns:
            Relative file path (e.g., 'uploads/pdfs/abc123.pdf')

        Raises:
            IOError: If file write fails
        """
        try:
            pdf_path = self.PDF_DIR / f"{source_id}.pdf"
            pdf_path.write_bytes(file_content)
            relative_path = str(pdf_path.relative_to(Path.cwd()))
            logger.info(f"Saved PDF to {relative_path}")
            return relative_path
        except Exception as e:
            logger.error(f"Failed to save PDF {source_id}: {e}")
            raise IOError(f"Failed to save PDF: {e}")

    def save_thumbnail(self, image_bytes: bytes, source_id: str, format: str = "jpg") -> str:
        """
        Save thumbnail image to uploads/thumbnails/.

        Args:
            image_bytes: Image file bytes (JPEG or PNG)
            source_id: Unique identifier matching the PDF
            format: Image format extension (default: 'jpg')

        Returns:
            Relative file path (e.g., 'uploads/thumbnails/abc123.jpg')

        Raises:
            IOError: If file write fails
        """
        try:
            thumb_path = self.THUMBNAIL_DIR / f"{source_id}.{format}"
            thumb_path.write_bytes(image_bytes)
            relative_path = str(thumb_path.relative_to(Path.cwd()))
            logger.info(f"Saved thumbnail to {relative_path}")
            return relative_path
        except Exception as e:
            logger.error(f"Failed to save thumbnail {source_id}: {e}")
            raise IOError(f"Failed to save thumbnail: {e}")

    def get_pdf_path(self, source_id: str) -> Path:
        """Get full path to PDF file."""
        return self.PDF_DIR / f"{source_id}.pdf"

    def get_thumbnail_path(self, source_id: str, format: str = "jpg") -> Path:
        """Get full path to thumbnail file."""
        return self.THUMBNAIL_DIR / f"{source_id}.{format}"

    def pdf_exists(self, source_id: str) -> bool:
        """Check if PDF file exists."""
        return self.get_pdf_path(source_id).exists()

    def thumbnail_exists(self, source_id: str, format: str = "jpg") -> bool:
        """Check if thumbnail file exists."""
        return self.get_thumbnail_path(source_id, format).exists()

    def get_pdf_url(self, file_path: str) -> str:
        """
        Convert file path to API URL for serving.

        Args:
            file_path: Relative or absolute path to PDF

        Returns:
            API URL (e.g., '/api/files/pdf/abc123.pdf')
        """
        filename = Path(file_path).name
        return f"/api/files/pdf/{filename}"

    def get_thumbnail_url(self, thumbnail_path: Optional[str]) -> Optional[str]:
        """
        Convert thumbnail path to API URL for serving.

        Args:
            thumbnail_path: Relative or absolute path to thumbnail (or None)

        Returns:
            API URL or None if path is None
        """
        if not thumbnail_path:
            return None
        filename = Path(thumbnail_path).name
        return f"/api/files/thumbnail/{filename}"

    def delete_pdf(self, source_id: str) -> bool:
        """
        Delete PDF file.

        Args:
            source_id: Source identifier

        Returns:
            True if deleted, False if not found
        """
        try:
            pdf_path = self.get_pdf_path(source_id)
            if pdf_path.exists():
                pdf_path.unlink()
                logger.info(f"Deleted PDF: {source_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete PDF {source_id}: {e}")
            return False

    def delete_thumbnail(self, source_id: str, format: str = "jpg") -> bool:
        """
        Delete thumbnail file.

        Args:
            source_id: Source identifier
            format: Image format

        Returns:
            True if deleted, False if not found
        """
        try:
            thumb_path = self.get_thumbnail_path(source_id, format)
            if thumb_path.exists():
                thumb_path.unlink()
                logger.info(f"Deleted thumbnail: {source_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete thumbnail {source_id}: {e}")
            return False

    def get_storage_stats(self) -> dict:
        """
        Get storage statistics.

        Returns:
            Dict with file counts and sizes
        """
        try:
            pdf_files = list(self.PDF_DIR.glob("*.pdf"))
            thumbnail_files = list(self.THUMBNAIL_DIR.glob("*"))

            pdf_size = sum(f.stat().st_size for f in pdf_files if f.is_file())
            thumbnail_size = sum(f.stat().st_size for f in thumbnail_files if f.is_file())

            return {
                "pdf_count": len(pdf_files),
                "thumbnail_count": len(thumbnail_files),
                "pdf_size_bytes": pdf_size,
                "thumbnail_size_bytes": thumbnail_size,
                "pdf_size_mb": round(pdf_size / (1024 * 1024), 2),
                "thumbnail_size_mb": round(thumbnail_size / (1024 * 1024), 2),
                "total_size_mb": round((pdf_size + thumbnail_size) / (1024 * 1024), 2),
            }
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {}


# Singleton instance
_file_storage_instance: Optional[FileStorageService] = None


def get_file_storage_service() -> FileStorageService:
    """Get or create singleton FileStorageService instance."""
    global _file_storage_instance
    if _file_storage_instance is None:
        _file_storage_instance = FileStorageService()
    return _file_storage_instance
