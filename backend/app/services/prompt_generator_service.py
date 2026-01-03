"""
Prompt Generator Service

Generates production-ready prompts for 7 AI tool categories using:
- Video transcript as primary context
- Optional discovery/summary analyses for enrichment
- Nate B Jones' prompting techniques (intent, disambiguation, failure handling)

Supports two LLM providers:
1. Claude (via CLI) - Primary, uses existing subscription
2. OpenAI GPT-4o - Fallback if Claude unavailable
"""

import json
import logging
import os
import time
import uuid
from typing import Dict, Any, Optional, List

from openai import OpenAI

from app.config import settings
from app.models.prompt_generator import (
    PromptCategory,
    GeneratedPrompt,
    PromptGeneratorResult,
    CATEGORY_INFO,
    PROMPT_GENERATOR_SYSTEM_PROMPT,
    build_user_prompt,
)
from app.services.claude_provider import get_claude_provider

logger = logging.getLogger(__name__)

# Provider preference: "claude", "openai", or "auto" (claude first, then openai)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto")


class PromptGeneratorService:
    """Service for generating AI tool prompts from video/text content."""

    def __init__(self):
        """Initialize with available LLM providers."""
        # Claude provider (uses CLI, rides subscription)
        self.claude_provider = get_claude_provider()

        # OpenAI provider (requires API key)
        if settings.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.openai_client = None

        self.provider = LLM_PROVIDER
        logger.info(f"Prompt generator service initialized with provider preference: {self.provider}")

    def is_available(self) -> bool:
        """Check if any LLM provider is available."""
        if self.provider == "claude":
            return self.claude_provider.is_available()
        elif self.provider == "openai":
            return self.openai_client is not None
        else:  # auto
            return self.claude_provider.is_available() or self.openai_client is not None

    def _get_active_provider(self) -> tuple:
        """Determine which provider to use based on availability."""
        if self.provider == "claude":
            if self.claude_provider.is_available():
                return "claude", self.claude_provider
            return None, None
        elif self.provider == "openai":
            if self.openai_client:
                return "openai", self.openai_client
            return None, None
        else:  # auto - try claude first, then openai
            if self.claude_provider.is_available():
                return "claude", self.claude_provider
            if self.openai_client:
                return "openai", self.openai_client
            return None, None

    async def generate_prompts(
        self,
        transcript: str,
        video_title: Optional[str] = None,
        video_author: Optional[str] = None,
        video_id: Optional[str] = None,
        video_url: Optional[str] = None,
        discovery_summary: Optional[str] = None,
        content_summary: Optional[str] = None,
        categories: Optional[List[PromptCategory]] = None
    ) -> Dict[str, Any]:
        """
        Generate prompts for all or selected categories.

        Args:
            transcript: The main content to generate prompts from
            video_title: Optional title of the source
            video_author: Optional author of the source
            video_id: Optional YouTube video ID
            video_url: Optional source URL
            discovery_summary: Optional discovery analysis summary
            content_summary: Optional content summary
            categories: Optional list of categories to generate (None = all 7)

        Returns:
            Dictionary with success status and PromptGeneratorResult or error
        """
        provider_name, provider = self._get_active_provider()

        if not provider:
            return {
                "success": False,
                "error": "No LLM provider available. Configure Claude CLI or set OPENAI_API_KEY."
            }

        start_time = time.time()
        input_word_count = len(transcript.split())

        # Build the prompts
        system_prompt = PROMPT_GENERATOR_SYSTEM_PROMPT
        user_prompt = build_user_prompt(
            transcript=transcript,
            video_title=video_title,
            video_author=video_author,
            discovery_summary=discovery_summary,
            content_summary=content_summary,
            categories=categories
        )

        logger.info(f"Generating prompts with {provider_name} provider for {input_word_count} words of content")

        if provider_name == "claude":
            result = await self._generate_with_claude(
                system_prompt, user_prompt, video_title, video_id, video_url,
                input_word_count, categories, start_time
            )
        else:
            result = await self._generate_with_openai(
                system_prompt, user_prompt, video_title, video_id, video_url,
                input_word_count, categories, start_time
            )

        # Add analysis types used
        if result.get("success") and result.get("result"):
            analysis_types = []
            if discovery_summary:
                analysis_types.append("discovery")
            if content_summary:
                analysis_types.append("summary")
            result["result"].analysis_types_used = analysis_types

        return result

    async def _generate_with_claude(
        self,
        system_prompt: str,
        user_prompt: str,
        video_title: Optional[str],
        video_id: Optional[str],
        video_url: Optional[str],
        input_word_count: int,
        categories: Optional[List[PromptCategory]],
        start_time: float
    ) -> Dict[str, Any]:
        """Generate prompts using Claude CLI."""
        try:
            result = self.claude_provider.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model="claude-opus-4-5-20251101",
                response_format="json"
            )

            if not result["success"]:
                logger.error(f"Claude prompt generation failed: {result['error']}")
                # Try fallback to OpenAI if in auto mode
                if self.provider == "auto" and self.openai_client:
                    logger.info("Falling back to OpenAI...")
                    return await self._generate_with_openai(
                        system_prompt, user_prompt, video_title, video_id, video_url,
                        input_word_count, categories, start_time
                    )
                return {
                    "success": False,
                    "error": f"Claude generation failed: {result['error']}"
                }

            response_text = result["content"]
            tokens_used = result["tokens_used"]

            try:
                raw_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Claude response: {e}")
                return {
                    "success": False,
                    "error": f"Failed to parse response: {str(e)}"
                }

            # Convert to PromptGeneratorResult
            generator_result = self._parse_result(
                raw_data=raw_data,
                video_title=video_title or "Untitled Content",
                video_id=video_id,
                video_url=video_url,
                input_word_count=input_word_count,
                tokens_used=tokens_used,
                duration=time.time() - start_time,
                model_used="claude-opus-4-5-20251101"
            )

            logger.info(f"Claude generated {generator_result.total_prompts} prompts in {time.time() - start_time:.1f}s")

            return {
                "success": True,
                "result": generator_result,
                "tokens_used": tokens_used,
                "provider": "claude"
            }

        except Exception as e:
            logger.error(f"Unexpected error during Claude generation: {e}")
            if self.provider == "auto" and self.openai_client:
                logger.info("Falling back to OpenAI due to error...")
                return await self._generate_with_openai(
                    system_prompt, user_prompt, video_title, video_id, video_url,
                    input_word_count, categories, start_time
                )
            return {
                "success": False,
                "error": f"Claude generation failed: {str(e)}"
            }

    async def _generate_with_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        video_title: Optional[str],
        video_id: Optional[str],
        video_url: Optional[str],
        input_word_count: int,
        categories: Optional[List[PromptCategory]],
        start_time: float
    ) -> Dict[str, Any]:
        """Generate prompts using OpenAI GPT-4o."""
        if not self.openai_client:
            return {
                "success": False,
                "error": "OpenAI API key not configured"
            }

        try:
            logger.info("Generating prompts with OpenAI GPT-4o...")

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,
                max_tokens=16000,  # Large to accommodate 7 detailed prompts
                response_format={"type": "json_object"}
            )

            response_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0

            try:
                raw_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response: {e}")
                return {
                    "success": False,
                    "error": f"Failed to parse response: {str(e)}"
                }

            # Convert to PromptGeneratorResult
            generator_result = self._parse_result(
                raw_data=raw_data,
                video_title=video_title or "Untitled Content",
                video_id=video_id,
                video_url=video_url,
                input_word_count=input_word_count,
                tokens_used=tokens_used,
                duration=time.time() - start_time,
                model_used="gpt-4o"
            )

            logger.info(f"OpenAI generated {generator_result.total_prompts} prompts in {time.time() - start_time:.1f}s")

            return {
                "success": True,
                "result": generator_result,
                "tokens_used": tokens_used,
                "provider": "openai"
            }

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return {
                "success": False,
                "error": f"OpenAI generation failed: {str(e)}"
            }

    def _parse_result(
        self,
        raw_data: Dict[str, Any],
        video_title: str,
        video_id: Optional[str],
        video_url: Optional[str],
        input_word_count: int,
        tokens_used: int,
        duration: float,
        model_used: str
    ) -> PromptGeneratorResult:
        """Parse raw LLM response into PromptGeneratorResult."""

        prompts = []
        prompts_by_category = {}
        total_word_count = 0

        raw_prompts = raw_data.get("prompts", [])

        for raw_prompt in raw_prompts:
            try:
                category_str = raw_prompt.get("category", "")
                try:
                    category = PromptCategory(category_str)
                except ValueError:
                    logger.warning(f"Unknown category: {category_str}")
                    continue

                # Get category info
                cat_info = CATEGORY_INFO.get(category, {})

                # Calculate word count
                prompt_content = raw_prompt.get("prompt_content", "")
                word_count = len(prompt_content.split())
                total_word_count += word_count

                prompt = GeneratedPrompt(
                    prompt_id=raw_prompt.get("prompt_id", f"prompt-{category.value}-{uuid.uuid4().hex[:8]}"),
                    category=category,
                    category_name=raw_prompt.get("category_name", cat_info.get("name", category.value)),
                    category_icon=raw_prompt.get("category_icon", cat_info.get("icon", "📝")),
                    title=raw_prompt.get("title", f"{cat_info.get('name', 'Unknown')} Prompt"),
                    description=raw_prompt.get("description", ""),
                    prompt_content=prompt_content,
                    intent_specification=raw_prompt.get("intent_specification", ""),
                    disambiguation_questions=raw_prompt.get("disambiguation_questions", []),
                    failure_conditions=raw_prompt.get("failure_conditions", []),
                    success_criteria=raw_prompt.get("success_criteria", []),
                    video_context_used=raw_prompt.get("video_context_used", []),
                    analysis_context_used=raw_prompt.get("analysis_context_used", []),
                    target_tool=raw_prompt.get("target_tool", cat_info.get("target_tool", "AI Assistant")),
                    estimated_output_type=raw_prompt.get("estimated_output_type", ""),
                    word_count=word_count
                )

                prompts.append(prompt)
                prompts_by_category[category.value] = prompt

            except Exception as e:
                logger.warning(f"Failed to parse prompt: {e}")
                continue

        return PromptGeneratorResult(
            content_title=video_title,
            source_id=video_id,
            source_url=video_url or (f"https://www.youtube.com/watch?v={video_id}" if video_id else None),
            prompts=prompts,
            prompts_by_category=prompts_by_category,
            total_prompts=len(prompts),
            total_word_count=total_word_count,
            input_word_count=input_word_count,
            tokens_used=tokens_used,
            analysis_duration_seconds=duration,
            model_used=model_used
        )


# Singleton instance
_prompt_generator_service: Optional[PromptGeneratorService] = None


def get_prompt_generator_service() -> PromptGeneratorService:
    """Get or create the prompt generator service singleton."""
    global _prompt_generator_service
    if _prompt_generator_service is None:
        _prompt_generator_service = PromptGeneratorService()
    return _prompt_generator_service
