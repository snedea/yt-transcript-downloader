"""
Rhetorical Analysis Service

Orchestrates the analysis of transcripts for rhetorical techniques,
combining AI analysis with web search verification for quotes.
"""

import time
import logging
from typing import Dict, List, Any, Optional

from app.services.openai_service import OpenAIService
from app.services.web_search import WebSearchService, get_web_search_service
from app.models.analysis import (
    AnalysisRequest,
    AnalysisResult,
    TechniqueMatch,
    QuoteMatch,
    PillarScore,
    TechniqueSummary,
    score_to_grade
)
from app.data.rhetorical_toolkit import RHETORICAL_TECHNIQUES, RHETORICAL_PILLARS

logger = logging.getLogger(__name__)


class RhetoricalAnalysisService:
    """
    Service for analyzing transcripts for rhetorical techniques.

    Combines:
    - OpenAI GPT-4 for technique detection and scoring
    - SearXNG web search for quote verification
    """

    def __init__(self):
        """Initialize the analysis service."""
        self.openai_service = OpenAIService()
        self.web_search_service = get_web_search_service()

    async def analyze_transcript(
        self,
        request: AnalysisRequest
    ) -> AnalysisResult:
        """
        Perform complete rhetorical analysis on a transcript.

        Args:
            request: AnalysisRequest with transcript and options

        Returns:
            AnalysisResult with complete analysis
        """
        start_time = time.time()

        # Count words in transcript
        word_count = len(request.transcript.split())

        # Step 1: Get AI analysis from OpenAI
        logger.info(f"Starting rhetorical analysis for transcript ({word_count} words)")

        ai_result = await self.openai_service.analyze_rhetoric(
            transcript=request.transcript,
            video_title=request.video_title,
            video_author=request.video_author
        )

        if not ai_result["success"]:
            raise ValueError(f"AI analysis failed: {ai_result.get('error', 'Unknown error')}")

        analysis_data = ai_result["analysis"]
        tokens_used = ai_result["tokens_used"]

        # Step 2: Process technique matches
        technique_matches = self._process_technique_matches(
            analysis_data.get("technique_matches", []),
            request.transcript_data
        )

        # Step 3: Create technique summary
        technique_summary = self._create_technique_summary(technique_matches)

        # Step 4: Process pillar scores
        pillar_scores = self._process_pillar_scores(
            analysis_data.get("pillar_scores", [])
        )

        # Step 5: Process and verify quotes
        quote_matches = await self._process_quotes(
            analysis_data.get("potential_quotes", []),
            request.verify_quotes,
            request.transcript_data
        )

        # Calculate duration
        duration = time.time() - start_time

        # Build the result
        overall_score = analysis_data.get("overall_score", 0)

        result = AnalysisResult(
            overall_score=overall_score,
            overall_grade=score_to_grade(overall_score),
            pillar_scores=pillar_scores,
            technique_matches=technique_matches,
            technique_summary=technique_summary,
            total_techniques_found=len(technique_matches),
            unique_techniques_used=len(set(m.technique_id for m in technique_matches)),
            quote_matches=quote_matches,
            total_quotes_found=len(quote_matches),
            verified_quotes=sum(1 for q in quote_matches if q.verified),
            executive_summary=analysis_data.get("executive_summary", ""),
            strengths=analysis_data.get("strengths", []),
            areas_for_improvement=analysis_data.get("areas_for_improvement", []),
            tokens_used=tokens_used,
            analysis_duration_seconds=round(duration, 2),
            transcript_word_count=word_count
        )

        logger.info(
            f"Analysis complete: score={overall_score}, "
            f"techniques={len(technique_matches)}, "
            f"quotes={len(quote_matches)}, "
            f"duration={duration:.2f}s"
        )

        return result

    def _process_technique_matches(
        self,
        raw_matches: List[Dict[str, Any]],
        transcript_data: Optional[List[dict]]
    ) -> List[TechniqueMatch]:
        """
        Process raw technique matches from AI analysis.

        Maps phrases to timestamps if transcript_data is available.
        """
        matches = []

        for raw in raw_matches:
            # Skip if raw is not a dict (defensive handling for unexpected GPT output)
            if not isinstance(raw, dict):
                logger.warning(f"Skipping non-dict technique match: {type(raw)}")
                continue
            # Get technique info from our toolkit
            technique_id = raw.get("technique_id", "unknown")
            technique_info = RHETORICAL_TECHNIQUES.get(technique_id, {})

            # Try to find timestamp for this phrase
            start_time, end_time = None, None
            if transcript_data:
                start_time, end_time = self._find_phrase_timestamp(
                    raw.get("phrase", ""),
                    transcript_data
                )

            match = TechniqueMatch(
                technique_id=technique_id,
                technique_name=raw.get("technique_name", technique_info.get("name", technique_id.title())),
                category=raw.get("category", technique_info.get("category", "other")),
                phrase=raw.get("phrase", ""),
                start_time=start_time,
                end_time=end_time,
                explanation=raw.get("explanation", ""),
                strength=raw.get("strength", "moderate"),
                context=raw.get("context")
            )
            matches.append(match)

        return matches

    def _create_technique_summary(
        self,
        matches: List[TechniqueMatch]
    ) -> List[TechniqueSummary]:
        """
        Create a summary of techniques used, grouped by technique type.
        """
        technique_counts: Dict[str, Dict[str, Any]] = {}

        for match in matches:
            tid = match.technique_id
            if tid not in technique_counts:
                technique_counts[tid] = {
                    "technique_id": tid,
                    "technique_name": match.technique_name,
                    "category": match.category,
                    "count": 0,
                    "strongest_example": "",
                    "strongest_strength": ""
                }

            technique_counts[tid]["count"] += 1

            # Update strongest example
            strength_order = {"strong": 3, "moderate": 2, "subtle": 1}
            current_strength = strength_order.get(technique_counts[tid]["strongest_strength"], 0)
            new_strength = strength_order.get(match.strength, 0)

            if new_strength > current_strength or not technique_counts[tid]["strongest_example"]:
                technique_counts[tid]["strongest_example"] = match.phrase
                technique_counts[tid]["strongest_strength"] = match.strength

        return [
            TechniqueSummary(
                technique_id=data["technique_id"],
                technique_name=data["technique_name"],
                category=data["category"],
                count=data["count"],
                strongest_example=data["strongest_example"]
            )
            for data in sorted(
                technique_counts.values(),
                key=lambda x: x["count"],
                reverse=True
            )
        ]

    def _process_pillar_scores(
        self,
        raw_scores: List[Dict[str, Any]]
    ) -> List[PillarScore]:
        """
        Process raw pillar scores from AI analysis.
        """
        scores = []

        # Ensure we have all four pillars - filter out non-dict items
        pillar_map = {}
        for s in raw_scores:
            if isinstance(s, dict) and "pillar" in s:
                pillar_map[s.get("pillar")] = s
            else:
                logger.warning(f"Skipping invalid pillar score: {type(s)}")

        for pillar_id in ["logos", "pathos", "ethos", "kairos"]:
            raw = pillar_map.get(pillar_id, {})
            pillar_info = RHETORICAL_PILLARS.get(pillar_id, {})

            score = PillarScore(
                pillar=pillar_id,
                pillar_name=pillar_info.get("name", pillar_id.title()),
                score=raw.get("score", 0),
                explanation=raw.get("explanation", f"No analysis available for {pillar_id}"),
                contributing_techniques=raw.get("contributing_techniques", []),
                key_examples=raw.get("key_examples", [])
            )
            scores.append(score)

        return scores

    async def _process_quotes(
        self,
        raw_quotes: List[Dict[str, Any]],
        verify_quotes: bool,
        transcript_data: Optional[List[dict]]
    ) -> List[QuoteMatch]:
        """
        Process potential quotes and optionally verify them via web search.
        """
        quotes = []

        for raw in raw_quotes:
            # Skip if raw is not a dict (defensive handling for unexpected GPT output)
            if not isinstance(raw, dict):
                logger.warning(f"Skipping non-dict quote match: {type(raw)}")
                continue

            phrase = raw.get("phrase", "")

            # Find timestamp
            start_time = None
            if transcript_data:
                start_time, _ = self._find_phrase_timestamp(phrase, transcript_data)

            # Verify via web search if enabled
            verified = False
            verification_details = None
            source = raw.get("likely_source")
            source_type = raw.get("source_type")

            if verify_quotes and phrase:
                try:
                    attribution = await self.web_search_service.verify_quote(phrase)
                    verified = attribution.verified
                    verification_details = attribution.verification_details

                    # Update source if web search found something more specific
                    if attribution.source and (not source or attribution.confidence > raw.get("confidence", 0)):
                        source = attribution.source
                        source_type = attribution.source_type
                except Exception as e:
                    logger.warning(f"Failed to verify quote: {e}")
                    verification_details = f"Verification failed: {str(e)}"

            quote = QuoteMatch(
                phrase=phrase,
                is_quote=raw.get("confidence", 0) > 0.5,
                confidence=raw.get("confidence", 0.5),
                source=source,
                source_type=source_type,
                verified=verified,
                verification_details=verification_details,
                start_time=start_time
            )
            quotes.append(quote)

        return quotes

    def _find_phrase_timestamp(
        self,
        phrase: str,
        transcript_data: List[dict]
    ) -> tuple[Optional[float], Optional[float]]:
        """
        Find the timestamp for a phrase in the transcript data.

        Returns (start_time, end_time) or (None, None) if not found.
        """
        if not phrase or not transcript_data:
            return None, None

        # Normalize the phrase for matching
        phrase_lower = phrase.lower().strip()
        phrase_words = phrase_lower.split()[:5]  # Use first 5 words for matching

        for segment in transcript_data:
            # Skip if segment is not a dict
            if not isinstance(segment, dict):
                continue
            segment_text = segment.get("text", "").lower()

            # Check if the phrase starts in this segment
            if phrase_words and phrase_words[0] in segment_text:
                # More thorough check
                if any(word in segment_text for word in phrase_words[:3]):
                    start = segment.get("start", 0)
                    duration = segment.get("duration", 5)
                    return start, start + duration

        return None, None

    async def check_services(self) -> Dict[str, bool]:
        """
        Check if required services are available.
        """
        openai_available = self.openai_service.is_available()
        searxng_available = await self.web_search_service.check_connection()

        return {
            "openai": openai_available,
            "searxng": searxng_available,
            "ready": openai_available  # Only OpenAI is required
        }


# Singleton instance
_analysis_service: Optional[RhetoricalAnalysisService] = None


def get_analysis_service() -> RhetoricalAnalysisService:
    """Get or create the analysis service singleton."""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = RhetoricalAnalysisService()
    return _analysis_service
