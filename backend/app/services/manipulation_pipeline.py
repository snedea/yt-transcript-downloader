"""
Manipulation Analysis Pipeline

Orchestrates the manipulation analysis for both Quick and Deep modes.
- Quick mode: Single comprehensive GPT call (~15 seconds)
- Deep mode: Multi-pass pipeline with claim verification (~60 seconds)

Uses the 5-dimension framework:
1. Epistemic Integrity
2. Argument Quality
3. Manipulation Risk
4. Rhetorical Craft
5. Fairness/Balance
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from openai import OpenAI, OpenAIError

from app.config import settings
from app.models.manipulation_analysis import (
    ManipulationAnalysisResult,
    ManipulationAnalysisRequest,
    DimensionScore,
    DimensionType,
    DetectedClaim,
    ClaimType,
    VerificationStatus,
    AnalyzedSegment,
    SegmentAnnotation,
    AnnotationSeverity,
    DeviceSummary,
    AnalysisMode,
    calculate_overall_score,
    score_to_grade
)
from app.data.manipulation_toolkit import (
    DIMENSION_DEFINITIONS,
    MANIPULATION_TECHNIQUES,
    TECHNIQUE_CATEGORIES,
    get_full_prompt_reference
)
from app.services.web_search import get_web_search_service

logger = logging.getLogger(__name__)


# JSON Schema for Quick Mode response
QUICK_MODE_SCHEMA = {
    "type": "object",
    "properties": {
        "dimension_scores": {
            "type": "object",
            "properties": {
                "epistemic_integrity": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "integer", "minimum": 0, "maximum": 100},
                        "explanation": {"type": "string"},
                        "red_flags": {"type": "array", "items": {"type": "string"}},
                        "strengths": {"type": "array", "items": {"type": "string"}},
                        "key_examples": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["score", "explanation"]
                },
                "argument_quality": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "integer", "minimum": 0, "maximum": 100},
                        "explanation": {"type": "string"},
                        "red_flags": {"type": "array", "items": {"type": "string"}},
                        "strengths": {"type": "array", "items": {"type": "string"}},
                        "key_examples": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["score", "explanation"]
                },
                "manipulation_risk": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "integer", "minimum": 0, "maximum": 100},
                        "explanation": {"type": "string"},
                        "red_flags": {"type": "array", "items": {"type": "string"}},
                        "strengths": {"type": "array", "items": {"type": "string"}},
                        "key_examples": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["score", "explanation"]
                },
                "rhetorical_craft": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "integer", "minimum": 0, "maximum": 100},
                        "explanation": {"type": "string"},
                        "red_flags": {"type": "array", "items": {"type": "string"}},
                        "strengths": {"type": "array", "items": {"type": "string"}},
                        "key_examples": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["score", "explanation"]
                },
                "fairness_balance": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "integer", "minimum": 0, "maximum": 100},
                        "explanation": {"type": "string"},
                        "red_flags": {"type": "array", "items": {"type": "string"}},
                        "strengths": {"type": "array", "items": {"type": "string"}},
                        "key_examples": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["score", "explanation"]
                }
            },
            "required": ["epistemic_integrity", "argument_quality", "manipulation_risk", "rhetorical_craft", "fairness_balance"]
        },
        "detected_claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim_text": {"type": "string"},
                    "claim_type": {"type": "string", "enum": ["factual", "causal", "normative", "prediction", "prescriptive"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["claim_text", "claim_type", "confidence"]
            }
        },
        "detected_techniques": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "technique_id": {"type": "string"},
                    "phrase": {"type": "string"},
                    "explanation": {"type": "string"},
                    "severity": {"type": "string", "enum": ["low", "medium", "high"]}
                },
                "required": ["technique_id", "phrase", "explanation"]
            }
        },
        "executive_summary": {"type": "string"},
        "top_concerns": {"type": "array", "items": {"type": "string"}},
        "top_strengths": {"type": "array", "items": {"type": "string"}},
        "charitable_interpretation": {"type": "string"},
        "concerning_interpretation": {"type": "string"}
    },
    "required": ["dimension_scores", "executive_summary", "top_concerns", "top_strengths"]
}


class ManipulationAnalysisPipeline:
    """
    Pipeline for analyzing transcripts for manipulation techniques.

    Supports two modes:
    - Quick: Single GPT-4 call with comprehensive prompt (~15s)
    - Deep: Multi-pass analysis with claim verification (~60s)
    """

    MODES = {
        "quick": ["consolidated"],
        "deep": [
            "claim_extraction",
            "argument_mapping",
            "manipulation_scan",
            "dimension_scoring",
            "claim_verification",
            "synthesis"
        ]
    }

    def __init__(self):
        """Initialize the pipeline."""
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
        self.web_search = get_web_search_service()

    async def analyze(
        self,
        request: ManipulationAnalysisRequest
    ) -> ManipulationAnalysisResult:
        """
        Run the full analysis pipeline.

        Args:
            request: ManipulationAnalysisRequest with transcript and options

        Returns:
            ManipulationAnalysisResult with complete analysis
        """
        start_time = time.time()

        if not self.client:
            raise ValueError("OpenAI API key not configured")

        mode = request.analysis_mode
        transcript = request.transcript

        logger.info(f"Starting {mode.value} mode analysis for transcript ({len(transcript)} chars)")

        if mode == AnalysisMode.QUICK:
            result = await self._run_quick_mode(request)
        else:
            result = await self._run_deep_mode(request)

        # Set timing
        result.analysis_duration_seconds = time.time() - start_time
        result.transcript_word_count = len(transcript.split())

        logger.info(f"Analysis completed in {result.analysis_duration_seconds:.1f}s")

        return result

    async def _run_quick_mode(
        self,
        request: ManipulationAnalysisRequest
    ) -> ManipulationAnalysisResult:
        """
        Run Quick mode analysis - single comprehensive GPT call.

        Args:
            request: The analysis request

        Returns:
            ManipulationAnalysisResult
        """
        toolkit_reference = get_full_prompt_reference()

        # Build context
        context = ""
        if request.video_title:
            context += f"Video Title: {request.video_title}\n"
        if request.video_author:
            context += f"Speaker/Author: {request.video_author}\n"

        system_prompt = f"""You are an expert in rhetoric, argumentation theory, propaganda analysis, and critical discourse analysis.

Your task is to analyze a transcript for manipulation techniques and intellectual integrity using a 5-dimension framework.

{toolkit_reference}

## SCORING GUIDELINES

For each dimension, provide:
1. A score from 0-100
2. A brief explanation (2-3 sentences)
3. Red flags detected (list of specific issues found)
4. Strengths noted (list of positive patterns)
5. Key examples (exact quotes from the transcript)

### Score Interpretation:
- 90-100: Exceptionally rigorous, virtually no concerning patterns
- 80-89: Strong integrity, minor issues only
- 70-79: Generally sound, some concerning patterns
- 60-69: Mixed - notable issues balanced by positives
- 50-59: Concerning - significant manipulation patterns
- 40-49: Poor - many manipulation techniques present
- Below 40: Severe manipulation concerns

### Important Notes:
- **Manipulation Risk** is scored as risk level (high score = high risk = BAD)
- **Rhetorical Craft** is neutral (high score = effective, not good/bad)
- Be specific - cite exact phrases from the transcript
- Distinguish between persuasion (legitimate) and manipulation (coercive)

## OUTPUT FORMAT

Return a JSON object with dimension scores, detected claims, techniques, and summary.
Provide BOTH a charitable interpretation AND a concerning interpretation."""

        user_prompt = f"""{context}
## TRANSCRIPT TO ANALYZE:

{request.transcript}

Analyze this transcript using the 5-dimension manipulation framework.
Return your analysis as JSON matching the required schema."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=8000,
                response_format={"type": "json_object"}
            )

            tokens_used = response.usage.total_tokens
            raw_content = response.choices[0].message.content
            logger.info(f"GPT response (first 2000 chars): {raw_content[:2000]}")
            analysis_data = json.loads(raw_content)

            # Debug: log dimension_scores structure
            dim_scores_raw = analysis_data.get("dimension_scores", {})

            # GPT might put dimension scores at top level or nested under 'dimension_scores'
            dimension_keys = ["epistemic_integrity", "argument_quality", "manipulation_risk",
                            "rhetorical_craft", "fairness_balance"]
            alt_dimension_keys = ["Epistemic Integrity", "Argument Quality", "Manipulation Risk",
                                 "Rhetorical Craft", "Fairness/Balance", "Fairness Balance"]

            if not dim_scores_raw:
                # Check for dimension keys at top level
                for key in dimension_keys + alt_dimension_keys:
                    if key in analysis_data:
                        logger.info(f"Quick mode - Found dimension at top level: {key}")
                        # Normalize key name
                        normalized = key.lower().replace(" ", "_").replace("/", "_")
                        if normalized.endswith("_balance") and normalized != "fairness_balance":
                            normalized = "fairness_balance"
                        dim_scores_raw[normalized] = analysis_data[key]

            logger.info(f"dimension_scores keys: {list(dim_scores_raw.keys())}")
            for k, v in dim_scores_raw.items():
                logger.info(f"  {k}: {type(v)} = {v if isinstance(v, dict) else str(v)[:100]}")

            # Parse dimension scores
            dimension_scores = self._parse_dimension_scores(dim_scores_raw)

            # Calculate overall score
            overall_score = calculate_overall_score(dimension_scores)
            overall_grade = score_to_grade(overall_score)

            # Parse detected claims
            detected_claims = self._parse_claims(analysis_data.get("detected_claims", []))

            # Parse techniques into device summary
            device_summary = self._parse_techniques_to_summary(analysis_data.get("detected_techniques", []))

            # Get most used devices (top 5)
            most_used = sorted(device_summary, key=lambda x: x.count, reverse=True)[:5]

            # Verify claims if requested
            verified_claims = []
            if request.verify_claims and detected_claims:
                verified_claims = await self._verify_claims(detected_claims[:5])  # Limit to 5 for quick mode

            return ManipulationAnalysisResult(
                analysis_version="2.0",
                analysis_mode=AnalysisMode.QUICK,
                passes_completed=1,
                overall_score=overall_score,
                overall_grade=overall_grade,
                dimension_scores=dimension_scores,
                segments=[],  # No segment-level analysis in quick mode
                detected_claims=detected_claims,
                verified_claims=verified_claims,
                total_claims=len(detected_claims),
                claims_verified=len(verified_claims),
                claims_disputed=len([c for c in verified_claims if c.verification_status == VerificationStatus.DISPUTED]),
                device_summary=device_summary,
                most_used_devices=most_used,
                executive_summary=analysis_data.get("executive_summary", ""),
                top_concerns=analysis_data.get("top_concerns", []),
                top_strengths=analysis_data.get("top_strengths", []),
                charitable_interpretation=analysis_data.get("charitable_interpretation", ""),
                concerning_interpretation=analysis_data.get("concerning_interpretation", ""),
                tokens_used=tokens_used
            )

        except OpenAIError as e:
            logger.error(f"OpenAI API error in quick mode: {e}")
            raise ValueError(f"Analysis failed: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT response as JSON: {e}")
            raise ValueError(f"Failed to parse analysis response: {str(e)}")

    async def _run_deep_mode(
        self,
        request: ManipulationAnalysisRequest
    ) -> ManipulationAnalysisResult:
        """
        Run Deep mode analysis - multi-pass pipeline.

        Passes:
        1. Claim extraction
        2. Argument mapping (Toulmin model)
        3. Manipulation scan (per-segment)
        4. Dimension scoring
        5. Claim verification (via SearXNG)
        6. Synthesis

        Args:
            request: The analysis request

        Returns:
            ManipulationAnalysisResult
        """
        passes_completed = 0
        tokens_used = 0

        # Build segments from transcript_data if available
        segments = self._build_segments(request.transcript, request.transcript_data)

        # Pass 1: Extract claims
        logger.info("Deep mode: Pass 1 - Extracting claims")
        claims, pass_tokens = await self._extract_claims(request.transcript)
        tokens_used += pass_tokens
        passes_completed += 1

        # Assign claims to segments
        for claim in claims:
            for seg in segments:
                if claim.claim_text.lower() in seg.text.lower():
                    claim.segment_index = seg.segment_index
                    seg.claims.append(claim)
                    break

        # Pass 2: Manipulation scan (per-segment annotations)
        logger.info("Deep mode: Pass 2 - Scanning for manipulation techniques")
        annotations, pass_tokens = await self._scan_manipulation(request.transcript, segments)
        tokens_used += pass_tokens
        passes_completed += 1

        # Pass 3: Score dimensions
        logger.info("Deep mode: Pass 3 - Scoring dimensions")
        dimension_scores, summary_data, pass_tokens = await self._score_dimensions(
            request.transcript,
            claims,
            annotations,
            request.video_title,
            request.video_author
        )
        tokens_used += pass_tokens
        passes_completed += 1

        # Pass 4: Verify claims if requested
        verified_claims = []
        if request.verify_claims:
            logger.info("Deep mode: Pass 4 - Verifying claims")
            factual_claims = [c for c in claims if c.claim_type == ClaimType.FACTUAL][:10]
            verified_claims = await self._verify_claims(factual_claims)
            passes_completed += 1

        # Calculate overall score
        overall_score = calculate_overall_score(dimension_scores)
        overall_grade = score_to_grade(overall_score)

        # Build device summary from annotations
        device_summary = self._build_device_summary(annotations)
        most_used = sorted(device_summary, key=lambda x: x.count, reverse=True)[:5]

        return ManipulationAnalysisResult(
            analysis_version="2.0",
            analysis_mode=AnalysisMode.DEEP,
            passes_completed=passes_completed,
            overall_score=overall_score,
            overall_grade=overall_grade,
            dimension_scores=dimension_scores,
            segments=segments,
            detected_claims=claims,
            verified_claims=verified_claims,
            total_claims=len(claims),
            claims_verified=len(verified_claims),
            claims_disputed=len([c for c in verified_claims if c.verification_status == VerificationStatus.DISPUTED]),
            device_summary=device_summary,
            most_used_devices=most_used,
            executive_summary=summary_data.get("executive_summary", ""),
            top_concerns=summary_data.get("top_concerns", []),
            top_strengths=summary_data.get("top_strengths", []),
            charitable_interpretation=summary_data.get("charitable_interpretation", ""),
            concerning_interpretation=summary_data.get("concerning_interpretation", ""),
            tokens_used=tokens_used
        )

    def _build_segments(
        self,
        transcript: str,
        transcript_data: Optional[List[dict]]
    ) -> List[AnalyzedSegment]:
        """Build segment list from transcript data."""
        segments = []

        if transcript_data:
            for i, seg in enumerate(transcript_data):
                segments.append(AnalyzedSegment(
                    segment_index=i,
                    start_time=seg.get("start", 0.0),
                    end_time=seg.get("start", 0.0) + seg.get("duration", 0.0),
                    text=seg.get("text", ""),
                    claims=[],
                    annotations=[]
                ))
        else:
            # Split transcript into ~100 word chunks
            words = transcript.split()
            chunk_size = 100
            for i in range(0, len(words), chunk_size):
                chunk_words = words[i:i + chunk_size]
                segments.append(AnalyzedSegment(
                    segment_index=i // chunk_size,
                    start_time=0.0,
                    end_time=0.0,
                    text=" ".join(chunk_words),
                    claims=[],
                    annotations=[]
                ))

        return segments

    async def _extract_claims(self, transcript: str) -> Tuple[List[DetectedClaim], int]:
        """Extract claims from transcript."""
        system_prompt = """You are an expert in argument analysis. Extract all claims from the transcript.

For each claim, identify:
1. The exact claim text (as stated in the transcript)
2. The claim type:
   - factual: Verifiable facts (statistics, events, scientific claims)
   - causal: Cause-effect claims ("X leads to Y")
   - normative: Value/moral claims ("X is good/bad")
   - prediction: Future-oriented claims ("X will happen")
   - prescriptive: Action recommendations ("You should do X")
3. Your confidence in the detection (0-1)

Return a JSON object with a "claims" array."""

        user_prompt = f"""Extract all claims from this transcript:

{transcript}

Return JSON with "claims" array containing objects with: claim_text, claim_type, confidence"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Use mini for this pass to save tokens
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )

            tokens_used = response.usage.total_tokens
            data = json.loads(response.choices[0].message.content)

            claims = []
            for i, c in enumerate(data.get("claims", [])):
                try:
                    claims.append(DetectedClaim(
                        claim_id=f"claim_{i}",
                        claim_text=c.get("claim_text", ""),
                        claim_type=ClaimType(c.get("claim_type", "normative")),
                        confidence=c.get("confidence", 0.7),
                        segment_index=0
                    ))
                except ValueError:
                    # Invalid claim type, default to normative
                    claims.append(DetectedClaim(
                        claim_id=f"claim_{i}",
                        claim_text=c.get("claim_text", ""),
                        claim_type=ClaimType.NORMATIVE,
                        confidence=c.get("confidence", 0.7),
                        segment_index=0
                    ))

            return claims, tokens_used

        except Exception as e:
            logger.error(f"Claim extraction failed: {e}")
            return [], 0

    async def _scan_manipulation(
        self,
        transcript: str,
        segments: List[AnalyzedSegment]
    ) -> Tuple[List[SegmentAnnotation], int]:
        """Scan for manipulation techniques."""
        # Build technique reference
        technique_list = []
        for tech_id, tech in MANIPULATION_TECHNIQUES.items():
            technique_list.append(f"- {tech_id}: {tech.get('description', '')}")
        technique_ref = "\n".join(technique_list)

        system_prompt = f"""You are an expert in manipulation detection. Analyze the transcript for manipulation techniques.

## TECHNIQUES TO DETECT:
{technique_ref}

For each technique found, provide:
1. technique_id: The ID from the list above
2. phrase: The EXACT phrase from the transcript
3. explanation: Why this qualifies as this technique
4. severity: low, medium, or high

Return a JSON object with an "annotations" array."""

        user_prompt = f"""Analyze this transcript for manipulation techniques:

{transcript}

Return JSON with "annotations" array containing objects with: technique_id, phrase, explanation, severity"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )

            tokens_used = response.usage.total_tokens
            data = json.loads(response.choices[0].message.content)

            annotations = []
            for i, a in enumerate(data.get("annotations", [])):
                technique_id = a.get("technique_id", "unknown")
                tech_info = MANIPULATION_TECHNIQUES.get(technique_id, {})

                severity_str = a.get("severity", "medium").lower()
                try:
                    severity = AnnotationSeverity(severity_str)
                except ValueError:
                    severity = AnnotationSeverity.MEDIUM

                ann = SegmentAnnotation(
                    annotation_id=f"ann_{i}",
                    span=(0, 0),  # Would need text processing to compute
                    label=technique_id,
                    category=tech_info.get("category", "unknown"),
                    confidence=0.8,
                    explanation=a.get("explanation", ""),
                    severity=severity
                )
                annotations.append(ann)

                # Assign to matching segment
                phrase = a.get("phrase", "").lower()
                for seg in segments:
                    if phrase in seg.text.lower():
                        seg.annotations.append(ann)
                        break

            return annotations, tokens_used

        except Exception as e:
            logger.error(f"Manipulation scan failed: {e}")
            return [], 0

    async def _score_dimensions(
        self,
        transcript: str,
        claims: List[DetectedClaim],
        annotations: List[SegmentAnnotation],
        video_title: Optional[str],
        video_author: Optional[str]
    ) -> Tuple[Dict[str, DimensionScore], Dict[str, Any], int]:
        """Score all 5 dimensions."""
        toolkit_reference = get_full_prompt_reference()

        # Summarize claims and annotations for context
        claim_summary = f"{len(claims)} claims detected"
        if claims:
            claim_types = {}
            for c in claims:
                claim_types[c.claim_type.value] = claim_types.get(c.claim_type.value, 0) + 1
            claim_summary += f": {claim_types}"

        ann_summary = f"{len(annotations)} manipulation techniques detected"
        if annotations:
            technique_counts = {}
            for a in annotations:
                technique_counts[a.label] = technique_counts.get(a.label, 0) + 1
            top_techniques = sorted(technique_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            ann_summary += f": {dict(top_techniques)}"

        context = ""
        if video_title:
            context += f"Video Title: {video_title}\n"
        if video_author:
            context += f"Speaker/Author: {video_author}\n"

        system_prompt = f"""You are an expert in manipulation analysis. Score the transcript on 5 dimensions.

{toolkit_reference}

## PRIOR ANALYSIS CONTEXT
{claim_summary}
{ann_summary}

## SCORING TASK
Score each dimension 0-100 with:
- explanation: 2-3 sentence justification
- red_flags: List of concerning patterns found
- strengths: List of positive patterns found
- key_examples: Exact quotes from transcript

Remember:
- manipulation_risk: HIGH score = HIGH risk = BAD
- rhetorical_craft: Neutral (effective ≠ ethical)

Also provide:
- executive_summary: 2-3 paragraph assessment
- top_concerns: Top 3 concerns
- top_strengths: Top 3 strengths
- charitable_interpretation: Best-case reading
- concerning_interpretation: Most concerning reading"""

        user_prompt = f"""{context}
## TRANSCRIPT:

{transcript}

Score all 5 dimensions and provide summary. Return as JSON."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=6000,
                response_format={"type": "json_object"}
            )

            tokens_used = response.usage.total_tokens
            raw_content = response.choices[0].message.content
            logger.info(f"Deep mode - GPT dimension scoring response (first 2000 chars): {raw_content[:2000]}")
            data = json.loads(raw_content)

            # Debug: log the keys in the response
            logger.info(f"Deep mode - Response top-level keys: {list(data.keys())}")

            # GPT might put dimension scores at top level or nested under 'dimension_scores'
            dim_scores_raw = data.get("dimension_scores", {})

            # If dimension_scores is empty, check if dimensions are at top level
            dimension_keys = ["epistemic_integrity", "argument_quality", "manipulation_risk",
                            "rhetorical_craft", "fairness_balance"]
            alt_dimension_keys = ["Epistemic Integrity", "Argument Quality", "Manipulation Risk",
                                 "Rhetorical Craft", "Fairness/Balance", "Fairness Balance"]

            if not dim_scores_raw:
                # Check for dimension keys at top level
                for key in dimension_keys + alt_dimension_keys:
                    if key in data:
                        logger.info(f"Found dimension at top level: {key}")
                        # Normalize key name
                        normalized = key.lower().replace(" ", "_").replace("/", "_")
                        if normalized.endswith("_balance") and normalized != "fairness_balance":
                            normalized = "fairness_balance"
                        dim_scores_raw[normalized] = data[key]

            logger.info(f"Deep mode - dimension_scores keys: {list(dim_scores_raw.keys()) if isinstance(dim_scores_raw, dict) else type(dim_scores_raw)}")

            dimension_scores = self._parse_dimension_scores(dim_scores_raw)

            summary_data = {
                "executive_summary": data.get("executive_summary", ""),
                "top_concerns": data.get("top_concerns", []),
                "top_strengths": data.get("top_strengths", []),
                "charitable_interpretation": data.get("charitable_interpretation", ""),
                "concerning_interpretation": data.get("concerning_interpretation", "")
            }

            return dimension_scores, summary_data, tokens_used

        except Exception as e:
            logger.error(f"Dimension scoring failed: {e}")
            return {}, {}, 0

    async def _verify_claims(self, claims: List[DetectedClaim]) -> List[DetectedClaim]:
        """Verify factual claims via web search."""
        verified = []

        for claim in claims:
            if claim.claim_type != ClaimType.FACTUAL:
                claim.verification_status = VerificationStatus.UNVERIFIABLE
                verified.append(claim)
                continue

            try:
                result = await self.web_search.verify_quote(claim.claim_text)

                if result.verified:
                    if result.confidence > 0.7:
                        claim.verification_status = VerificationStatus.VERIFIED
                    elif result.confidence < 0.3:
                        claim.verification_status = VerificationStatus.DISPUTED
                    else:
                        claim.verification_status = VerificationStatus.UNVERIFIED
                else:
                    claim.verification_status = VerificationStatus.UNVERIFIED

                claim.verification_details = result.verification_details
                if result.source:
                    claim.supporting_sources.append(result.source)

                verified.append(claim)

            except Exception as e:
                logger.error(f"Claim verification failed for '{claim.claim_text[:50]}': {e}")
                claim.verification_status = VerificationStatus.UNVERIFIED
                claim.verification_details = f"Verification failed: {str(e)}"
                verified.append(claim)

        return verified

    def _parse_dimension_scores(self, scores_data: Dict) -> Dict[str, DimensionScore]:
        """Parse dimension scores from GPT response."""
        dimension_scores = {}

        dimension_map = {
            "epistemic_integrity": DimensionType.EPISTEMIC_INTEGRITY,
            "argument_quality": DimensionType.ARGUMENT_QUALITY,
            "manipulation_risk": DimensionType.MANIPULATION_RISK,
            "rhetorical_craft": DimensionType.RHETORICAL_CRAFT,
            "fairness_balance": DimensionType.FAIRNESS_BALANCE
        }

        # Also handle alternate key formats GPT might use
        alternate_keys = {
            "epistemic_integrity": ["epistemic_integrity", "Epistemic Integrity", "epistemicIntegrity", "epistemic"],
            "argument_quality": ["argument_quality", "Argument Quality", "argumentQuality", "argument"],
            "manipulation_risk": ["manipulation_risk", "Manipulation Risk", "manipulationRisk", "manipulation"],
            "rhetorical_craft": ["rhetorical_craft", "Rhetorical Craft", "rhetoricalCraft", "rhetorical"],
            "fairness_balance": ["fairness_balance", "Fairness/Balance", "Fairness Balance", "fairnessBalance", "fairness"]
        }

        for dim_key, dim_type in dimension_map.items():
            # Try to find the dimension data using alternate keys
            dim_data = {}
            for alt_key in alternate_keys.get(dim_key, [dim_key]):
                if alt_key in scores_data:
                    dim_data = scores_data[alt_key]
                    logger.info(f"Found dimension {dim_key} under key '{alt_key}'")
                    break

            if not dim_data:
                logger.warning(f"Dimension {dim_key} not found in response. Available keys: {list(scores_data.keys())}")

            dim_def = DIMENSION_DEFINITIONS.get(dim_key, {})

            # Handle case where dim_data might be an int (just a score) instead of a dict
            if isinstance(dim_data, (int, float)):
                score = int(dim_data)
                explanation = ""
                red_flags = []
                strengths = []
                key_examples = []
                contributing_techniques = []
                confidence = 0.8
            elif isinstance(dim_data, dict):
                score = dim_data.get("score", 50)
                explanation = dim_data.get("explanation", "")
                red_flags = dim_data.get("red_flags", [])
                strengths = dim_data.get("strengths", [])
                key_examples = dim_data.get("key_examples", [])
                contributing_techniques = dim_data.get("contributing_techniques", [])
                confidence = dim_data.get("confidence", 0.8)
            else:
                logger.warning(f"Unexpected dim_data type for {dim_key}: {type(dim_data)}")
                score = 50
                explanation = ""
                red_flags = []
                strengths = []
                key_examples = []
                contributing_techniques = []
                confidence = 0.8

            dimension_scores[dim_key] = DimensionScore(
                dimension=dim_type,
                dimension_name=dim_def.get("name", dim_key.replace("_", " ").title()),
                score=score,
                confidence=confidence,
                explanation=explanation,
                red_flags=red_flags,
                strengths=strengths,
                key_examples=key_examples,
                contributing_techniques=contributing_techniques
            )

        return dimension_scores

    def _parse_claims(self, claims_data: List[Dict]) -> List[DetectedClaim]:
        """Parse claims from GPT response."""
        claims = []

        for i, c in enumerate(claims_data):
            claim_type_str = c.get("claim_type", "normative")
            try:
                claim_type = ClaimType(claim_type_str)
            except ValueError:
                claim_type = ClaimType.NORMATIVE

            claims.append(DetectedClaim(
                claim_id=f"claim_{i}",
                claim_text=c.get("claim_text", ""),
                claim_type=claim_type,
                confidence=c.get("confidence", 0.7),
                segment_index=0
            ))

        return claims

    def _parse_techniques_to_summary(self, techniques_data: List[Dict]) -> List[DeviceSummary]:
        """Parse techniques into device summary."""
        device_counts = {}
        device_examples = {}
        device_severity = {}

        for t in techniques_data:
            tech_id = t.get("technique_id", "unknown")
            tech_info = MANIPULATION_TECHNIQUES.get(tech_id, {})

            device_counts[tech_id] = device_counts.get(tech_id, 0) + 1

            if tech_id not in device_examples:
                device_examples[tech_id] = []
            device_examples[tech_id].append(t.get("phrase", ""))

            severity_str = t.get("severity", "medium").lower()
            try:
                severity = AnnotationSeverity(severity_str)
            except ValueError:
                severity = AnnotationSeverity.MEDIUM

            if tech_id not in device_severity or severity.value > device_severity[tech_id].value:
                device_severity[tech_id] = severity

        summaries = []
        for tech_id, count in device_counts.items():
            tech_info = MANIPULATION_TECHNIQUES.get(tech_id, {})
            summaries.append(DeviceSummary(
                device_id=tech_id,
                device_name=tech_info.get("name", tech_id.replace("_", " ").title()),
                category=tech_info.get("category", "unknown"),
                count=count,
                severity=device_severity.get(tech_id, AnnotationSeverity.MEDIUM),
                examples=device_examples.get(tech_id, [])[:3]
            ))

        return summaries

    def _build_device_summary(self, annotations: List[SegmentAnnotation]) -> List[DeviceSummary]:
        """Build device summary from annotations."""
        device_counts = {}
        device_examples = {}
        device_severity = {}

        for ann in annotations:
            tech_id = ann.label
            device_counts[tech_id] = device_counts.get(tech_id, 0) + 1

            if tech_id not in device_examples:
                device_examples[tech_id] = []
            device_examples[tech_id].append(ann.explanation)

            if tech_id not in device_severity or ann.severity.value > device_severity[tech_id].value:
                device_severity[tech_id] = ann.severity

        summaries = []
        for tech_id, count in device_counts.items():
            tech_info = MANIPULATION_TECHNIQUES.get(tech_id, {})
            summaries.append(DeviceSummary(
                device_id=tech_id,
                device_name=tech_info.get("name", tech_id.replace("_", " ").title()),
                category=tech_info.get("category", "unknown"),
                count=count,
                severity=device_severity.get(tech_id, AnnotationSeverity.MEDIUM),
                examples=device_examples.get(tech_id, [])[:3]
            ))

        return summaries

    def is_available(self) -> bool:
        """Check if the pipeline is available."""
        return self.client is not None


# Singleton instance
_pipeline_instance: Optional[ManipulationAnalysisPipeline] = None


def get_manipulation_pipeline() -> ManipulationAnalysisPipeline:
    """Get or create the pipeline singleton."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = ManipulationAnalysisPipeline()
    return _pipeline_instance
