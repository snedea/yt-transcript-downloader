"""OpenAI transcript cleaning and rhetorical analysis service"""
import json
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI, OpenAIError, RateLimitError, AuthenticationError
from app.config import settings
from app.data.rhetorical_toolkit import get_toolkit_summary, RHETORICAL_TECHNIQUES, RHETORICAL_PILLARS

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for cleaning transcripts and rhetorical analysis using OpenAI"""

    # JSON schema for rhetorical analysis response
    RHETORIC_ANALYSIS_SCHEMA = {
        "type": "object",
        "properties": {
            "overall_score": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100,
                "description": "Overall rhetorical effectiveness score"
            },
            "pillar_scores": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "pillar": {"type": "string", "enum": ["logos", "pathos", "ethos", "kairos"]},
                        "score": {"type": "integer", "minimum": 0, "maximum": 100},
                        "explanation": {"type": "string"},
                        "contributing_techniques": {"type": "array", "items": {"type": "string"}},
                        "key_examples": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["pillar", "score", "explanation"]
                }
            },
            "technique_matches": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "technique_id": {"type": "string"},
                        "technique_name": {"type": "string"},
                        "category": {"type": "string"},
                        "phrase": {"type": "string"},
                        "explanation": {"type": "string"},
                        "strength": {"type": "string", "enum": ["strong", "moderate", "subtle"]}
                    },
                    "required": ["technique_id", "technique_name", "phrase", "explanation", "strength"]
                }
            },
            "potential_quotes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "phrase": {"type": "string"},
                        "likely_source": {"type": "string"},
                        "source_type": {"type": "string", "enum": ["religious", "political", "literary", "philosophical", "scientific", "unknown"]},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                    },
                    "required": ["phrase", "confidence"]
                }
            },
            "executive_summary": {"type": "string"},
            "strengths": {"type": "array", "items": {"type": "string"}},
            "areas_for_improvement": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["overall_score", "pillar_scores", "technique_matches", "executive_summary"]
    }
    
    def __init__(self):
        """Initialize OpenAI client"""
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
    
    async def clean_transcript(self, transcript: str) -> Dict:
        """
        Clean and format transcript using GPT-4o-mini
        
        Args:
            transcript: Raw transcript text
            
        Returns:
            Dictionary with cleaned transcript and token usage
            Format: {
                "success": bool,
                "cleaned_transcript": str (if success),
                "tokens_used": int (if success),
                "error": str (if failure)
            }
        """
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI API key not configured"
            }
        
        try:
            # System prompt for transcript cleaning
            system_prompt = (
                "You are a transcript formatter. Clean up YouTube auto-generated "
                "transcripts by adding proper punctuation, paragraphs, and removing "
                "repetitive filler words. Maintain the original meaning and content. "
                "Do not add any commentary or analysis - just format the transcript."
            )
            
            # Call GPT-4o-mini
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Clean this transcript:\n\n{transcript}"}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            cleaned_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return {
                "success": True,
                "cleaned_transcript": cleaned_text,
                "tokens_used": tokens_used
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
            return {
                "success": False,
                "error": f"OpenAI API error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

    async def analyze_rhetoric(
        self,
        transcript: str,
        video_title: Optional[str] = None,
        video_author: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a transcript for rhetorical techniques using GPT-4.

        Args:
            transcript: The transcript text to analyze
            video_title: Optional title for context
            video_author: Optional author/speaker for context

        Returns:
            Dictionary with analysis results or error
        """
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI API key not configured"
            }

        # Get the toolkit summary for the prompt
        toolkit_reference = get_toolkit_summary()

        # Build context string
        context_info = ""
        if video_title:
            context_info += f"Video Title: {video_title}\n"
        if video_author:
            context_info += f"Speaker/Author: {video_author}\n"

        # System prompt for rhetorical analysis
        system_prompt = f"""You are an expert rhetorician and communication analyst, trained in classical rhetoric from Aristotle, Cicero, and the Rhetorica ad Herennium.

Your task is to analyze a transcript for rhetorical techniques and provide a comprehensive evaluation.

{toolkit_reference}

## Analysis Guidelines

1. **Identify Rhetorical Techniques**: Find ALL instances of the techniques listed above. For each:
   - Quote the EXACT phrase from the transcript
   - Identify which technique it represents (use the technique_id like "anaphora", "chiasmus", etc.)
   - Explain WHY this qualifies as that technique
   - Rate the strength: "strong" (textbook example), "moderate" (clear instance), or "subtle" (arguable)

2. **Score the Four Pillars** (0-100 each):
   - **Logos**: How well does the speaker use logic, evidence, and reasoning?
   - **Pathos**: How effectively does the speaker appeal to emotions?
   - **Ethos**: How well does the speaker establish credibility and trust?
   - **Kairos**: How well does the speaker leverage timing and context?

3. **Identify Potential Quotes**: Flag phrases that appear to be:
   - Biblical or religious quotes
   - Famous political speeches
   - Literary references
   - Philosophical quotes
   - Any phrase that sounds like it's from another source

4. **Calculate Overall Score**: Weight the pillars and technique usage to give an overall effectiveness score (0-100).

5. **Provide Executive Summary**: Write a 2-3 paragraph professional assessment of the speaker's rhetorical effectiveness.

Be thorough but accurate. Only identify techniques you're confident about. It's better to miss a subtle instance than to incorrectly flag something.

CRITICAL: Every "phrase" you report MUST be an EXACT quote from the transcript provided below. Do NOT use generic examples or famous quotes unless they actually appear in the transcript. If you cannot find a clear example of a technique in the actual transcript, do not report that technique."""

        user_prompt = f"""{context_info}
## Transcript to Analyze:

{transcript}

Analyze this transcript for rhetorical techniques. Return your analysis as JSON matching the required schema."""

        try:
            # Use GPT-4 for better analysis quality
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use GPT-4o for best quality
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=8000,
                response_format={"type": "json_object"}
            )

            # Parse the JSON response
            analysis_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            try:
                analysis_data = json.loads(analysis_text)
                # Debug logging to understand GPT response structure
                print(f"=== GPT RESPONSE DEBUG ===")
                print(f"GPT response type: {type(analysis_data)}")
                if isinstance(analysis_data, dict):
                    print(f"ALL keys in GPT response: {list(analysis_data.keys())}")
                    for key, val in analysis_data.items():
                        if isinstance(val, list):
                            print(f"  {key}: list with {len(val)} items")
                            if val and len(val) > 0:
                                print(f"    First item type: {type(val[0])}")
                                print(f"    First item preview: {str(val[0])[:200]}")
                        elif isinstance(val, dict):
                            print(f"  {key}: dict with keys {list(val.keys())[:5]}")
                        elif isinstance(val, (int, float)):
                            print(f"  {key}: {val}")
                        elif isinstance(val, str):
                            print(f"  {key}: str ({len(val)} chars)")
                        else:
                            print(f"  {key}: {type(val)}")
                else:
                    print(f"Unexpected response type: {analysis_data}")
                print(f"=== END DEBUG ===")

                # Normalize GPT response keys to our expected format
                # GPT sometimes uses different key names - be comprehensive
                key_mappings = {
                    # Technique variations
                    'techniques': 'technique_matches',
                    'rhetorical_techniques': 'technique_matches',
                    'technique_analysis': 'technique_matches',
                    'identified_techniques': 'technique_matches',
                    'found_techniques': 'technique_matches',
                    'techniques_found': 'technique_matches',
                    'techniques_identified': 'technique_matches',
                    # Pillar variations
                    'four_pillars_scores': 'pillar_scores',
                    'four_pillars': 'pillar_scores',
                    'pillars': 'pillar_scores',
                    'pillar_analysis': 'pillar_scores',
                    'pillar_breakdown': 'pillar_scores',
                    # Quote variations
                    'quotes': 'potential_quotes',
                    'identified_quotes': 'potential_quotes',
                    'quotes_found': 'potential_quotes',
                    'quote_analysis': 'potential_quotes',
                }
                for old_key, new_key in key_mappings.items():
                    if old_key in analysis_data and new_key not in analysis_data:
                        analysis_data[new_key] = analysis_data[old_key]
                        print(f"  Mapped {old_key} -> {new_key}")

                # Also check for nested structures - GPT sometimes wraps data
                if 'analysis' in analysis_data and isinstance(analysis_data['analysis'], dict):
                    print(f"  Found nested 'analysis' key, flattening")
                    for key, value in analysis_data['analysis'].items():
                        if key not in analysis_data:
                            analysis_data[key] = value

                # Fallback: search for any key containing 'technique' if we don't have technique_matches
                if 'technique_matches' not in analysis_data or not analysis_data.get('technique_matches'):
                    for key in list(analysis_data.keys()):
                        if 'technique' in key.lower() and isinstance(analysis_data[key], list) and len(analysis_data[key]) > 0:
                            print(f"  Fallback: Found techniques in '{key}' with {len(analysis_data[key])} items")
                            analysis_data['technique_matches'] = analysis_data[key]
                            break

                # Debug: show what we have after mapping
                print(f"=== AFTER KEY MAPPING ===")
                for key in ['pillar_scores', 'technique_matches', 'potential_quotes']:
                    val = analysis_data.get(key)
                    print(f"  {key}: {type(val).__name__}, len={len(val) if val and hasattr(val, '__len__') else 'N/A'}")
                    if val and isinstance(val, (list, dict)) and len(val) > 0:
                        if isinstance(val, dict):
                            print(f"    Dict keys: {list(val.keys())[:5]}")
                        elif isinstance(val, list):
                            print(f"    First item: {str(val[0])[:200]}")
                print(f"=== END AFTER MAPPING ===")

                # Normalize potential_quotes - fix field names and source_type values
                if 'potential_quotes' in analysis_data and analysis_data['potential_quotes']:
                    normalized_quotes = []
                    for q in analysis_data['potential_quotes']:
                        # Handle string quotes - convert to dict format
                        if isinstance(q, str):
                            q = {
                                'phrase': q,
                                'confidence': 0.7,
                                'source_type': 'unknown'
                            }
                        if isinstance(q, dict):
                            # Map 'quote' to 'phrase'
                            if 'quote' in q and 'phrase' not in q:
                                q['phrase'] = q['quote']
                            # Normalize source_type to allowed values
                            st = q.get('source_type', 'unknown')
                            if st:
                                st_lower = st.lower()
                                if 'religious' in st_lower or 'bible' in st_lower or 'biblical' in st_lower:
                                    q['source_type'] = 'religious'
                                elif 'political' in st_lower or 'speech' in st_lower:
                                    q['source_type'] = 'political'
                                elif 'literary' in st_lower or 'book' in st_lower or 'novel' in st_lower:
                                    q['source_type'] = 'literary'
                                elif 'philosoph' in st_lower:
                                    q['source_type'] = 'philosophical'
                                elif 'scien' in st_lower:
                                    q['source_type'] = 'scientific'
                                else:
                                    q['source_type'] = 'unknown'
                            # Ensure confidence exists
                            if 'confidence' not in q:
                                q['confidence'] = 0.7
                            normalized_quotes.append(q)
                    analysis_data['potential_quotes'] = normalized_quotes

                # Normalize technique_matches - ensure required fields
                if 'technique_matches' in analysis_data and analysis_data['technique_matches']:
                    normalized_techniques = []
                    for t in analysis_data['technique_matches']:
                        if isinstance(t, dict):
                            # Map common field name variations for phrase
                            if 'quote' in t and 'phrase' not in t:
                                t['phrase'] = t['quote']
                            if 'text' in t and 'phrase' not in t:
                                t['phrase'] = t['text']
                            if 'example' in t and 'phrase' not in t:
                                t['phrase'] = t['example']

                            # Map common field name variations for technique name/id
                            if 'technique' in t and 'technique_name' not in t:
                                t['technique_name'] = t['technique']
                            if 'name' in t and 'technique_name' not in t:
                                t['technique_name'] = t['name']
                            if 'type' in t and 'technique_name' not in t:
                                t['technique_name'] = t['type']
                            if 'rhetorical_technique' in t and 'technique_name' not in t:
                                t['technique_name'] = t['rhetorical_technique']

                            if 'id' in t and 'technique_id' not in t:
                                t['technique_id'] = t['id']
                            if 'technique_name' in t and 'technique_id' not in t:
                                t['technique_id'] = t['technique_name'].lower().replace(' ', '_')

                            # Map explanation variations
                            if 'analysis' in t and 'explanation' not in t:
                                t['explanation'] = t['analysis']
                            if 'description' in t and 'explanation' not in t:
                                t['explanation'] = t['description']
                            if 'reason' in t and 'explanation' not in t:
                                t['explanation'] = t['reason']

                            # Map strength variations
                            if 'impact' in t and 'strength' not in t:
                                t['strength'] = t['impact']
                            if 'effectiveness' in t and 'strength' not in t:
                                # Map effectiveness descriptions to strength
                                eff = str(t['effectiveness']).lower()
                                if 'high' in eff or 'strong' in eff:
                                    t['strength'] = 'strong'
                                elif 'low' in eff or 'subtle' in eff or 'weak' in eff:
                                    t['strength'] = 'subtle'
                                else:
                                    t['strength'] = 'moderate'

                            # Ensure required fields have defaults
                            t.setdefault('technique_id', 'unknown')
                            t.setdefault('technique_name', t.get('technique_id', 'Unknown Technique').replace('_', ' ').title())
                            t.setdefault('phrase', '')
                            t.setdefault('explanation', '')
                            t.setdefault('strength', 'moderate')

                            # Look up category from toolkit BEFORE setting default
                            tech_id = t.get('technique_id', '').lower().replace(' ', '_')
                            if tech_id in RHETORICAL_TECHNIQUES and not t.get('category'):
                                t['category'] = RHETORICAL_TECHNIQUES[tech_id].get('category', 'other')
                            else:
                                t.setdefault('category', 'other')

                            # Debug: log what we have for this technique
                            print(f"  Normalized technique: id={t.get('technique_id')}, name={t.get('technique_name')}, phrase={t.get('phrase', '')[:50]}...")

                            normalized_techniques.append(t)
                    analysis_data['technique_matches'] = normalized_techniques

                # Normalize pillar_scores - handle both list and dict formats
                if 'pillar_scores' in analysis_data and analysis_data['pillar_scores']:
                    pillar_data = analysis_data['pillar_scores']

                    # Convert dict format to list format if needed
                    # e.g., {"logos": {"score": 80, ...}, "pathos": {...}} -> [{"pillar": "logos", "score": 80}, ...]
                    if isinstance(pillar_data, dict):
                        print(f"  Converting pillar_scores from dict to list format")
                        # Debug: show first pillar's full structure
                        first_pillar = list(pillar_data.keys())[0] if pillar_data else None
                        if first_pillar:
                            print(f"  Sample pillar '{first_pillar}' structure: {pillar_data[first_pillar]}")
                        new_pillar_list = []
                        for pillar_name, pillar_info in pillar_data.items():
                            if isinstance(pillar_info, dict):
                                pillar_info['pillar'] = pillar_name.lower()
                                new_pillar_list.append(pillar_info)
                            elif isinstance(pillar_info, (int, float)):
                                # Simple format: {"logos": 80, "pathos": 75}
                                new_pillar_list.append({
                                    'pillar': pillar_name.lower(),
                                    'score': int(pillar_info),
                                    'explanation': ''
                                })
                        pillar_data = new_pillar_list
                        analysis_data['pillar_scores'] = pillar_data

                    normalized_pillars = []
                    for p in pillar_data:
                        if isinstance(p, dict):
                            # Map common field name variations
                            if 'name' in p and 'pillar' not in p:
                                p['pillar'] = p['name'].lower()
                            if 'pillar_name' in p and 'pillar' not in p:
                                p['pillar'] = p['pillar_name'].lower().split()[0]
                            # Normalize pillar name to expected values
                            pillar_val = p.get('pillar', '').lower()
                            if 'logo' in pillar_val:
                                p['pillar'] = 'logos'
                            elif 'patho' in pillar_val:
                                p['pillar'] = 'pathos'
                            elif 'etho' in pillar_val:
                                p['pillar'] = 'ethos'
                            elif 'kairo' in pillar_val:
                                p['pillar'] = 'kairos'
                            p.setdefault('score', 0)
                            p.setdefault('explanation', '')
                            normalized_pillars.append(p)
                    analysis_data['pillar_scores'] = normalized_pillars

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse GPT response as JSON: {e}")
                return {
                    "success": False,
                    "error": f"Failed to parse analysis response: {str(e)}"
                }

            # Add pillar names to scores
            pillar_names = {
                "logos": "Logos (Reason)",
                "pathos": "Pathos (Emotion)",
                "ethos": "Ethos (Credibility)",
                "kairos": "Kairos (Timing)"
            }

            for pillar_score in analysis_data.get("pillar_scores", []):
                # Skip non-dict items
                if not isinstance(pillar_score, dict):
                    continue
                pillar_id = pillar_score.get("pillar", "")
                pillar_score["pillar_name"] = pillar_names.get(pillar_id, pillar_id.title())

            # Add category to technique matches if missing or set to 'other'
            for match in analysis_data.get("technique_matches", []):
                # Skip non-dict items
                if not isinstance(match, dict):
                    continue
                tech_id = match.get("technique_id", "").lower().replace(' ', '_')
                current_cat = match.get("category", "")
                # Update category from toolkit if missing or defaulted to 'other'
                if tech_id in RHETORICAL_TECHNIQUES and (not current_cat or current_cat == "other"):
                    match["category"] = RHETORICAL_TECHNIQUES[tech_id].get("category", "other")

            return {
                "success": True,
                "analysis": analysis_data,
                "tokens_used": tokens_used
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
            logger.error(f"OpenAI API error during rhetoric analysis: {e}")
            return {
                "success": False,
                "error": f"OpenAI API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error during rhetoric analysis: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

    def is_available(self) -> bool:
        """Check if the OpenAI service is configured and available."""
        return self.client is not None
