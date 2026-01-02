"""
Health Analyzer Service

Uses Claude CLI or OpenAI GPT-4o with vision capabilities to analyze video frames for
observable health-related features. This is an EDUCATIONAL tool only.

Supports two providers (like Discovery):
1. Claude CLI - Primary (uses existing subscription)
2. OpenAI GPT-4o - Fallback with vision support
"""

import base64
import json
import logging
import os
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import uuid

from openai import OpenAI

from app.config import settings
from app.models.health_observation import (
    BodyRegion,
    HealthObservation,
    HealthObservationResult,
    FrameAnalysis,
    ObservationSeverity,
    CLAUDE_HEALTH_PROMPT,
    HEALTH_DISCLAIMER,
    format_timestamp,
    group_observations_by_region,
)
from app.services.frame_extractor import FrameExtractor
from app.services.human_detector import HumanDetector

logger = logging.getLogger(__name__)

# Provider preference: "claude", "openai", or "auto" (claude first, then openai)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto")


class HealthAnalyzer:
    """Analyzes video frames for health-related observations using vision AI."""

    def __init__(self):
        self.claude_path = shutil.which("claude")
        self.frame_extractor = FrameExtractor()

        # Initialize OpenAI client if API key is available
        if settings.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.openai_client = None

        self.provider = LLM_PROVIDER
        logger.info(f"Health analyzer initialized with provider preference: {self.provider}")

    def is_available(self) -> bool:
        """Check if any vision provider is available."""
        if self.provider == "claude":
            return self.claude_path is not None
        elif self.provider == "openai":
            return self.openai_client is not None
        else:  # auto
            return self.claude_path is not None or self.openai_client is not None

    def _get_active_provider(self) -> str:
        """Determine which provider to use."""
        if self.provider == "claude":
            return "claude" if self.claude_path else None
        elif self.provider == "openai":
            return "openai" if self.openai_client else None
        else:  # auto - try claude first, then openai
            if self.claude_path:
                return "claude"
            if self.openai_client:
                return "openai"
            return None

    async def analyze_video(
        self,
        video_id: str,
        video_title: str = "",
        interval_seconds: int = 30,
        max_frames: int = 20
    ) -> HealthObservationResult:
        """
        Full pipeline: extract frames -> detect humans -> analyze -> cleanup.
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

            # Step 3: Analyze each frame with vision AI
            provider = self._get_active_provider()
            if not provider:
                return self._empty_result(
                    video_id, video_title, start_time,
                    frames_extracted=frames_extracted,
                    frames_with_humans=frames_with_humans,
                    note="No vision provider available (Claude CLI or OpenAI API key required)"
                )

            logger.info(f"Analyzing frames with {provider} vision...")
            for frame, detection in human_frames:
                frame_analysis = await self._analyze_frame(
                    frame_path=Path(frame.frame_path),
                    timestamp=frame.timestamp,
                    body_regions=detection.body_regions,
                    video_title=video_title,
                    provider=provider
                )
                if frame_analysis:
                    frame_analyses.append(frame_analysis)
                    all_observations.extend(frame_analysis.observations)

            frames_analyzed = len(frame_analyses)
            logger.info(f"Analyzed {frames_analyzed} frames, found {len(all_observations)} observations")

            # Step 4: Build result
            duration = (datetime.now() - start_time).total_seconds()
            observations_by_region = group_observations_by_region(all_observations)
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
                interval_seconds=interval_seconds,
                model_used="gpt-4o" if provider == "openai" else "claude-sonnet-4-20250514"
            )

        finally:
            if video_dir:
                self.frame_extractor.cleanup(video_dir)
                logger.info("Cleaned up temporary files")

    async def _analyze_frame(
        self,
        frame_path: Path,
        timestamp: float,
        body_regions: List[BodyRegion],
        video_title: str,
        provider: str
    ) -> Optional[FrameAnalysis]:
        """Analyze a single frame using the specified vision provider."""

        # Try primary provider, fall back if it fails
        if provider == "claude":
            result = await self._analyze_frame_claude(frame_path, timestamp, body_regions, video_title)
            if result:
                return result
            # Fall back to OpenAI if in auto mode
            if self.provider == "auto" and self.openai_client:
                logger.info("Claude failed, falling back to OpenAI...")
                return await self._analyze_frame_openai(frame_path, timestamp, body_regions, video_title)
            return None
        else:
            return await self._analyze_frame_openai(frame_path, timestamp, body_regions, video_title)

    async def _analyze_frame_claude(
        self,
        frame_path: Path,
        timestamp: float,
        body_regions: List[BodyRegion],
        video_title: str
    ) -> Optional[FrameAnalysis]:
        """Analyze frame using Claude CLI."""
        if not self.claude_path:
            return None

        try:
            regions_str = ", ".join(r.value for r in body_regions) if body_regions else "unknown"
            formatted_time = format_timestamp(timestamp)

            prompt = CLAUDE_HEALTH_PROMPT.format(
                timestamp=timestamp,
                formatted_time=formatted_time,
                regions=regions_str,
                video_title=video_title or "Unknown"
            )

            full_prompt = f"""Please analyze the image at this path: {frame_path}

Read the image file and then provide your analysis.

{prompt}"""

            cmd = [
                self.claude_path,
                "--print",
                "--permission-mode", "bypassPermissions",
                "--model", "claude-sonnet-4-20250514",
                "--max-turns", "3",
                "--allowedTools", "Read",
            ]

            logger.debug(f"Analyzing frame at {formatted_time} with Claude...")

            result = subprocess.run(
                cmd,
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=180
            )

            if result.returncode != 0:
                logger.error(f"Claude CLI error: {result.stderr}")
                return None

            output = result.stdout.strip()
            response = self._parse_json_response(output)
            if not response:
                return None

            return self._build_frame_analysis(response, timestamp, body_regions)

        except subprocess.TimeoutExpired:
            logger.error(f"Claude frame analysis timed out for {frame_path}")
            return None
        except Exception as e:
            logger.error(f"Error analyzing frame with Claude: {e}")
            return None

    async def _analyze_frame_openai(
        self,
        frame_path: Path,
        timestamp: float,
        body_regions: List[BodyRegion],
        video_title: str
    ) -> Optional[FrameAnalysis]:
        """Analyze frame using OpenAI GPT-4o vision."""
        if not self.openai_client:
            return None

        try:
            regions_str = ", ".join(r.value for r in body_regions) if body_regions else "unknown"
            formatted_time = format_timestamp(timestamp)

            prompt = CLAUDE_HEALTH_PROMPT.format(
                timestamp=timestamp,
                formatted_time=formatted_time,
                regions=regions_str,
                video_title=video_title or "Unknown"
            )

            # Read and encode image as base64
            with open(frame_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            logger.debug(f"Analyzing frame at {formatted_time} with OpenAI GPT-4o...")

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            output = response.choices[0].message.content
            parsed = self._parse_json_response(output)
            if not parsed:
                return None

            return self._build_frame_analysis(parsed, timestamp, body_regions)

        except Exception as e:
            logger.error(f"Error analyzing frame with OpenAI: {e}")
            return None

    def _build_frame_analysis(
        self,
        response: dict,
        timestamp: float,
        body_regions: List[BodyRegion]
    ) -> FrameAnalysis:
        """Convert parsed response to FrameAnalysis."""
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

    def _parse_json_response(self, output: str) -> Optional[dict]:
        """Parse JSON from response, handling markdown wrappers."""
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
        frames_with_humans: int = 0,
        note: str = ""
    ) -> HealthObservationResult:
        """Create an empty result for when no analysis could be performed."""
        duration = (datetime.now() - start_time).total_seconds()
        return HealthObservationResult(
            video_id=video_id,
            video_title=video_title,
            video_url=f"https://www.youtube.com/watch?v={video_id}",
            frames_extracted=frames_extracted,
            frames_with_humans=frames_with_humans,
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

        severity_counts = {s: 0 for s in ObservationSeverity}
        region_counts: dict = {}

        for obs in observations:
            severity_counts[obs.severity] += 1
            region = obs.body_region.value
            region_counts[region] = region_counts.get(region, 0) + 1

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
