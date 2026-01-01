"""
Content Summary Service

Handles the GPT-4o analysis for extracting key concepts, TLDR,
technical details, and action items from YouTube transcripts.
"""

import json
import logging
import time
from typing import Optional

from openai import OpenAI, OpenAIError

from app.config import settings
from app.models.summary_analysis import (
    ContentSummaryRequest,
    ContentSummaryResult,
    ContentType,
    TechnicalCategory,
    Priority,
    KeyConcept,
    TechnicalDetail,
    ActionItem,
    KeyMoment,
)

logger = logging.getLogger(__name__)


SUMMARY_SYSTEM_PROMPT = """You are an expert content analyst specializing in extracting structured, actionable information from video transcripts. Your goal is to create comprehensive summaries optimized for note-taking and knowledge management.

## CONTENT TYPE DETECTION

First, identify the content type from these categories:
- programming_technical: Code tutorials, software development, tech explanations, system design
- tutorial_howto: Step-by-step guides, DIY instructions, how-to content
- news_current_events: News coverage, current events discussion, breaking stories
- educational: Academic content, concept explanations, learning material
- entertainment: Comedy, storytelling, vlogs, lifestyle content
- discussion_opinion: Debates, opinion pieces, commentary, analysis
- review: Product/service/media reviews, comparisons
- interview: Q&A format, conversations, podcasts with guests
- other: Content that doesn't fit above categories

## EXTRACTION GUIDELINES

### For ALL content types:
1. TLDR: Write 2-3 clear sentences that capture the main message
2. Key Concepts: Extract 3-7 main ideas, each with a brief explanation
3. Action Items: List practical takeaways the viewer should remember or do
4. Keywords: Generate 5-15 tags (lowercase, no spaces, use underscores)
5. Key Moments: Identify 3-5 significant points with approximate timestamps

### For programming_technical content, ALSO extract:
- Code snippets mentioned or demonstrated
- Libraries, frameworks, and packages with versions if mentioned
- Commands (terminal, git, npm, pip, etc.)
- Tools and APIs referenced
- Programming concepts explained

### For tutorial_howto content, ALSO focus on:
- Step-by-step instructions
- Materials or tools needed
- Common mistakes or warnings mentioned
- Tips and best practices

### For news_current_events content, ALSO extract:
- Key facts and claims
- Names, dates, and locations
- Sources mentioned
- Different perspectives presented

### For educational content, ALSO focus on:
- Core concepts and definitions
- Examples and analogies used
- Prerequisites mentioned
- Related topics for further learning

## TIMESTAMP HANDLING
- Estimate timestamps based on position in transcript
- Use format of seconds (e.g., 125 for 2:05)
- If transcript has timing data, try to correlate

## OUTPUT FORMAT
Return a JSON object with ALL required fields. Be thorough but concise.
Focus on extracting ACTIONABLE and MEMORABLE information."""


JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "content_type": {
            "type": "string",
            "enum": [
                "programming_technical", "tutorial_howto", "news_current_events",
                "educational", "entertainment", "discussion_opinion",
                "review", "interview", "other"
            ]
        },
        "content_type_confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "content_type_reasoning": {"type": "string"},
        "tldr": {"type": "string"},
        "key_concepts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "concept": {"type": "string"},
                    "explanation": {"type": "string"},
                    "importance": {"type": "string", "enum": ["high", "medium", "low"]},
                    "timestamp": {"type": ["number", "null"]}
                },
                "required": ["concept", "explanation"]
            }
        },
        "technical_details": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["code_snippet", "library", "framework", "command", "tool", "api", "concept"]
                    },
                    "name": {"type": "string"},
                    "description": {"type": ["string", "null"]},
                    "code": {"type": ["string", "null"]},
                    "timestamp": {"type": ["number", "null"]}
                },
                "required": ["category", "name"]
            }
        },
        "action_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "context": {"type": ["string", "null"]},
                    "priority": {"type": "string", "enum": ["high", "medium", "low"]}
                },
                "required": ["action"]
            }
        },
        "keywords": {
            "type": "array",
            "items": {"type": "string"}
        },
        "key_moments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "timestamp": {"type": "number"},
                    "title": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["timestamp", "title", "description"]
            }
        }
    },
    "required": [
        "content_type", "tldr", "key_concepts",
        "action_items", "keywords", "key_moments"
    ]
}


class ContentSummaryService:
    """
    Service for analyzing transcripts and extracting content summaries.

    Uses GPT-4o with a single comprehensive prompt for fast (~10s) analysis.
    """

    def __init__(self):
        """Initialize the service."""
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None

    async def analyze(self, request: ContentSummaryRequest) -> ContentSummaryResult:
        """
        Analyze transcript and extract content summary.

        Args:
            request: ContentSummaryRequest with transcript and metadata

        Returns:
            ContentSummaryResult with extracted information
        """
        start_time = time.time()

        if not self.client:
            raise ValueError("OpenAI API key not configured")

        transcript = request.transcript
        word_count = len(transcript.split())

        logger.info(f"Starting content summary analysis ({word_count} words)")

        # Build context from metadata
        context_parts = []
        if request.video_title:
            context_parts.append(f"Video Title: {request.video_title}")
        if request.video_author:
            context_parts.append(f"Channel/Author: {request.video_author}")

        context = "\n".join(context_parts) if context_parts else ""

        # Build transcript with timestamp markers if available
        transcript_with_times = transcript
        video_duration = 0

        if request.transcript_data:
            # Build transcript with timestamp markers at intervals
            lines = []
            last_marker = -60  # Start before 0 so first marker shows
            for segment in request.transcript_data:
                start = segment.get("start", 0)
                text = segment.get("text", "")
                # Add timestamp marker every ~60 seconds
                if start - last_marker >= 60:
                    mins = int(start // 60)
                    secs = int(start % 60)
                    lines.append(f"\n[{mins}:{secs:02d}] ")
                    last_marker = start
                lines.append(text)
                video_duration = max(video_duration, start + segment.get("duration", 0))
            transcript_with_times = " ".join(lines)

        duration_info = ""
        if video_duration > 0:
            duration_mins = int(video_duration // 60)
            duration_secs = int(video_duration % 60)
            duration_info = f"\nVideo Duration: ~{duration_mins}:{duration_secs:02d}"

        # Build user prompt
        user_prompt = f"""Analyze this transcript and extract a comprehensive content summary.

{context}{duration_info}

## TRANSCRIPT (with timestamp markers like [M:SS]):

{transcript_with_times}

Return a JSON object with: content_type, content_type_confidence, content_type_reasoning, tldr, key_concepts, technical_details (if applicable), action_items, keywords, and key_moments.

IMPORTANT: For key_moments timestamps, use the [M:SS] markers in the transcript to estimate when each moment occurs. Convert to seconds (e.g., [2:30] = 150 seconds). Distribute moments across the video duration."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )

            tokens_used = response.usage.total_tokens
            raw_content = response.choices[0].message.content

            logger.info(f"GPT response received ({tokens_used} tokens)")

            # Parse JSON response
            data = json.loads(raw_content)

            # Parse content type
            content_type = self._parse_content_type(data.get("content_type") or "other")

            # Parse key concepts (use `or []` to handle null values from GPT)
            key_concepts = self._parse_key_concepts(data.get("key_concepts") or [])

            # Parse technical details
            technical_details = self._parse_technical_details(
                data.get("technical_details") or []
            )
            has_technical = len(technical_details) > 0

            # Parse action items
            action_items = self._parse_action_items(data.get("action_items") or [])

            # Parse keywords and create Obsidian tags
            keywords = data.get("keywords") or []
            if isinstance(keywords, list):
                keywords = [str(k).lower().replace("_", " ").strip() for k in keywords]
            else:
                keywords = []

            obsidian_tags = [f"#{k.replace(' ', '_')}" for k in keywords]

            # Parse key moments
            key_moments = self._parse_key_moments(data.get("key_moments") or [])

            # Correlate timestamps with transcript_data if available
            if request.transcript_data:
                self._correlate_timestamps(
                    key_concepts, key_moments, request.transcript_data
                )

            duration = time.time() - start_time

            result = ContentSummaryResult(
                content_type=content_type,
                content_type_confidence=data.get("content_type_confidence", 0.8),
                content_type_reasoning=data.get("content_type_reasoning", ""),
                tldr=data.get("tldr", ""),
                key_concepts=key_concepts,
                technical_details=technical_details,
                has_technical_content=has_technical,
                action_items=action_items,
                keywords=keywords,
                suggested_obsidian_tags=obsidian_tags,
                key_moments=key_moments,
                tokens_used=tokens_used,
                analysis_duration_seconds=round(duration, 2),
                transcript_word_count=word_count
            )

            logger.info(f"Content summary completed in {duration:.1f}s")

            return result

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise ValueError(f"Analysis failed: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT response: {e}")
            raise ValueError(f"Failed to parse analysis response: {str(e)}")

    def _parse_content_type(self, type_str: str) -> ContentType:
        """Parse content type string to enum."""
        try:
            return ContentType(type_str.lower())
        except ValueError:
            return ContentType.OTHER

    def _parse_key_concepts(self, concepts_data: list) -> list[KeyConcept]:
        """Parse key concepts from GPT response."""
        concepts = []
        for c in concepts_data:
            if not isinstance(c, dict):
                continue

            importance_str = c.get("importance", "medium")
            try:
                importance = Priority(importance_str.lower())
            except ValueError:
                importance = Priority.MEDIUM

            concepts.append(KeyConcept(
                concept=c.get("concept", ""),
                explanation=c.get("explanation", ""),
                importance=importance,
                timestamp=c.get("timestamp")
            ))

        return concepts

    def _parse_technical_details(self, details_data: list) -> list[TechnicalDetail]:
        """Parse technical details from GPT response."""
        details = []
        for d in details_data:
            if not isinstance(d, dict):
                continue

            category_str = d.get("category", "concept")
            try:
                category = TechnicalCategory(category_str.lower())
            except ValueError:
                category = TechnicalCategory.CONCEPT

            details.append(TechnicalDetail(
                category=category,
                name=d.get("name", ""),
                description=d.get("description"),
                code=d.get("code"),
                timestamp=d.get("timestamp")
            ))

        return details

    def _parse_action_items(self, items_data: list) -> list[ActionItem]:
        """Parse action items from GPT response."""
        items = []
        for item in items_data:
            if not isinstance(item, dict):
                continue

            priority_str = item.get("priority", "medium")
            try:
                priority = Priority(priority_str.lower())
            except ValueError:
                priority = Priority.MEDIUM

            items.append(ActionItem(
                action=item.get("action", ""),
                context=item.get("context"),
                priority=priority
            ))

        return items

    def _parse_key_moments(self, moments_data: list) -> list[KeyMoment]:
        """Parse key moments from GPT response."""
        moments = []
        for m in moments_data:
            if not isinstance(m, dict):
                continue

            timestamp = m.get("timestamp", 0)
            if not isinstance(timestamp, (int, float)):
                timestamp = 0

            moments.append(KeyMoment(
                timestamp=float(timestamp),
                title=m.get("title", ""),
                description=m.get("description", "")
            ))

        return moments

    def _correlate_timestamps(
        self,
        concepts: list[KeyConcept],
        moments: list[KeyMoment],
        transcript_data: list[dict]
    ) -> None:
        """
        Correlate extracted items with actual transcript timestamps.

        Uses fuzzy matching to find where concepts/moments appear in the
        timestamped transcript segments.
        """
        if not transcript_data:
            return

        # Build a combined text with position markers for better matching
        full_text_lower = " ".join(
            segment.get("text", "").lower() for segment in transcript_data
        )

        # Correlate key concepts
        for concept in concepts:
            if concept.timestamp is None or concept.timestamp == 0:
                concept_lower = concept.concept.lower()
                concept_words = concept_lower.split()[:3]  # First 3 words

                for segment in transcript_data:
                    text = segment.get("text", "").lower()
                    # Match if concept name or key words appear in segment
                    if concept_lower in text or any(
                        word in text for word in concept_words if len(word) > 3
                    ):
                        concept.timestamp = segment.get("start", 0)
                        break

        # Correlate key moments - use description/title to find position
        for moment in moments:
            if moment.timestamp == 0:
                # Extract key words from moment title and description
                moment_text = f"{moment.title} {moment.description}".lower()
                moment_words = [w for w in moment_text.split() if len(w) > 4][:5]

                best_match_score = 0
                best_timestamp = 0

                for segment in transcript_data:
                    text = segment.get("text", "").lower()
                    # Count matching words
                    match_score = sum(1 for word in moment_words if word in text)
                    if match_score > best_match_score:
                        best_match_score = match_score
                        best_timestamp = segment.get("start", 0)

                if best_match_score >= 2:  # At least 2 word matches
                    moment.timestamp = best_timestamp

    def is_available(self) -> bool:
        """Check if the service is available."""
        return self.client is not None


# Singleton instance
_service_instance: Optional[ContentSummaryService] = None


def get_summary_service() -> ContentSummaryService:
    """Get or create the service singleton."""
    global _service_instance
    if _service_instance is None:
        _service_instance = ContentSummaryService()
    return _service_instance
