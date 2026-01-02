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
    ScholarlyContext,
    ScholarlyFigure,
    ScholarlySource,
    ScholarlyDebate,
    EvidenceType,
    TimePeriod,
)

logger = logging.getLogger(__name__)


SUMMARY_SYSTEM_PROMPT = """You are an expert content analyst with deep expertise in academic research, source criticism, and scholarly analysis. Your goal is to extract CURRICULUM-GRADE summaries that capture not just surface-level content, but the scholarly depth, debates, and nuances presented.

## CONTENT TYPE DETECTION

First, identify the content type from these categories:
- programming_technical: Code tutorials, software development, tech explanations, system design
- tutorial_howto: Step-by-step guides, DIY instructions, how-to content
- news_current_events: News coverage, current events discussion, breaking stories
- educational: Academic content, concept explanations, learning material, lectures, documentaries
- entertainment: Comedy, storytelling, vlogs, lifestyle content
- discussion_opinion: Debates, opinion pieces, commentary, analysis
- review: Product/service/media reviews, comparisons
- interview: Q&A format, conversations, podcasts with guests
- other: Content that doesn't fit above categories

## EXTRACTION GUIDELINES

### For ALL content types:
1. TLDR: Write 2-3 clear sentences that capture the THESIS and main argument, not just the topic
2. Key Concepts: Extract 5-10 main ideas with DETAILED explanations (2-3 sentences each)
3. Action Items: List practical takeaways the viewer should remember or do
4. Keywords: Generate 10-20 tags (lowercase, spaces allowed)
5. Key Moments: Identify 5-8 significant points with approximate timestamps

### For educational content, extract WITH SCHOLARLY DEPTH:

#### Named Figures & Relationships:
- List ALL named individuals (historical figures, scholars, authors)
- Include their relationships to each other (e.g., "Jonathan - David's close friend/ally")
- Note their roles, titles, and significance
- Include dates/periods when mentioned

#### Source Criticism & Debates:
- What sources or texts are discussed? (e.g., "Deuteronomistic History", "Dead Sea Scrolls")
- What scholarly debates are presented? (e.g., "historicity vs. literary construction")
- What different scholarly positions exist? Name them explicitly
- What evidence supports each position?

#### Historical Context:
- Time periods discussed with approximate dates
- Geographic locations and their significance
- Political/social context of the era
- How modern understanding differs from traditional views

#### Evidence Types Mentioned:
- Archaeological evidence (sites, artifacts, inscriptions)
- Textual evidence (manuscripts, translations, redactions)
- Linguistic evidence (word origins, literary analysis)
- Comparative evidence (parallel texts, similar traditions)

#### Methodological Approaches:
- What analytical methods does the presenter use?
- Source criticism, form criticism, redaction criticism?
- Historical-critical method vs. literary approaches?

### For programming_technical content, ALSO extract:
- Code snippets mentioned or demonstrated
- Libraries, frameworks, and packages with versions if mentioned
- Commands (terminal, git, npm, pip, etc.)
- Tools and APIs referenced
- Programming concepts explained
- Architecture decisions and trade-offs

### For tutorial_howto content, ALSO focus on:
- Step-by-step instructions
- Materials or tools needed
- Common mistakes or warnings mentioned
- Tips and best practices

### For news_current_events content, ALSO extract:
- Key facts and claims with sources
- Names, dates, and locations
- Different perspectives presented
- What's contested vs. established

### For discussion_opinion content, ALSO extract:
- Main thesis/argument being made
- Evidence cited to support claims
- Counter-arguments acknowledged
- Logical structure of the argument

## SCHOLARLY CONTENT SPECIAL INSTRUCTIONS

When analyzing educational content about history, religion, philosophy, or academic subjects:

1. DO NOT oversimplify - capture the nuance and complexity
2. EXPLICITLY list all named figures with brief identifiers
3. IDENTIFY scholarly debates and different schools of thought
4. NOTE what evidence types support different claims
5. DISTINGUISH between what the presenter states as fact vs. scholarly consensus vs. contested
6. CAPTURE methodological approaches used in the analysis
7. INCLUDE specific examples, case studies, or textual citations mentioned

## CRITICAL: SOURCES AND DEBATES ARE MANDATORY

For educational content, you MUST populate the scholarly_context.sources and scholarly_context.debates arrays. These are NOT optional.

### SOURCES - What to look for:
Sources are ANY texts, documents, manuscripts, or scholarly works mentioned or implied:
- **Biblical/Religious**: Book names (Genesis, Psalms, Gospel of Mark), manuscript traditions (Masoretic Text, Septuagint, Dead Sea Scrolls)
- **Historical Documents**: Chronicles, king lists, inscriptions, letters, treaties
- **Scholarly Works**: Named theories (Documentary Hypothesis, Deuteronomistic History), academic consensus positions
- **Archaeological**: Site reports, artifact catalogs, excavation findings
- **Primary vs Secondary**: Note if the source is ancient/primary or modern/scholarly

Example sources to extract:
- "Book of Samuel" [type: biblical text] - Primary narrative source for David's life
- "Deuteronomistic History" [type: scholarly theory] - The theory that Deuteronomy-2 Kings was edited by a single school
- "Tel Dan Stele" [type: archaeological] - 9th century BCE inscription mentioning "House of David"
- "Psalms" [type: biblical text] - Traditional attribution to David, modern scholarship debates authorship

### DEBATES - What to look for:
A debate exists whenever the presenter mentions ANY of these patterns:
- "Some scholars think X, while others argue Y"
- "Traditional view vs. modern scholarship"
- "The question of whether..."
- "Debate over the historicity of..."
- "Minimalist vs. maximalist positions"
- "Dating controversies"
- "Authorship questions"
- Implicit disagreements between sources

Example debates to extract:
- Topic: "Historicity of King David"
  Positions: ["Maximalists argue David was a powerful king as described", "Minimalists view David as a minor chieftain or legendary figure", "Moderate position accepts historical core with literary embellishment"]
  Evidence: "Tel Dan Stele provides external evidence; lack of monumental architecture challenges grand kingdom narrative"

- Topic: "Authorship of Psalms"
  Positions: ["Traditional view: David wrote the Psalms attributed to him", "Critical view: Many 'Davidic' psalms are post-exilic compositions"]
  Evidence: "Linguistic analysis, historical references within psalms, superscription traditions"

- Topic: "Nature of David-Jonathan relationship"
  Positions: ["Political covenant/alliance interpretation", "Deep personal friendship", "Romantic relationship interpretation"]
  Evidence: "Hebrew term 'ahava', covenant language, narrative context"

### IF NO EXPLICIT DEBATES MENTIONED:
Even if the presenter doesn't explicitly frame something as a "debate", extract IMPLIED scholarly tensions:
- If they present "the traditional view" vs "what we now know" = that's a debate
- If they say "scholars disagree" or "it's uncertain" = that's a debate
- If they present multiple interpretations = that's a debate
- If they question conventional wisdom = that's a debate

Example of GOOD scholarly extraction:
- "Deuteronomistic History: The scholarly theory that Deuteronomy through 2 Kings were composed/edited by a single school during the Babylonian exile (6th century BCE), giving a theological interpretation of Israel's history"
- "David-Jonathan relationship: Presented as deep friendship/covenant bond; some scholars interpret the Hebrew 'ahava' (love) as political treaty language, others as genuine affection"

Example of BAD superficial extraction:
- "The video discusses King David"
- "David had friends"

## TIMESTAMP HANDLING
- Estimate timestamps based on position in transcript
- Use format of seconds (e.g., 125 for 2:05)
- If transcript has timing data, try to correlate

## OUTPUT FORMAT
Return a JSON object with ALL required fields. Be THOROUGH - err on the side of including more detail.
For educational content, include scholarly_context object with figures, sources, debates, evidence, and methodology."""


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
        },
        "scholarly_context": {
            "type": ["object", "null"],
            "properties": {
                "figures": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "role": {"type": ["string", "null"]},
                            "period": {"type": ["string", "null"]},
                            "relationships": {"type": ["string", "null"]},
                            "significance": {"type": ["string", "null"]}
                        },
                        "required": ["name"]
                    }
                },
                "sources": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": ["string", "null"]},
                            "description": {"type": ["string", "null"]},
                            "significance": {"type": ["string", "null"]}
                        },
                        "required": ["name"]
                    }
                },
                "debates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string"},
                            "positions": {"type": "array", "items": {"type": "string"}},
                            "evidence": {"type": ["string", "null"]},
                            "consensus": {"type": ["string", "null"]}
                        },
                        "required": ["topic"]
                    }
                },
                "evidence_types": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "examples": {"type": "array", "items": {"type": "string"}},
                            "significance": {"type": ["string", "null"]}
                        },
                        "required": ["type"]
                    }
                },
                "methodology": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "time_periods": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "period": {"type": "string"},
                            "dates": {"type": ["string", "null"]},
                            "context": {"type": ["string", "null"]}
                        },
                        "required": ["period"]
                    }
                }
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

Return a JSON object with: content_type, content_type_confidence, content_type_reasoning, tldr, key_concepts, technical_details (if applicable), action_items, keywords, key_moments, and scholarly_context (for educational content).

IMPORTANT:
1. For key_moments timestamps, use the [M:SS] markers in the transcript to estimate when each moment occurs. Convert to seconds (e.g., [2:30] = 150 seconds). Distribute moments across the video duration.
2. For educational/scholarly content, populate the scholarly_context object with: figures (named individuals), sources (texts/manuscripts discussed), debates (scholarly disagreements), evidence_types (archaeological, textual, etc.), methodology (analytical approaches used), and time_periods (historical eras discussed).
3. Be THOROUGH with key_concepts - extract 5-10 concepts with detailed 2-3 sentence explanations each.

CRITICAL FOR EDUCATIONAL CONTENT:
- scholarly_context.sources MUST contain at least 3-5 sources (biblical books, historical documents, scholarly theories, archaeological findings mentioned)
- scholarly_context.debates MUST contain at least 2-3 debates (any scholarly disagreements, traditional vs modern views, interpretation disputes)
- If a source or debate seems implied but not explicit, INCLUDE IT with a note that it's implied
- Look for patterns like "some argue", "traditionally believed", "modern scholarship suggests", "the question of" - these indicate debates"""

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

            # Parse scholarly context (for educational content)
            scholarly_context = self._parse_scholarly_context(
                data.get("scholarly_context")
            )

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
                scholarly_context=scholarly_context,
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

    def _parse_scholarly_context(
        self, context_data: Optional[dict]
    ) -> Optional[ScholarlyContext]:
        """Parse scholarly context from GPT response."""
        if not context_data or not isinstance(context_data, dict):
            return None

        # Parse figures
        figures = []
        for f in context_data.get("figures") or []:
            if isinstance(f, dict):
                figures.append(ScholarlyFigure(
                    name=f.get("name", ""),
                    role=f.get("role"),
                    period=f.get("period"),
                    relationships=f.get("relationships"),
                    significance=f.get("significance")
                ))

        # Parse sources
        sources = []
        for s in context_data.get("sources") or []:
            if isinstance(s, dict):
                sources.append(ScholarlySource(
                    name=s.get("name", ""),
                    type=s.get("type"),
                    description=s.get("description"),
                    significance=s.get("significance")
                ))

        # Parse debates
        debates = []
        for d in context_data.get("debates") or []:
            if isinstance(d, dict):
                debates.append(ScholarlyDebate(
                    topic=d.get("topic", ""),
                    positions=d.get("positions") or [],
                    evidence=d.get("evidence"),
                    consensus=d.get("consensus")
                ))

        # Parse evidence types
        evidence_types = []
        for e in context_data.get("evidence_types") or []:
            if isinstance(e, dict):
                evidence_types.append(EvidenceType(
                    type=e.get("type", ""),
                    examples=e.get("examples") or [],
                    significance=e.get("significance")
                ))

        # Parse methodology
        methodology = context_data.get("methodology") or []
        if not isinstance(methodology, list):
            methodology = []
        methodology = [str(m) for m in methodology if m]

        # Parse time periods
        time_periods = []
        for t in context_data.get("time_periods") or []:
            if isinstance(t, dict):
                time_periods.append(TimePeriod(
                    period=t.get("period", ""),
                    dates=t.get("dates"),
                    context=t.get("context")
                ))

        # Only return if we have at least some data
        if not any([figures, sources, debates, evidence_types, methodology, time_periods]):
            return None

        return ScholarlyContext(
            figures=figures,
            sources=sources,
            debates=debates,
            evidence_types=evidence_types,
            methodology=methodology,
            time_periods=time_periods
        )

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
