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
        self.api_key = config.OPEN_ROUTER_API_KEY
        self.model = "openrouter/google/gemini-2.5-flash-lite"
        self.initialized = False

        if not litellm:
            logger.warning("⚠️ litellm SDK not available")
            return

        if self.api_key:
            try:
                litellm.api_key = self.api_key
                logger.info("✅ AI Client initialized with OpenRouter")
                self.initialized = True
            except Exception as e:
                logger.error(f"❌ Failed to initialize AI Client: {e}", exc_info=True)
        else:
            logger.warning("⚠️ OPEN_ROUTER_API_KEY not found in config")

    def summarize_decision(self, decision: Decision, votes: list[Vote]) -> Optional[str]:
        if not self.initialized:
            logger.error("❌ AI client not initialized")
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
                messages=[{"role": "user", "content": prompt}]
            )
            if response and response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            return "Unable to generate summary"
        except Exception as e:
            logger.error(f"Error during AI summarization: {e}", exc_info=True)
            return None

    def suggest_next_steps(self, decision: Decision, votes: list[Vote]) -> Optional[str]:
        if not self.initialized:
            logger.error("❌ AI client not initialized")
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
                messages=[{"role": "user", "content": prompt}]
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
