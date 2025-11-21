"""OpenAI transcript cleaning service"""
from typing import Dict
from openai import OpenAI, OpenAIError, RateLimitError, AuthenticationError
from app.config import settings


class OpenAIService:
    """Service for cleaning transcripts using GPT-4o-mini"""
    
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
