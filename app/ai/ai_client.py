"""
AI Client for generating decision summaries using Google Gemini API.
"""
import logging
import google.generativeai as genai
from typing import Optional, Dict, Any
from app.config import config
from app.models import Decision, Vote

logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        self.model = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                logger.info("✅ AI Client initialized with Gemini 2.5 Flash")
            except Exception as e:
                logger.error(f"❌ Failed to initialize AI Client: {e}")
        else:
            logger.warning("⚠️ GEMINI_API_KEY not found in config")

    def summarize_decision(self, decision: Decision, votes: list[Vote]) -> Optional[str]:
        """
        Generate a summary for a decision using Gemini.
        """
        if not self.model:
            logger.error("❌ AI model not initialized")
            return None

        try:
            # Prepare data for prompt
            vote_counts = {"approve": 0, "reject": 0}
            anonymous_count = 0
            
            for vote in votes:
                if vote.vote_type in vote_counts:
                    vote_counts[vote.vote_type] += 1
                if vote.is_anonymous:
                    anonymous_count += 1
            
            total_votes = len(votes)
            approval_pct = (vote_counts["approve"] / total_votes * 100) if total_votes > 0 else 0
            
            # Construct prompt
            prompt = f"""
            Please summarize the following team decision in a clear, professional format for Slack.
            
            **Decision Context:**
            - ID: #{decision.id}
            - Proposal: "{decision.text}"
            - Proposer: {decision.proposer_name}
            - Status: {decision.status.upper()}
            - Date: {decision.created_at.strftime('%Y-%m-%d')}
            
            **Voting Results:**
            - Total Votes: {total_votes}
            - Approvals: {vote_counts['approve']} ({approval_pct:.1f}%)
            - Rejections: {vote_counts['reject']}
            - Anonymous Votes: {anonymous_count}
            - Approval Threshold: {decision.approval_threshold}
            
            **Instructions:**
            1. Start with a 1-sentence executive summary of the outcome.
            2. Provide a brief breakdown of the voting pattern.
            3. If there are anonymous votes, mention that privacy was respected.
            4. If the decision is closed, explain why (e.g., "Passed with majority support").
            5. Keep it concise (max 150 words) and use Slack formatting (bolding, emojis).
            6. Do NOT mention specific voter names unless they are the proposer.
            """
            
            # Generate content
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"❌ Error generating summary: {e}")
            return None

# Global instance
ai_client = AIClient()
