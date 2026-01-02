"""
Health Analyzer Service

Uses Claude CLI with vision capabilities to analyze video frames for
observable health-related features. This is an EDUCATIONAL tool only.
"""

import json
import logging
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
import uuid

from app.models.health_observation import (
    BodyRegion,
    HealthObservation,
    HealthObservationResult,
    FrameAnalysis,
    ExtractedFrame,
    HumanDetectionResult,
    ObservationSeverity,
    CLAUDE_HEALTH_PROMPT,
    HEALTH_DISCLAIMER,
    format_timestamp,
    group_observations_by_region,
)
from app.services.frame_extractor import FrameExtractor
from app.services.human_detector import HumanDetector

logger = logging.getLogger(__name__)


class HealthAnalyzer:
    """Analyzes video frames for health-related observations using Claude vision."""

    def __init__(self):
        self.claude_path = shutil.which("claude")
        self.frame_extractor = FrameExtractor()

    def is_available(self) -> bool:
        """Check if Claude CLI is available."""
        return self.claude_path is not None

    async def analyze_video(
        self,
        video_id: str,
        video_title: str = "",
        interval_seconds: int = 30,
        max_frames: int = 20
    ) -> HealthObservationResult:
        """
        Full pipeline: extract frames -> detect humans -> analyze -> cleanup.

        Args:
            video_id: YouTube video ID
            video_title: Video title for context
            interval_seconds: Seconds between frame extractions
            max_frames: Maximum frames to analyze

        Returns:
            HealthObservationResult with all observations
        """
        start_time = datetime.now()
        video_dir = None
        all_observations: List[HealthObservation] = []
        frame_analyses: List[FrameAnalysis] = []

        try:
            # Step 1: Extract frames
            logger.info(f"Extracting frames from video {video_id}...")
            frames, video_dir = await self.frame_extractor.extract_frames(
                video_id=video_id,
                interval_seconds=interval_seconds,
                max_frames=max_frames
            )
            frames_extracted = len(frames)
            logger.info(f"Extracted {frames_extracted} frames")

            if not frames:
                return self._empty_result(video_id, video_title, start_time)

            # Step 2: Filter for human presence
            logger.info("Detecting humans in frames...")
            with HumanDetector() as detector:
                human_frames = detector.filter_frames(frames, require_face=False)

            frames_with_humans = len(human_frames)
            logger.info(f"Found {frames_with_humans} frames with humans")

            if not human_frames:
                return self._empty_result(
                    video_id, video_title, start_time,
                    frames_extracted=frames_extracted,
                    note="No human presence detected in video frames"
                )

            # Step 3: Analyze each frame with Claude vision
            logger.info("Analyzing frames with Claude vision...")
            for frame, detection in human_frames:
                frame_analysis = await self._analyze_frame(
                    frame_path=Path(frame.frame_path),
                    timestamp=frame.timestamp,
                    body_regions=detection.body_regions,
                    video_title=video_title
                )
                if frame_analysis:
                    frame_analyses.append(frame_analysis)
                    all_observations.extend(frame_analysis.observations)

            frames_analyzed = len(frame_analyses)
            logger.info(f"Analyzed {frames_analyzed} frames, found {len(all_observations)} observations")

            # Step 4: Build result
            duration = (datetime.now() - start_time).total_seconds()

            # Group observations by body region
            observations_by_region = group_observations_by_region(all_observations)

            # Generate summary
            summary = self._generate_summary(all_observations, frames_analyzed)

            return HealthObservationResult(
                video_id=video_id,
                video_title=video_title,
                video_url=f"https://www.youtube.com/watch?v={video_id}",
                frames_extracted=frames_extracted,
                frames_with_humans=frames_with_humans,
                frames_analyzed=frames_analyzed,
                observations=all_observations,
                summary=summary,
                observations_by_region=observations_by_region,
                frame_analyses=frame_analyses,
                limitations=self._get_standard_limitations(),
                disclaimer=HEALTH_DISCLAIMER,
                analysis_duration_seconds=duration,
                analyzed_at=datetime.now().isoformat(),
                interval_seconds=interval_seconds
            )

        finally:
            # Always cleanup temp files
            if video_dir:
                self.frame_extractor.cleanup(video_dir)
                logger.info("Cleaned up temporary files")

    async def _analyze_frame(
        self,
        frame_path: Path,
        timestamp: float,
        body_regions: List[BodyRegion],
        video_title: str
    ) -> Optional[FrameAnalysis]:
        """
        Analyze a single frame using Claude vision.

        Uses Claude CLI with file path - Claude Code can read images directly.
        """
        if not self.claude_path:
            logger.error("Claude CLI not available")
            return None

        try:
            # Format the prompt with absolute file path for Claude to read
            regions_str = ", ".join(r.value for r in body_regions) if body_regions else "unknown"
            formatted_time = format_timestamp(timestamp)

            prompt = CLAUDE_HEALTH_PROMPT.format(
                timestamp=timestamp,
                formatted_time=formatted_time,
                regions=regions_str,
                video_title=video_title or "Unknown"
            )

            # Instruct Claude to read the image file directly
            # Claude Code's Read tool can handle image files natively
            full_prompt = f"""Please analyze the image at this path: {frame_path}

Read the image file and then provide your analysis.

{prompt}"""

            cmd = [
                self.claude_path,
                "--print",
                "--permission-mode", "bypassPermissions",
                "--model", "claude-sonnet-4-20250514",  # Sonnet for vision (faster, cheaper)
                "--max-turns", "3",  # Allow turns for: read image -> analyze -> respond
                "--allowedTools", "Read",  # Only allow Read tool for image access
            ]

            logger.debug(f"Analyzing frame at {formatted_time}...")

            result = subprocess.run(
                cmd,
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=180  # 3 minute timeout per frame (needs to read + analyze)
            )

            if result.returncode != 0:
                logger.error(f"Claude CLI error: {result.stderr}")
                return None

            output = result.stdout.strip()

            # Parse JSON response
            response = self._parse_json_response(output)
            if not response:
                return None

            # Convert to FrameAnalysis
            frame_id = str(uuid.uuid4())[:8]
            observations = []

            for obs_data in response.get("observations", []):
                try:
                    obs_id = str(uuid.uuid4())[:8]
                    observations.append(HealthObservation(
                        observation_id=obs_id,
                        timestamp=timestamp,
                        body_region=BodyRegion(obs_data.get("body_region", "other")),
                        observation=obs_data.get("observation", ""),
                        reasoning=obs_data.get("reasoning", ""),
                        confidence=float(obs_data.get("confidence", 0.5)),
                        limitations=obs_data.get("limitations", []),
                        severity=ObservationSeverity(obs_data.get("severity", "informational")),
                        related_conditions=obs_data.get("related_conditions", []),
                        references=obs_data.get("references", [])
                    ))
                except Exception as e:
                    logger.warning(f"Failed to parse observation: {e}")

            return FrameAnalysis(
                frame_id=frame_id,
                timestamp=timestamp,
                humans_detected=1,
                body_regions_visible=body_regions,
                observations=observations,
                image_quality_notes=response.get("image_quality_notes", [])
            )

        except subprocess.TimeoutExpired:
            logger.error(f"Frame analysis timed out for {frame_path}")
            return None
        except Exception as e:
            logger.error(f"Error analyzing frame: {e}")
            return None

    def _parse_json_response(self, output: str) -> Optional[dict]:
        """Parse JSON from Claude's response, handling markdown wrappers."""
        # Remove markdown code blocks if present
        if output.startswith("```json"):
            output = output[7:]
        if output.startswith("```"):
            output = output[3:]
        if output.endswith("```"):
            output = output[:-3]
        output = output.strip()

        try:
            return json.loads(output)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            logger.debug(f"Raw output: {output[:500]}")
            return None

    def _empty_result(
        self,
        video_id: str,
        video_title: str,
        start_time: datetime,
        frames_extracted: int = 0,
        note: str = ""
    ) -> HealthObservationResult:
        """Create an empty result for when no analysis could be performed."""
        duration = (datetime.now() - start_time).total_seconds()
        return HealthObservationResult(
            video_id=video_id,
            video_title=video_title,
            video_url=f"https://www.youtube.com/watch?v={video_id}",
            frames_extracted=frames_extracted,
            frames_with_humans=0,
            frames_analyzed=0,
            observations=[],
            summary=note or "No observations could be made from this video.",
            observations_by_region={},
            frame_analyses=[],
            limitations=self._get_standard_limitations(),
            disclaimer=HEALTH_DISCLAIMER,
            analysis_duration_seconds=duration,
            analyzed_at=datetime.now().isoformat()
        )

    def _generate_summary(
        self,
        observations: List[HealthObservation],
        frames_analyzed: int
    ) -> str:
        """Generate a summary of observations."""
        if not observations:
            return f"Analyzed {frames_analyzed} frames. No notable health-related observations were found."

        # Count by severity
        severity_counts = {s: 0 for s in ObservationSeverity}
        region_counts: dict = {}

        for obs in observations:
            severity_counts[obs.severity] += 1
            region = obs.body_region.value
            region_counts[region] = region_counts.get(region, 0) + 1

        # Build summary
        parts = [f"Analyzed {frames_analyzed} frames with {len(observations)} observations."]

        if severity_counts[ObservationSeverity.CONSIDER_CHECKUP] > 0:
            parts.append(
                f"{severity_counts[ObservationSeverity.CONSIDER_CHECKUP]} observation(s) may warrant professional evaluation."
            )

        regions_mentioned = ", ".join(f"{k} ({v})" for k, v in sorted(region_counts.items(), key=lambda x: -x[1]))
        parts.append(f"Body regions observed: {regions_mentioned}.")

        parts.append("Remember: This is an educational tool only, not medical advice.")

        return " ".join(parts)

    def _get_standard_limitations(self) -> List[str]:
        """Get standard limitations that apply to all analyses."""
        return [
            "Single video frames cannot capture dynamic signs (tremors, gait)",
            "Lighting conditions significantly affect skin color perception",
            "Camera quality and angle may distort proportions",
            "Makeup, filters, or video processing may mask features",
            "No baseline comparison - observations are from a single point in time",
            "AI analysis has inherent limitations and may produce false positives/negatives"
        ]


# Singleton instance
_health_analyzer: Optional[HealthAnalyzer] = None


def get_health_analyzer() -> HealthAnalyzer:
    """Get or create the health analyzer singleton."""
    global _health_analyzer
    if _health_analyzer is None:
        _health_analyzer = HealthAnalyzer()
    return _health_analyzer
