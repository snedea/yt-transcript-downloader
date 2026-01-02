"""
Discovery Mode analysis service.

Implements the "Kinoshita Pattern" for cross-domain knowledge transfer:
Extracts problems, techniques, cross-domain applications, research trail,
and experiment ideas from any content source.

Supports two LLM providers:
1. Claude (via CLI) - Primary, uses existing subscription (free)
2. OpenAI GPT-4o - Fallback if Claude unavailable
"""

import json
import logging
import os
import time
import uuid
from typing import Dict, Any, Optional, List

from openai import OpenAI, OpenAIError, RateLimitError, AuthenticationError

from app.config import settings
from app.models.content import ContentSourceType, UnifiedContent
from app.models.discovery import (
    Problem,
    Technique,
    CrossDomainApplication,
    ResearchReference,
    ExperimentIdea,
    DiscoveryResult,
)
from app.services.claude_provider import get_claude_provider, LocalClaudeProvider

logger = logging.getLogger(__name__)

# Provider preference: "claude" (default), "openai", or "auto" (claude first, then openai)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto")


# JSON Schema for GPT-4o structured output
DISCOVERY_SCHEMA = {
    "type": "object",
    "properties": {
        "problems": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "statement": {"type": "string"},
                    "context": {"type": "string"},
                    "blockers": {"type": "array", "items": {"type": "string"}},
                    "domain": {"type": "string"},
                    "timestamp": {"type": "number"}
                },
                "required": ["statement", "context", "blockers", "domain"]
            }
        },
        "techniques": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "principle": {"type": "string"},
                    "implementation": {"type": "string"},
                    "requirements": {"type": "array", "items": {"type": "string"}},
                    "domain": {"type": "string"},
                    "source": {"type": "string"},
                    "timestamp": {"type": "number"}
                },
                "required": ["name", "principle", "implementation", "domain"]
            }
        },
        "cross_domain_applications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source_technique_name": {"type": "string"},
                    "target_domain": {"type": "string"},
                    "hypothesis": {"type": "string"},
                    "potential_problems_solved": {"type": "array", "items": {"type": "string"}},
                    "adaptation_needed": {"type": "string"},
                    "confidence": {"type": "number"},
                    "similar_existing_work": {"type": "string"}
                },
                "required": ["source_technique_name", "target_domain", "hypothesis", "confidence"]
            }
        },
        "research_trail": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "authors": {"type": "array", "items": {"type": "string"}},
                    "year": {"type": "integer"},
                    "domain": {"type": "string"},
                    "relevance": {"type": "string"},
                    "mentioned_at": {"type": "number"}
                },
                "required": ["domain", "relevance"]
            }
        },
        "key_insights": {
            "type": "array",
            "items": {"type": "string"}
        },
        "recommended_reads": {
            "type": "array",
            "items": {"type": "string"}
        },
        "experiment_ideas": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]},
                    "time_estimate": {"type": "string"},
                    "prerequisites": {"type": "array", "items": {"type": "string"}},
                    "success_criteria": {"type": "array", "items": {"type": "string"}},
                    "llm_prompt": {"type": "string"},
                    "related_techniques": {"type": "array", "items": {"type": "string"}},
                    "related_problems": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["title", "description", "difficulty", "llm_prompt"]
            }
        }
    },
    "required": ["problems", "techniques", "cross_domain_applications", "key_insights", "experiment_ideas"]
}


class DiscoveryService:
    """Service for Kinoshita Pattern discovery analysis."""

    def __init__(self):
        """Initialize with available LLM providers."""
        # Claude provider (uses CLI, rides subscription)
        self.claude_provider = get_claude_provider()

        # OpenAI provider (requires API key)
        if settings.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.openai_client = None

        # Determine which provider to use
        self.provider = LLM_PROVIDER
        logger.info(f"Discovery service initialized with provider preference: {self.provider}")

    def is_available(self) -> bool:
        """Check if any LLM provider is available."""
        if self.provider == "claude":
            return self.claude_provider.is_available()
        elif self.provider == "openai":
            return self.openai_client is not None
        else:  # auto
            return self.claude_provider.is_available() or self.openai_client is not None

    def _get_active_provider(self) -> tuple[str, Any]:
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

    async def analyze(
        self,
        content: UnifiedContent,
        focus_domains: Optional[List[str]] = None,
        max_applications: int = 5
    ) -> Dict[str, Any]:
        """
        Perform discovery analysis on content using the Kinoshita Pattern.

        Args:
            content: Unified content to analyze
            focus_domains: Optional list of domains to focus cross-domain suggestions
            max_applications: Maximum cross-domain applications to generate

        Returns:
            Dictionary with success status and DiscoveryResult or error
        """
        provider_name, provider = self._get_active_provider()

        if not provider:
            return {
                "success": False,
                "error": "No LLM provider available. Configure Claude CLI or set OPENAI_API_KEY."
            }

        start_time = time.time()

        # Build the analysis prompt
        system_prompt = self._build_system_prompt(focus_domains, max_applications)
        user_prompt = self._build_user_prompt(content)

        logger.info(f"Running discovery analysis with {provider_name} provider")

        if provider_name == "claude":
            return await self._analyze_with_claude(
                system_prompt, user_prompt, content, start_time
            )
        else:
            return await self._analyze_with_openai(
                system_prompt, user_prompt, content, start_time
            )

    async def _analyze_with_claude(
        self,
        system_prompt: str,
        user_prompt: str,
        content: UnifiedContent,
        start_time: float
    ) -> Dict[str, Any]:
        """Run analysis using Claude CLI."""
        try:
            result = self.claude_provider.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model="claude-opus-4-5-20251101",
                response_format="json"
            )

            if not result["success"]:
                logger.error(f"Claude analysis failed: {result['error']}")
                # Try fallback to OpenAI if in auto mode
                if self.provider == "auto" and self.openai_client:
                    logger.info("Falling back to OpenAI...")
                    return await self._analyze_with_openai(
                        system_prompt, user_prompt, content, start_time
                    )
                return {
                    "success": False,
                    "error": f"Claude analysis failed: {result['error']}"
                }

            analysis_text = result["content"]
            tokens_used = result["tokens_used"]

            try:
                raw_data = json.loads(analysis_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Claude response: {e}")
                return {
                    "success": False,
                    "error": f"Failed to parse analysis response: {str(e)}"
                }

            # Convert raw data to DiscoveryResult
            discovery_result = self._parse_result(
                raw_data=raw_data,
                content=content,
                tokens_used=tokens_used,
                duration=time.time() - start_time
            )

            logger.info(f"Claude analysis completed in {time.time() - start_time:.1f}s")

            return {
                "success": True,
                "result": discovery_result,
                "tokens_used": tokens_used,
                "provider": "claude"
            }

        except Exception as e:
            logger.error(f"Unexpected error during Claude analysis: {e}")
            # Try fallback to OpenAI if in auto mode
            if self.provider == "auto" and self.openai_client:
                logger.info("Falling back to OpenAI due to error...")
                return await self._analyze_with_openai(
                    system_prompt, user_prompt, content, start_time
                )
            return {
                "success": False,
                "error": f"Claude analysis failed: {str(e)}"
            }

    async def _analyze_with_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        content: UnifiedContent,
        start_time: float
    ) -> Dict[str, Any]:
        """Run analysis using OpenAI GPT-4o."""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,
                max_tokens=8000,
                response_format={"type": "json_object"}
            )

            analysis_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            try:
                raw_data = json.loads(analysis_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse GPT response: {e}")
                return {
                    "success": False,
                    "error": f"Failed to parse analysis response: {str(e)}"
                }

            # Convert raw data to DiscoveryResult
            discovery_result = self._parse_result(
                raw_data=raw_data,
                content=content,
                tokens_used=tokens_used,
                duration=time.time() - start_time
            )

            logger.info(f"OpenAI analysis completed in {time.time() - start_time:.1f}s")

            return {
                "success": True,
                "result": discovery_result,
                "tokens_used": tokens_used,
                "provider": "openai"
            }

        except AuthenticationError:
            return {
                "success": False,
                "error": "Invalid OpenAI API key"
            }
        except RateLimitError:
            return {
                "success": False,
                "error": "OpenAI rate limit exceeded. Please try again later."
            }
        except OpenAIError as e:
            logger.error(f"OpenAI API error during discovery analysis: {e}")
            return {
                "success": False,
                "error": f"OpenAI API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error during discovery analysis: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

    def _build_system_prompt(
        self,
        focus_domains: Optional[List[str]] = None,
        max_applications: int = 5
    ) -> str:
        """Build the system prompt for discovery analysis."""

        focus_section = ""
        if focus_domains:
            domains_str = ", ".join(focus_domains)
            focus_section = f"""
## Focus Domains
When generating cross-domain applications, prioritize these domains: {domains_str}
"""

        return f"""You are an expert at identifying cross-domain knowledge transfer opportunities, inspired by how Hiroo Kinoshita discovered EUV lithography.

## The Kinoshita Pattern

Kinoshita made a breakthrough discovery by:
1. Having a clear PROBLEM (wanted 10nm X-ray lithography)
2. Identifying BLOCKERS (X-rays absorbed by lenses/air)
3. Cross-domain research (found Underwood & Barbee's X-ray mirror paper from nuclear physics)
4. Recognizing a TRANSFERABLE PRINCIPLE ("curved mirrors can focus light like lenses")
5. Adapting the TECHNIQUE (modified tungsten-carbon mirrors for his wavelength)
6. Creating something new (EUV lithography - now used in every modern chip)

## Your Task

Analyze the provided content and extract:

### 1. PROBLEMS (What challenges are discussed?)
- What is the desired outcome?
- What blockers or constraints prevent achieving it?
- What domain is this problem in?

### 2. TECHNIQUES (What methods or solutions are described?)
- What is the core principle/mechanism?
- How is it implemented?
- What requirements does it have?
- Where did it originate?

### 3. CROSS-DOMAIN APPLICATIONS (Where else could these techniques apply?)
Generate up to {max_applications} creative but plausible applications:
- What other fields have similar problems?
- How would the technique need to be adapted?
- Rate your confidence (0.0-1.0) based on feasibility
- Note any existing similar work
{focus_section}
### 4. RESEARCH TRAIL (What sources are mentioned?)
- Papers, researchers, or prior work referenced
- Why each is relevant

### 5. SYNTHESIS
- Key insights (top 3-5 takeaways)
- Recommended reading for deeper exploration

### 6. EXPERIMENT IDEAS WITH LLM PROMPTS
For each experiment idea, generate a COMPLETE, KICK-ASS prompt that someone can copy-paste directly into an LLM (Claude, GPT-4, etc.) to execute that experiment.

**THE PROMPT MUST INCLUDE ALL OF THESE SECTIONS:**

```
<context>
- Detailed background from the source content (not generic!)
- Specific facts, numbers, techniques mentioned in the original
- Why this matters and what problem it addresses
- Any relevant equations, principles, or mechanisms
</context>

<task>
- Exactly what to do, step by step
- Specific domain or dataset to apply this to
- Clear deliverables
</task>

<research_queries>
- 3-5 specific search queries to find relevant papers/resources
- Keywords and phrases to look for
- Names of researchers or papers to find
</research_queries>

<starter_code>
- Python/JavaScript code skeleton to get started (if applicable)
- Key functions or algorithms needed
- Libraries to import
</starter_code>

<sources_to_check>
- Specific papers, websites, or databases to consult
- ArXiv categories, Google Scholar queries
- GitHub repos or tools to use
</sources_to_check>

<success_criteria>
- Measurable outcomes that indicate success
- What the final output should look like
- How to validate results
</success_criteria>

<agent_instructions>
- If using an AI agent, specific tool calls to make
- Web searches to perform
- Code to execute
</agent_instructions>
```

**CRITICAL**: The llm_prompt field must be 500-2000 characters. Include SPECIFIC details from the source content - names, numbers, techniques, principles. NOT generic advice. The prompt should let someone with NO context from the original content still execute the experiment successfully.

## Output Format

Return valid JSON with these EXACT field names:

```json
{{
  "problems": [
    {{
      "statement": "The main problem being solved",
      "context": "Background and why it matters",
      "blockers": ["blocker 1", "blocker 2"],
      "domain": "The field this problem is in"
    }}
  ],
  "techniques": [
    {{
      "name": "Name of the technique",
      "principle": "Core mechanism/why it works",
      "implementation": "How it's applied",
      "requirements": ["requirement 1"],
      "domain": "Original domain",
      "source": "Original researcher/paper if mentioned"
    }}
  ],
  "cross_domain_applications": [
    {{
      "source_technique_name": "Name of technique being transferred",
      "target_domain": "The NEW field where this could apply (e.g., 'Medical Imaging', 'Aerospace', 'Materials Science')",
      "hypothesis": "What if we applied X to Y?",
      "potential_problems_solved": ["problem this could solve"],
      "adaptation_needed": "How to modify for new domain",
      "confidence": 0.7
    }}
  ],
  "research_trail": [
    {{
      "title": "Paper title if known",
      "authors": ["author names"],
      "year": 1986,
      "domain": "Field",
      "relevance": "Why it's relevant"
    }}
  ],
  "key_insights": ["insight 1", "insight 2"],
  "recommended_reads": ["reading suggestion 1"],
  "experiment_ideas": [
    {{
      "title": "Short actionable title",
      "description": "What this experiment explores and why it matters",
      "difficulty": "easy|medium|hard",
      "time_estimate": "2-4 hours",
      "prerequisites": ["prerequisite 1"],
      "success_criteria": ["How to know if it worked"],
      "related_techniques": ["technique names from above"],
      "related_problems": ["problem statements from above"],
      "llm_prompt": "<context>\\nDetailed background with SPECIFIC facts from the source: names, numbers, equations, principles. Example: 'Benford's Law states leading digit d appears with probability log10(1 + 1/d), meaning ~30% start with 1, ~17.5% with 2. Used to detect fraud in tax returns and election data.'\\n</context>\\n\\n<task>\\n1. Specific step one\\n2. Specific step two\\n3. What to produce\\n</task>\\n\\n<research_queries>\\n- 'benford law [specific domain]'\\n- 'first digit distribution anomaly'\\n- Author names to search\\n</research_queries>\\n\\n<starter_code>\\nimport numpy as np\\ndef benford_expected():\\n    return {{d: np.log10(1 + 1/d) for d in range(1, 10)}}\\n</starter_code>\\n\\n<sources_to_check>\\n- ArXiv: stat.AP (applications)\\n- Specific paper titles mentioned\\n</sources_to_check>\\n\\n<success_criteria>\\n- Collect 1000+ data points\\n- Chi-square test p-value < 0.05 indicates anomaly\\n- Visualization comparing observed vs expected\\n</success_criteria>"
    }}
  ]
}}
```

IMPORTANT: For cross_domain_applications, the "target_domain" field is REQUIRED and must be a specific, named field (e.g., "Medical Imaging", "Biotechnology", "Renewable Energy", "Aerospace").

Be thorough but accurate. Only include things actually mentioned or strongly implied in the content.
For cross-domain applications, be creative but ground suggestions in real feasibility."""

    def _build_user_prompt(self, content: UnifiedContent) -> str:
        """Build the user prompt with content details."""

        source_info = f"Source Type: {content.source_type.value}"
        if content.source_url:
            source_info += f"\nSource URL: {content.source_url}"
        if content.author:
            source_info += f"\nAuthor: {content.author}"

        return f"""## Content to Analyze

Title: {content.title}
{source_info}
Word Count: {content.word_count}

---

{content.text}

---

Analyze this content using the Kinoshita Pattern. Extract problems, techniques, cross-domain applications, and insights."""

    def _parse_result(
        self,
        raw_data: Dict[str, Any],
        content: UnifiedContent,
        tokens_used: int,
        duration: float
    ) -> DiscoveryResult:
        """Parse GPT response into DiscoveryResult model."""

        # Parse problems
        problems = []
        for i, p in enumerate(raw_data.get("problems", [])):
            problems.append(Problem(
                problem_id=f"prob-{i+1:03d}",
                statement=p.get("statement", ""),
                context=p.get("context", ""),
                blockers=p.get("blockers", []),
                domain=p.get("domain", "Unknown"),
                timestamp=p.get("timestamp")
            ))

        # Parse techniques
        techniques = []
        technique_name_to_id = {}
        for i, t in enumerate(raw_data.get("techniques", [])):
            tech_id = f"tech-{i+1:03d}"
            name = t.get("name", f"Technique {i+1}")
            technique_name_to_id[name.lower()] = tech_id

            techniques.append(Technique(
                technique_id=tech_id,
                name=name,
                principle=t.get("principle", ""),
                implementation=t.get("implementation", ""),
                requirements=t.get("requirements", []),
                domain=t.get("domain", "Unknown"),
                source=t.get("source"),
                timestamp=t.get("timestamp")
            ))

        # Parse cross-domain applications
        applications = []
        for i, a in enumerate(raw_data.get("cross_domain_applications", [])):
            # Try to link to technique by name
            source_tech_name = a.get("source_technique_name", "").lower()
            source_tech_id = technique_name_to_id.get(
                source_tech_name,
                f"tech-{source_tech_name[:8]}"
            )

            applications.append(CrossDomainApplication(
                application_id=f"app-{i+1:03d}",
                source_technique=source_tech_id,
                target_domain=a.get("target_domain", "Unknown"),
                hypothesis=a.get("hypothesis", ""),
                potential_problems_solved=a.get("potential_problems_solved", []),
                adaptation_needed=a.get("adaptation_needed", ""),
                confidence=min(1.0, max(0.0, a.get("confidence", 0.5))),
                similar_existing_work=a.get("similar_existing_work")
            ))

        # Parse research trail
        references = []
        for i, r in enumerate(raw_data.get("research_trail", [])):
            references.append(ResearchReference(
                reference_id=f"ref-{i+1:03d}",
                title=r.get("title"),
                authors=r.get("authors", []),
                year=r.get("year"),
                domain=r.get("domain", "Unknown"),
                relevance=r.get("relevance", ""),
                mentioned_at=r.get("mentioned_at")
            ))

        # Parse experiment ideas with LLM prompts
        experiments = []
        for i, e in enumerate(raw_data.get("experiment_ideas", [])):
            # Handle both old string format and new object format
            if isinstance(e, str):
                # Legacy format - convert string to ExperimentIdea
                experiments.append(ExperimentIdea(
                    experiment_id=f"exp-{i+1:03d}",
                    title=e[:100] if len(e) > 100 else e,
                    description=e,
                    difficulty="medium",
                    time_estimate="varies",
                    prerequisites=[],
                    success_criteria=[],
                    llm_prompt=f"Help me execute this experiment: {e}",
                    related_techniques=[],
                    related_problems=[]
                ))
            else:
                # New structured format
                experiments.append(ExperimentIdea(
                    experiment_id=f"exp-{i+1:03d}",
                    title=e.get("title", f"Experiment {i+1}"),
                    description=e.get("description", ""),
                    difficulty=e.get("difficulty", "medium"),
                    time_estimate=e.get("time_estimate", "varies"),
                    prerequisites=e.get("prerequisites", []),
                    success_criteria=e.get("success_criteria", []),
                    llm_prompt=e.get("llm_prompt", ""),
                    related_techniques=e.get("related_techniques", []),
                    related_problems=e.get("related_problems", [])
                ))

        return DiscoveryResult(
            content_title=content.title,
            source_type=content.source_type,
            source_id=content.source_id,
            source_url=content.source_url,
            problems=problems,
            techniques=techniques,
            cross_domain_applications=applications,
            research_trail=references,
            key_insights=raw_data.get("key_insights", []),
            recommended_reads=raw_data.get("recommended_reads", []),
            experiment_ideas=experiments,
            tokens_used=tokens_used,
            analysis_duration_seconds=duration
        )
