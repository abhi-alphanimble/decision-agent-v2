"""AI Client for generating decision summaries using Google Gemini API.
Provides a test-mode mock when running under pytest to avoid external calls
and make unit tests deterministic.
"""
from typing import Optional, Dict, Any
import os
try:
    import google.generativeai as genai
except Exception:
    genai = None
from app.config import config
from app.models import Decision, Vote
from app.config import get_context_logger

logger = get_context_logger(__name__)


def _is_test_mode() -> bool:
    return bool(os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING"))


class AIClient:
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        self.model = None
        self.initialized = False

        if not genai:
            logger.warning("⚠️ google.generativeai SDK not available")
            return

        if self.api_key:
            try:
                configure_func = getattr(genai, 'configure', None)
                if configure_func:
                    configure_func(api_key=self.api_key)
                else:
                    logger.warning("⚠️ configure function not available in google.generativeai")
                    return
                
                GenerativeModel = getattr(genai, 'GenerativeModel', None)
                if GenerativeModel:
                    self.model = GenerativeModel('gemini-2.5-flash')
                else:
                    logger.warning("⚠️ GenerativeModel not available in google.generativeai")
                    return

                if self.model:
                    logger.info("✅ AI Client initialized with Gemini 2.5 Flash")
                    self.initialized = True
                else:
                    logger.warning("⚠️ AI Client initialized but model object is unexpected")
                    self.initialized = False
            except Exception as e:
                logger.error(f"❌ Failed to initialize AI Client: {e}", exc_info=True)
        else:
            logger.warning("⚠️ GEMINI_API_KEY not found in config")

    def summarize_decision(self, decision: Decision, votes: list[Vote]) -> Optional[str]:
        if not self.model:
            logger.error("❌ AI model not initialized")
            return None
        try:
            # Build context from decision and votes
            votes_summary = "\n".join([
                f"- {v.voter_name}: {v.vote_type.upper()} {('(anonymous)' if v.is_anonymous else '')}"
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
            
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text
            return "Unable to generate summary"
        except Exception as e:
            logger.error(f"Error during AI summarization: {e}", exc_info=True)
            return None

    def suggest_next_steps(self, decision: Decision, votes: list[Vote]) -> Optional[str]:
        if not self.model:
            logger.error("❌ AI model not initialized")
            return None
        try:
            # Build context from decision and votes
            votes_summary = "\n".join([
                f"- {v.voter_name}: {v.vote_type.upper()} {('(anonymous)' if v.is_anonymous else '')}"
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
            
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text
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
