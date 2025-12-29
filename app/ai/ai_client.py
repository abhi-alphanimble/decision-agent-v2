"""AI Client for generating decision summaries using litellm (OpenRouter).
Provides a test-mode mock when running under pytest to avoid external calls
and make unit tests deterministic.
"""
from typing import Optional, Dict, Any
import os
try:
    import litellm
except Exception:
    litellm = None
from app.config import config
from app.models import Decision, Vote
from app.config import get_context_logger

logger = get_context_logger(__name__)


def _is_test_mode() -> bool:
    return bool(os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING"))


class AIClient:
    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY
        self.model = "openrouter/google/gemini-2.5-flash-lite"  # Updated to valid OpenRouter model
        self.initialized = False
        self.init_error = None  # Track initialization error for better diagnostics

        if not litellm:
            self.init_error = "litellm library not installed"
            logger.warning("⚠️ litellm SDK not available - AI features will be disabled")
            logger.info("💡 Install with: pip install litellm")
            return

        if not self.api_key:
            self.init_error = "OPENROUTER_API_KEY not configured"
            logger.warning("⚠️ OPENROUTER_API_KEY not found in environment variables")
            logger.info("💡 Set OPENROUTER_API_KEY in your .env file to enable AI features")
            return

        try:
            # For OpenRouter, set the API key in environment (LiteLLM convention)
            import os
            os.environ["OPENROUTER_API_KEY"] = self.api_key
            
            # Skip synchronous test completion during initialization to avoid blocking startup/Slack 3s window.
            # We will assume configuration is correct if API key is present.
            self.initialized = True
            logger.info(f"✅ AI Client configured with model: {self.model}")
                
        except Exception as e:
            self.init_error = f"AI Client configuration failed: {str(e)}"
            logger.error(f"❌ Failed to configure AI Client: {e}", exc_info=True)

    def summarize_decision(self, decision: Decision, votes: list[Vote]) -> Optional[str]:
        if not self.initialized:
            error_msg = f"AI client not initialized: {self.init_error or 'unknown reason'}"
            logger.error(f"❌ {error_msg}")
            return None
        try:
            # Build context from decision and votes
            votes_summary = "\n".join([
                f"- {v.voter_name}: {v.vote_type.upper()}"
                for v in votes
            ]) if votes else "No votes yet"
            
            prompt = f"""Provide a brief AI summary of this decision:

Decision: {decision.text}

Status: {decision.status}
Approvals: {decision.approval_count}/{decision.group_size_at_creation}
Rejections: {decision.rejection_count}
Threshold: {decision.approval_threshold}

Votes:
{votes_summary}

Provide a 2-3 sentence summary of the decision and voting status."""
            
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                api_key=self.api_key  # Pass API key explicitly for OpenRouter
            )
            if response and response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            return "Unable to generate summary"
        except Exception as e:
            logger.error(f"Error during AI summarization: {e}", exc_info=True)
            return None

    def suggest_next_steps(self, decision: Decision, votes: list[Vote]) -> Optional[str]:
        if not self.initialized:
            error_msg = f"AI client not initialized: {self.init_error or 'unknown reason'}"
            logger.error(f"❌ {error_msg}")
            return None
        try:
            # Build context from decision and votes
            votes_summary = "\n".join([
                f"- {v.voter_name}: {v.vote_type.upper()}"
                for v in votes
            ]) if votes else "No votes yet"
            
            prompt = f"""Suggest next steps for this decision:

Decision: {decision.text}

Status: {decision.status}
Approvals: {decision.approval_count}/{decision.group_size_at_creation}
Rejections: {decision.rejection_count}
Threshold needed: {decision.approval_threshold}

Votes:
{votes_summary}

Based on the current voting status, provide 2-3 actionable suggestions for next steps."""
            
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                api_key=self.api_key  # Pass API key explicitly for OpenRouter
            )
            if response and response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            return "Unable to generate suggestions"
        except Exception as e:
            logger.error(f"Error during AI suggestions: {e}", exc_info=True)
            return None


class MockAIClient:
    def summarize_decision(self, decision: Decision, votes: list[Vote]) -> Optional[str]:
        return "🤖 AI Summary (test mode)"

    def suggest_next_steps(self, decision: Decision, votes: list[Vote]) -> Optional[str]:
        return "🤖 AI Suggestions (test mode)"


# Global instance: use mock in tests to avoid external calls
if _is_test_mode():
    ai_client = MockAIClient()
else:
    ai_client = AIClient()
