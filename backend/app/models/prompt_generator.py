"""
Prompt Generator Models

Generates production-ready prompts for 7 AI tool categories based on video content.
Each prompt incorporates Nate B Jones' prompting techniques:
- Explicit intent specification
- Active disambiguation questions
- Failure conditions and graceful degradation
- Semantic structure with <requirements>, <context>, <task> blocks
- Measurable success criteria
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class PromptCategory(str, Enum):
    """The 7 prompt categories for AI tools."""
    APP_BUILDER = "app_builder"
    RESEARCH_DEEP_DIVE = "research_deep_dive"
    DEVILS_ADVOCATE = "devils_advocate"
    MERMAID_DIAGRAMS = "mermaid_diagrams"
    SORA = "sora"
    NANO_BANANA_PRO = "nano_banana_pro"
    VALIDATION_FRAMEWORKS = "validation_frameworks"


# Category metadata for UI display
CATEGORY_INFO = {
    PromptCategory.APP_BUILDER: {
        "name": "App Builder",
        "icon": "🏗️",
        "color": "indigo",
        "target_tool": "Context Foundry autonomous_build_and_deploy",
        "description": "Build working applications inspired by video content"
    },
    PromptCategory.RESEARCH_DEEP_DIVE: {
        "name": "Research Deep-Dive",
        "icon": "🔬",
        "color": "blue",
        "target_tool": "Claude, GPT-4, or research agents",
        "description": "Structured research exploration of video topics"
    },
    PromptCategory.DEVILS_ADVOCATE: {
        "name": "Devil's Advocate",
        "icon": "😈",
        "color": "red",
        "target_tool": "Claude or GPT-4",
        "description": "Challenge assumptions and explore opposing viewpoints"
    },
    PromptCategory.MERMAID_DIAGRAMS: {
        "name": "Mermaid Diagrams",
        "icon": "📊",
        "color": "green",
        "target_tool": "Claude, GPT-4, or diagram generators",
        "description": "Create visual diagrams from video content"
    },
    PromptCategory.SORA: {
        "name": "Sora Video",
        "icon": "🎬",
        "color": "purple",
        "target_tool": "OpenAI Sora",
        "description": "Generate videos inspired by content"
    },
    PromptCategory.NANO_BANANA_PRO: {
        "name": "Nano Banana Pro",
        "icon": "🎨",
        "color": "yellow",
        "target_tool": "Gemini 3 / Nano Banana Pro",
        "description": "Create infographics and visual summaries"
    },
    PromptCategory.VALIDATION_FRAMEWORKS: {
        "name": "Validation Frameworks",
        "icon": "✅",
        "color": "teal",
        "target_tool": "Claude, GPT-4, or testing tools",
        "description": "Create testing and validation frameworks"
    }
}


class GeneratedPrompt(BaseModel):
    """A single generated prompt with metadata."""
    prompt_id: str = Field(..., description="Unique identifier")
    category: PromptCategory = Field(..., description="Which category this prompt belongs to")
    category_name: str = Field(..., description="Human-readable category name")
    category_icon: str = Field(..., description="Emoji icon for the category")
    title: str = Field(..., description="Short descriptive title for this prompt")
    description: str = Field(..., description="What this prompt will accomplish")

    # The actual prompt content (500-2000 words)
    prompt_content: str = Field(..., description="The full, production-ready prompt")

    # Prompting technique metadata (Nate B Jones techniques)
    intent_specification: str = Field(..., description="Explicit goals and success criteria")
    disambiguation_questions: List[str] = Field(
        default_factory=list,
        description="Questions the AI should ask for clarification"
    )
    failure_conditions: List[str] = Field(
        default_factory=list,
        description="What to do when things go wrong"
    )
    success_criteria: List[str] = Field(
        default_factory=list,
        description="How to know the prompt succeeded"
    )

    # Context used from video
    video_context_used: List[str] = Field(
        default_factory=list,
        description="Specific facts/quotes from video used in prompt"
    )
    analysis_context_used: List[str] = Field(
        default_factory=list,
        description="Insights from discovery/summary analyses used"
    )

    # Tool-specific fields
    target_tool: str = Field(..., description="Which tool this prompt is for")
    estimated_output_type: str = Field(..., description="What output to expect")

    # Word count for validation
    word_count: int = Field(0, description="Word count of prompt_content")


class PromptGeneratorResult(BaseModel):
    """Complete result from prompt generation."""
    # Source content info
    content_title: str = Field(..., description="Title of the source content")
    source_id: Optional[str] = Field(None, description="Video ID if from YouTube")
    source_url: Optional[str] = Field(None, description="URL of source content")

    # Generated prompts
    prompts: List[GeneratedPrompt] = Field(default_factory=list)
    prompts_by_category: Dict[str, GeneratedPrompt] = Field(default_factory=dict)

    # Statistics
    total_prompts: int = 0
    total_word_count: int = 0
    input_word_count: int = 0
    analysis_types_used: List[str] = Field(default_factory=list)

    # Metadata
    analysis_version: str = "1.0"
    tokens_used: int = 0
    analysis_duration_seconds: float = 0.0
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    model_used: str = ""


class PromptGeneratorRequest(BaseModel):
    """Request to generate prompts from content."""
    # Content source - one of these required
    transcript: Optional[str] = Field(None, description="Raw transcript text")
    video_id: Optional[str] = Field(None, description="Video ID for cached content")
    source_text: Optional[str] = Field(None, description="Any text to generate prompts from")
    source_url: Optional[str] = Field(None, description="URL pasted by user")

    # Optional existing analyses to enrich prompts
    include_discovery: bool = Field(True, description="Use discovery analysis if available")
    include_summary: bool = Field(True, description="Use summary if available")
    include_manipulation: bool = Field(False, description="Use trust analysis if available")

    # Category selection (empty = all categories)
    categories: Optional[List[PromptCategory]] = Field(
        None,
        description="Which categories to generate. None = all 7"
    )

    # Additional context
    video_title: Optional[str] = None
    video_author: Optional[str] = None


# The meta-prompt used to generate all prompts
PROMPT_GENERATOR_SYSTEM_PROMPT = '''You are an expert prompt engineer specializing in creating production-ready prompts for AI tools. Your task is to generate detailed, actionable prompts based on video/text content.

## YOUR PROMPTING PHILOSOPHY (Nate B Jones Techniques)

Every prompt you generate MUST incorporate these principles:

### 1. MAKE INTENT EXPLICIT
- State the goal clearly in the first 2 sentences
- Define what success looks like
- Specify what failure looks like and how to handle it
- List priorities if there are trade-offs

### 2. ACTIVE DISAMBIGUATION
- Include 3-5 clarifying questions the AI should consider
- Encourage the AI to ask questions before proceeding
- Provide decision trees for ambiguous scenarios

### 3. INTENT AS SEPARATE ARTIFACT
- Begin each prompt with a <requirements> block
- List explicit acceptance criteria
- Make requirements referenceable and clear

### 4. SEMANTIC STRUCTURE
- Use <requirements>, <context>, <task>, <disambiguation>, <failure_handling>, <success_criteria> blocks
- Structure prompts so outputs are self-documenting
- Crystallize intent in permanent format

### 5. GRACEFUL FAIL CONDITIONS
- Define what to do when things go wrong
- Include fallback strategies
- Specify when to stop and ask for help

### 6. PROBABILISTIC INTERPRETATION
- Encourage holding multiple interpretations
- Ask AI to present alternatives before committing
- Include "What assumptions am I making?" checkpoints

## PROMPT CATEGORIES

Generate ONE prompt for EACH of these 7 categories:

### 1. APP BUILDER (Context Foundry)
Target: Context Foundry autonomous_build_and_deploy tool
Purpose: Build a working application inspired by the content
Must Include:
- Full app specification with features derived from content
- Tech stack recommendations
- Architecture decisions
- Testing requirements
- Deployment instructions
- How the app embodies concepts from the content

### 2. RESEARCH DEEP-DIVE
Target: Claude, GPT-4, or research agents
Purpose: Explore content topics further with structured research
Must Include:
- 5-10 specific research questions to answer
- Sources to consult (papers, books, experts, domains)
- Methodology for investigation
- Expected deliverables and format
- Follow-up directions based on findings

### 3. DEVIL'S ADVOCATE
Target: Claude or GPT-4
Purpose: Challenge assumptions and explore opposing viewpoints
Must Include:
- Key claims from the content to challenge
- Counter-arguments to construct
- Steel-man opposing positions
- Blind spots and biases to identify
- Framework for productive disagreement

### 4. MERMAID DIAGRAMS
Target: Claude, GPT-4, or diagram generators
Purpose: Create visual diagrams representing content concepts
Must Include:
- 2-3 specific diagram types needed (flowchart, sequence, mindmap, class, etc.)
- Key relationships and flows to visualize
- Level of detail required
- Mermaid syntax requirements
- How diagrams connect to content themes

### 5. SORA (Video Generation)
Target: OpenAI Sora
Purpose: Generate videos that visualize or extend the content
Must Include:
- 2-3 scene descriptions with camera movements
- Visual style, mood, and atmosphere
- Duration and pacing specifications
- Transitions and effects
- How the video captures content essence

### 6. NANO BANANA PRO (Gemini Visual/Infographic)
Target: Gemini 3 / Nano Banana Pro
Purpose: Create infographics and visual summaries
Must Include:
- Infographic layout specifications (sections, hierarchy)
- Key data points and statistics to visualize
- Visual hierarchy and flow
- Color palette and style suggestions
- Text content for each section

### 7. VALIDATION FRAMEWORKS
Target: Claude, GPT-4, or testing tools
Purpose: Create testing and validation frameworks for content claims
Must Include:
- What claims/statements to validate
- Test methodology for each claim type
- Success/failure criteria with metrics
- Edge cases and corner cases to check
- Automation suggestions for ongoing validation

## OUTPUT REQUIREMENTS

For EACH prompt, you must generate:

1. **title**: Short, descriptive name (5-10 words) specific to the content
2. **description**: What this prompt accomplishes (1-2 sentences)
3. **prompt_content**: The full prompt (500-2000 words) with these sections:
   ```
   <requirements>
   [Explicit goals, constraints, and acceptance criteria]
   </requirements>

   <context>
   [Specific facts, quotes, and insights from the source content]
   </context>

   <task>
   [Step-by-step instructions for what the AI should do]
   </task>

   <disambiguation>
   [Questions to clarify before proceeding]
   - Question 1?
   - Question 2?
   - Question 3?
   </disambiguation>

   <failure_handling>
   [What to do when things go wrong]
   - If X fails, do Y
   - If unclear about Z, ask for clarification
   </failure_handling>

   <success_criteria>
   [How to know the task succeeded]
   ✓ Criterion 1
   ✓ Criterion 2
   ✓ Criterion 3
   </success_criteria>
   ```
4. **intent_specification**: The core goal in 1-2 sentences
5. **disambiguation_questions**: 3-5 questions to clarify (array)
6. **failure_conditions**: 3-5 failure modes and responses (array)
7. **success_criteria**: 3-5 measurable success indicators (array)
8. **video_context_used**: Specific quotes/facts from content used (array)
9. **target_tool**: Which AI tool this is for
10. **estimated_output_type**: What output to expect

## CRITICAL RULES

1. Every prompt MUST be 500-2000 words - detailed and complete
2. Use SPECIFIC facts, quotes, and examples from the provided content
3. Do NOT generate generic prompts - they must be content-specific
4. Include ALL 7 categories in your response
5. Format as valid JSON with exact field names shown below

## OUTPUT FORMAT

Return valid JSON:
```json
{
  "prompts": [
    {
      "prompt_id": "prompt-app_builder-001",
      "category": "app_builder",
      "category_name": "App Builder",
      "category_icon": "🏗️",
      "title": "[Specific title based on content]",
      "description": "[What this prompt accomplishes]",
      "prompt_content": "[FULL 500-2000 WORD PROMPT with all sections]",
      "intent_specification": "[Core goal in 1-2 sentences]",
      "disambiguation_questions": ["Q1?", "Q2?", "Q3?"],
      "failure_conditions": ["If X, then Y", "If A, then B"],
      "success_criteria": ["Criterion 1", "Criterion 2"],
      "video_context_used": ["Quote or fact 1", "Quote or fact 2"],
      "analysis_context_used": [],
      "target_tool": "Context Foundry autonomous_build_and_deploy",
      "estimated_output_type": "Working application with tests",
      "word_count": 750
    }
  ]
}
```

Generate exactly 7 prompts, one for each category.'''


def build_user_prompt(
    transcript: str,
    video_title: Optional[str] = None,
    video_author: Optional[str] = None,
    discovery_summary: Optional[str] = None,
    content_summary: Optional[str] = None,
    categories: Optional[List[PromptCategory]] = None
) -> str:
    """Build the user prompt with content and optional analyses."""

    parts = []

    # Header
    parts.append("# SOURCE CONTENT FOR PROMPT GENERATION\n")

    # Metadata
    if video_title:
        parts.append(f"**Title:** {video_title}")
    if video_author:
        parts.append(f"**Author:** {video_author}")
    parts.append("")

    # Optional analyses for enrichment
    if discovery_summary:
        parts.append("## DISCOVERY ANALYSIS (Key Insights)")
        parts.append(discovery_summary)
        parts.append("")

    if content_summary:
        parts.append("## CONTENT SUMMARY")
        parts.append(content_summary)
        parts.append("")

    # Main transcript
    parts.append("## FULL TRANSCRIPT/CONTENT")
    parts.append("---")
    parts.append(transcript)
    parts.append("---")
    parts.append("")

    # Category filter if specified
    if categories:
        category_names = [CATEGORY_INFO[c]["name"] for c in categories]
        parts.append(f"## CATEGORIES TO GENERATE")
        parts.append(f"Only generate prompts for: {', '.join(category_names)}")
        parts.append("")
    else:
        parts.append("Generate prompts for ALL 7 categories.")

    parts.append("")
    parts.append("Analyze this content and generate production-ready prompts. Return valid JSON.")

    return "\n".join(parts)
