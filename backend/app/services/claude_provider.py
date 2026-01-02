"""
Local Claude Provider

Uses Claude Code CLI as a subprocess to leverage existing Claude subscription.
Inspired by Context Foundry's delegation pattern.
"""

import json
import logging
import shutil
import subprocess
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class LocalClaudeProvider:
    """
    Provider that uses the Claude Code CLI for LLM calls.

    This leverages your existing Claude subscription - no API key needed.
    The CLI must be installed and authenticated (via ~/.claude credentials).
    """

    def __init__(self):
        """Initialize the provider and check for claude CLI."""
        self.claude_path = shutil.which("claude")
        if not self.claude_path:
            logger.warning("Claude CLI not found in PATH. Install with: npm install -g @anthropic-ai/claude-code")

    def is_available(self) -> bool:
        """Check if Claude CLI is available and authenticated."""
        if not self.claude_path:
            return False

        try:
            # Quick check - just see if claude responds
            result = subprocess.run(
                [self.claude_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking Claude CLI: {e}")
            return False

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "claude-opus-4-5-20251101",
        max_tokens: int = 8000,
        temperature: float = 0.4,
        response_format: Optional[str] = "json"
    ) -> Dict[str, Any]:
        """
        Generate a response using Claude CLI.

        Args:
            system_prompt: System instructions for Claude
            user_prompt: The user's prompt/question
            model: Model to use (default: claude-opus-4-5-20251101)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            response_format: "json" for JSON output, None for text

        Returns:
            Dict with 'success', 'content', 'error', and 'tokens_used' keys
        """
        if not self.claude_path:
            return {
                "success": False,
                "content": None,
                "error": "Claude CLI not found. Install with: npm install -g @anthropic-ai/claude-code",
                "tokens_used": 0
            }

        # Build the command
        cmd = [
            self.claude_path,
            "--print",  # Non-interactive mode
            "--permission-mode", "bypassPermissions",  # Skip permission dialogs
            "--strict-mcp-config",  # Don't load MCP servers
            "--model", model,
            "--max-turns", "1",  # Single turn
        ]

        # Add system prompt
        if system_prompt:
            cmd.extend(["--system-prompt", system_prompt])

        # For JSON output, add instruction to the prompt
        full_prompt = user_prompt
        if response_format == "json":
            full_prompt = f"{user_prompt}\n\nIMPORTANT: Respond with valid JSON only. No markdown code blocks, no explanations outside the JSON."

        try:
            logger.info(f"Calling Claude CLI with model {model}")

            result = subprocess.run(
                cmd,
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                env=None  # Use current environment
            )

            if result.returncode != 0:
                error_msg = result.stderr or f"Claude CLI exited with code {result.returncode}"
                logger.error(f"Claude CLI error: {error_msg}")
                return {
                    "success": False,
                    "content": None,
                    "error": error_msg,
                    "tokens_used": 0
                }

            output = result.stdout.strip()

            # Try to extract JSON if response_format is json
            if response_format == "json":
                # Sometimes Claude wraps JSON in markdown code blocks
                if output.startswith("```json"):
                    output = output[7:]
                if output.startswith("```"):
                    output = output[3:]
                if output.endswith("```"):
                    output = output[:-3]
                output = output.strip()

                # Validate it's valid JSON
                try:
                    json.loads(output)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON response: {e}")
                    return {
                        "success": False,
                        "content": output,
                        "error": f"Invalid JSON response: {e}",
                        "tokens_used": 0
                    }

            # Estimate tokens (rough approximation)
            tokens_used = len(full_prompt.split()) * 1.3 + len(output.split()) * 1.3

            return {
                "success": True,
                "content": output,
                "error": None,
                "tokens_used": int(tokens_used)
            }

        except subprocess.TimeoutExpired:
            logger.error("Claude CLI timed out")
            return {
                "success": False,
                "content": None,
                "error": "Claude CLI timed out after 5 minutes",
                "tokens_used": 0
            }
        except Exception as e:
            logger.error(f"Error calling Claude CLI: {e}")
            return {
                "success": False,
                "content": None,
                "error": str(e),
                "tokens_used": 0
            }


# Singleton instance
_claude_provider: Optional[LocalClaudeProvider] = None


def get_claude_provider() -> LocalClaudeProvider:
    """Get or create the Claude provider singleton."""
    global _claude_provider
    if _claude_provider is None:
        _claude_provider = LocalClaudeProvider()
    return _claude_provider
