"""
Thumbnail Generator Service

Generates thumbnails for PDF documents.

Phase 1 (MVP): Extract first page as JPEG thumbnail
Phase 2 (Future): Use OpenAI Vision + DALL-E for artistic thumbnails
"""

import logging
import io
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

from app.services.file_storage_service import FileStorageService

logger = logging.getLogger(__name__)


class ThumbnailGeneratorService:
    """
    Service for generating PDF thumbnails.

    Currently extracts first page as image (Phase 1).
    Future: AI-generated artistic thumbnails (Phase 2).
    """

    # YouTube thumbnail size for consistency
    THUMBNAIL_WIDTH = 320
    THUMBNAIL_HEIGHT = 180
    THUMBNAIL_QUALITY = 85

    def __init__(self):
        """Initialize service."""
        self.file_storage = FileStorageService()

    async def generate_pdf_thumbnail(
        self,
        pdf_path: str,
        source_id: str,
        title: str,
        author: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate thumbnail for PDF document.

        Phase 1: Extracts first page and converts to JPEG
        Phase 2: Will use OpenAI Vision for artistic generation

        Args:
            pdf_path: Path to PDF file
            source_id: Unique identifier for this PDF
            title: PDF document title
            author: PDF author (optional)

        Returns:
            Relative path to saved thumbnail, or None if failed

        Example:
            'uploads/thumbnails/abc123.jpg'
        """
        try:
            # Try to extract first page as image
            thumbnail_bytes = await self._extract_first_page_as_jpeg(pdf_path)

            if thumbnail_bytes:
                # Save thumbnail
                thumbnail_path = self.file_storage.save_thumbnail(
                    thumbnail_bytes,
                    source_id,
                    format="jpg"
                )
                logger.info(f"Generated thumbnail for {source_id}")
                return thumbnail_path
            else:
                # Fallback: create generic PDF icon thumbnail
                logger.warning(f"First page extraction failed for {source_id}, using fallback")
                return await self._create_fallback_thumbnail(source_id, title)

        except Exception as e:
            logger.error(f"Thumbnail generation failed for {source_id}: {e}")
            # Try fallback
            try:
                return await self._create_fallback_thumbnail(source_id, title)
            except Exception as fallback_error:
                logger.error(f"Fallback thumbnail generation also failed: {fallback_error}")
                return None

    async def _extract_first_page_as_jpeg(self, pdf_path: str) -> Optional[bytes]:
        """
        Extract first page of PDF as JPEG image.

        Uses pdf2image library to convert PDF page to PIL Image,
        then resizes to YouTube thumbnail dimensions.

        Args:
            pdf_path: Path to PDF file (relative or absolute)

        Returns:
            JPEG bytes or None if extraction fails
        """
        try:
            from pdf2image import convert_from_path

            # Convert to absolute path if relative
            pdf_path_obj = Path(pdf_path)
            if not pdf_path_obj.is_absolute():
                pdf_path_obj = Path.cwd() / pdf_path_obj

            absolute_path = str(pdf_path_obj)

            # Convert first page only (faster)
            pages = convert_from_path(
                absolute_path,
                first_page=1,
                last_page=1,
                dpi=150,  # Good quality/speed balance
                fmt='jpeg'
            )

            if not pages:
                logger.warning(f"No pages extracted from {pdf_path}")
                return None

            first_page = pages[0]

            # Resize to YouTube thumbnail size (320x180)
            resized_image = self._resize_to_thumbnail(first_page)

            # Convert to JPEG bytes
            buffered = io.BytesIO()
            resized_image.save(buffered, format="JPEG", quality=self.THUMBNAIL_QUALITY, optimize=True)
            return buffered.getvalue()

        except ImportError:
            logger.error("pdf2image not installed. Run: pip install pdf2image")
            return None
        except Exception as e:
            logger.error(f"Failed to extract first page from {pdf_path}: {e}")
            return None

    def _resize_to_thumbnail(self, image: Image.Image) -> Image.Image:
        """
        Resize image to YouTube thumbnail dimensions (320x180).

        Maintains aspect ratio and adds padding if needed.

        Args:
            image: PIL Image object

        Returns:
            Resized PIL Image (320x180)
        """
        # Calculate scaling to fit within thumbnail dimensions
        original_width, original_height = image.size
        aspect_ratio = original_width / original_height

        if aspect_ratio > (self.THUMBNAIL_WIDTH / self.THUMBNAIL_HEIGHT):
            # Width is limiting factor
            new_width = self.THUMBNAIL_WIDTH
            new_height = int(new_width / aspect_ratio)
        else:
            # Height is limiting factor
            new_height = self.THUMBNAIL_HEIGHT
            new_width = int(new_height * aspect_ratio)

        # Resize image
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Create canvas with target dimensions
        canvas = Image.new('RGB', (self.THUMBNAIL_WIDTH, self.THUMBNAIL_HEIGHT), color='#f3f4f6')

        # Paste resized image centered
        x_offset = (self.THUMBNAIL_WIDTH - new_width) // 2
        y_offset = (self.THUMBNAIL_HEIGHT - new_height) // 2
        canvas.paste(resized, (x_offset, y_offset))

        return canvas

    async def _create_fallback_thumbnail(
        self,
        source_id: str,
        title: str
    ) -> Optional[str]:
        """
        Create simple fallback thumbnail with PDF icon and title.

        Used when first-page extraction fails.

        Args:
            source_id: Source identifier
            title: Document title

        Returns:
            Relative path to saved thumbnail
        """
        try:
            # Create blank canvas
            image = Image.new('RGB', (self.THUMBNAIL_WIDTH, self.THUMBNAIL_HEIGHT), color='#e5e7eb')
            draw = ImageDraw.Draw(image)

            # Draw PDF icon symbol (simple rectangle with lines)
            icon_size = 60
            icon_x = self.THUMBNAIL_WIDTH // 2 - icon_size // 2
            icon_y = 30

            # Document shape
            draw.rectangle(
                [icon_x, icon_y, icon_x + icon_size, icon_y + icon_size + 20],
                fill='#f3f4f6',
                outline='#9ca3af',
                width=2
            )

            # Folded corner
            corner_size = 15
            draw.polygon(
                [
                    (icon_x + icon_size - corner_size, icon_y),
                    (icon_x + icon_size, icon_y + corner_size),
                    (icon_x + icon_size, icon_y)
                ],
                fill='#d1d5db',
                outline='#9ca3af'
            )

            # Lines representing text
            line_y = icon_y + 15
            for i in range(4):
                draw.line(
                    [(icon_x + 10, line_y + i * 12), (icon_x + icon_size - 10, line_y + i * 12)],
                    fill='#9ca3af',
                    width=2
                )

            # Add title text (truncated if too long)
            title_text = title[:30] + "..." if len(title) > 30 else title
            try:
                # Try to use a system font
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            except:
                # Fallback to default font
                font = ImageFont.load_default()

            # Draw title below icon
            text_bbox = draw.textbbox((0, 0), title_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = self.THUMBNAIL_WIDTH // 2 - text_width // 2
            text_y = icon_y + icon_size + 35

            draw.text((text_x, text_y), title_text, fill='#374151', font=font)

            # Add "PDF" label
            pdf_label = "PDF"
            label_bbox = draw.textbbox((0, 0), pdf_label, font=font)
            label_width = label_bbox[2] - label_bbox[0]
            label_x = self.THUMBNAIL_WIDTH // 2 - label_width // 2
            label_y = text_y + 20

            draw.text((label_x, label_y), pdf_label, fill='#6b7280', font=font)

            # Save to bytes
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=self.THUMBNAIL_QUALITY)

            # Save to file storage
            thumbnail_path = self.file_storage.save_thumbnail(
                buffered.getvalue(),
                source_id,
                format="jpg"
            )

            logger.info(f"Created fallback thumbnail for {source_id}")
            return thumbnail_path

        except Exception as e:
            logger.error(f"Failed to create fallback thumbnail for {source_id}: {e}")
            return None


# Singleton instance
_thumbnail_generator_instance: Optional[ThumbnailGeneratorService] = None


def get_thumbnail_generator_service() -> ThumbnailGeneratorService:
    """Get or create singleton ThumbnailGeneratorService instance."""
    global _thumbnail_generator_instance
    if _thumbnail_generator_instance is None:
        _thumbnail_generator_instance = ThumbnailGeneratorService()
    return _thumbnail_generator_instance
