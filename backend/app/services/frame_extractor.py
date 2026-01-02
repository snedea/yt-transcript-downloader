"""
Frame Extraction Service

Extracts frames from YouTube videos at regular intervals using yt-dlp and ffmpeg.
Frames are saved to a temporary directory and cleaned up after analysis.
"""

import asyncio
import logging
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional
import uuid

from app.models.health_observation import ExtractedFrame

logger = logging.getLogger(__name__)


class FrameExtractor:
    """Extracts frames from YouTube videos using yt-dlp and ffmpeg."""

    def __init__(self, temp_base_dir: Path = Path("/tmp/yt-health")):
        self.temp_base_dir = temp_base_dir
        self.temp_base_dir.mkdir(parents=True, exist_ok=True)

    def _get_video_dir(self, video_id: str) -> Path:
        """Get temp directory for a specific video."""
        # Add a UUID to allow multiple simultaneous analyses of same video
        unique_id = str(uuid.uuid4())[:8]
        video_dir = self.temp_base_dir / f"{video_id}_{unique_id}"
        video_dir.mkdir(parents=True, exist_ok=True)
        return video_dir

    async def extract_frames(
        self,
        video_id: str,
        interval_seconds: int = 30,
        max_frames: int = 20
    ) -> tuple[List[ExtractedFrame], Path]:
        """
        Download video and extract frames at intervals.

        Args:
            video_id: YouTube video ID
            interval_seconds: Extract a frame every N seconds
            max_frames: Maximum number of frames to extract

        Returns:
            Tuple of (list of extracted frames, temp directory path)
            Caller is responsible for cleaning up temp directory after use.
        """
        video_dir = self._get_video_dir(video_id)
        video_path = video_dir / "video.mp4"
        frames_dir = video_dir / "frames"
        frames_dir.mkdir(exist_ok=True)

        try:
            # Step 1: Download video with yt-dlp
            logger.info(f"Downloading video {video_id}...")
            await self._download_video(video_id, video_path)

            if not video_path.exists():
                raise RuntimeError(f"Failed to download video {video_id}")

            # Step 2: Get video duration
            duration = await self._get_video_duration(video_path)
            logger.info(f"Video duration: {duration:.1f} seconds")

            # Step 3: Calculate frame timestamps
            timestamps = self._calculate_timestamps(duration, interval_seconds, max_frames)
            logger.info(f"Extracting {len(timestamps)} frames at timestamps: {timestamps[:5]}...")

            # Step 4: Extract frames at each timestamp
            frames = await self._extract_frames_at_timestamps(
                video_path, frames_dir, timestamps
            )

            logger.info(f"Extracted {len(frames)} frames to {frames_dir}")
            return frames, video_dir

        except Exception as e:
            # Clean up on error
            logger.error(f"Frame extraction failed: {e}")
            self.cleanup(video_dir)
            raise

    async def _download_video(self, video_id: str, output_path: Path) -> None:
        """Download video using yt-dlp."""
        url = f"https://www.youtube.com/watch?v={video_id}"

        # Use format that's good for frame extraction (mp4, reasonable quality)
        cmd = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]/best",
            "--merge-output-format", "mp4",
            "-o", str(output_path),
            "--no-playlist",
            "--remote-components", "ejs:github",  # Required for YouTube JS challenges
            "--quiet",
            url
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown error"
            raise RuntimeError(f"yt-dlp failed: {error_msg}")

    async def _get_video_duration(self, video_path: Path) -> float:
        """Get video duration in seconds using ffprobe."""
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"ffprobe failed: {stderr.decode()}")

        return float(stdout.decode().strip())

    def _calculate_timestamps(
        self,
        duration: float,
        interval_seconds: int,
        max_frames: int
    ) -> List[float]:
        """Calculate which timestamps to extract frames from."""
        timestamps = []
        current_time = 0.0

        # Skip first few seconds (often just intro/logo)
        current_time = min(5.0, duration * 0.05)

        while current_time < duration and len(timestamps) < max_frames:
            timestamps.append(current_time)
            current_time += interval_seconds

        return timestamps

    async def _extract_frames_at_timestamps(
        self,
        video_path: Path,
        frames_dir: Path,
        timestamps: List[float]
    ) -> List[ExtractedFrame]:
        """Extract frames at specific timestamps using ffmpeg."""
        frames = []

        for idx, timestamp in enumerate(timestamps):
            frame_path = frames_dir / f"frame_{idx:04d}.jpg"

            # Use ffmpeg to extract a single frame at the timestamp
            cmd = [
                "ffmpeg",
                "-ss", str(timestamp),
                "-i", str(video_path),
                "-vframes", "1",
                "-q:v", "2",  # High quality JPEG
                "-y",  # Overwrite if exists
                str(frame_path)
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await process.communicate()

            if frame_path.exists():
                frames.append(ExtractedFrame(
                    frame_path=str(frame_path),
                    timestamp=timestamp,
                    frame_index=idx
                ))

        return frames

    def cleanup(self, video_dir: Path) -> None:
        """Remove all temp files for a video."""
        if video_dir.exists():
            try:
                shutil.rmtree(video_dir)
                logger.info(f"Cleaned up temp directory: {video_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {video_dir}: {e}")

    def cleanup_all(self) -> None:
        """Remove all temp directories (for maintenance)."""
        if self.temp_base_dir.exists():
            for item in self.temp_base_dir.iterdir():
                if item.is_dir():
                    self.cleanup(item)
