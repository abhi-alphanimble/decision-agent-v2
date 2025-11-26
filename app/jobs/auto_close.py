"""
Auto-close stale decisions background job

This module handles automatically closing pending decisions that have exceeded
the timeout period (default 48 hours) based on their vote counts.
"""
import logging
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session

from app.config import config
from app.models import Decision
from app.slack_client import slack_client
from database.base import SessionLocal

logger = logging.getLogger(__name__)


def check_stale_decisions():
    """
    Main background job function that checks for and closes stale decisions.
    
    This function:
    1. Queries pending decisions older than the timeout period
    2. Determines final status based on vote counts
    3. Updates decision status and closed_at timestamp
    4. Sends Slack notifications to channels
    5. Logs all actions
    
    Runs every hour via APScheduler.
    """
    db = SessionLocal()
    
    try:
        logger.info("🔍 Starting auto-close job for stale decisions...")
        
        # Calculate cutoff time
        cutoff_time = datetime.utcnow() - timedelta(hours=config.DECISION_TIMEOUT_HOURS)
        
        # Query stale decisions
        stale_decisions = get_stale_decisions(db, cutoff_time)
        
        if not stale_decisions:
            logger.info("✅ No stale decisions found")
            return
        
        logger.info(f"📋 Found {len(stale_decisions)} stale decision(s) to process")
        
        # Process each stale decision
        closed_count = 0
        for decision in stale_decisions:
            try:
                # Determine final status based on votes
                final_status = determine_final_status(decision)
                
                # Update decision
                decision.status = final_status
                decision.closed_at = datetime.utcnow()
                db.commit()
                
                logger.info(
                    f"✅ Auto-closed decision #{decision.id} with status '{final_status}' "
                    f"(👍 {decision.approval_count} vs 👎 {decision.rejection_count})"
                )
                
                # Send Slack notification
                send_auto_close_notification(decision)
                
                closed_count += 1
                
            except Exception as e:
                logger.error(f"❌ Error closing decision #{decision.id}: {e}", exc_info=True)
                db.rollback()
                continue
        
        logger.info(f"🎉 Auto-close job completed. Closed {closed_count}/{len(stale_decisions)} decision(s)")
        
    except Exception as e:
        logger.error(f"❌ Error in auto-close job: {e}", exc_info=True)
        db.rollback()
        
    finally:
        db.close()


def get_stale_decisions(db: Session, cutoff_time: datetime) -> List[Decision]:
    """
    Query pending decisions older than the cutoff time.
    
    Args:
        db: Database session
        cutoff_time: Decisions created before this time are considered stale
        
    Returns:
        List of stale Decision objects
    """
    return db.query(Decision).filter(
        Decision.status == "pending",
        Decision.created_at < cutoff_time
    ).all()


def determine_final_status(decision: Decision) -> str:
    """
    Determine the final status of a decision based on vote counts.
    
    Logic:
    - If approvals > rejections → "approved"
    - If rejections > approvals → "rejected"
    - If tied → "expired_no_consensus"
    
    Args:
        decision: Decision object
        
    Returns:
        Final status string
    """
    if decision.approval_count > decision.rejection_count:
        return "approved"
    elif decision.rejection_count > decision.approval_count:
        return "rejected"
    else:
        return "expired_no_consensus"


def send_auto_close_notification(decision: Decision):
    """
    Send Slack notification to channel about auto-closed decision.
    
    Args:
        decision: The closed Decision object
    """
    try:
        # Determine emoji and message based on status
        if decision.status == "approved":
            emoji = "✅"
            result = "APPROVED"
            reason = "received more approvals than rejections"
        elif decision.status == "rejected":
            emoji = "❌"
            result = "REJECTED"
            reason = "received more rejections than approvals"
        else:  # expired_no_consensus
            emoji = "⏰"
            result = "EXPIRED (No Consensus)"
            reason = "had tied votes"
        
        # Format notification message
        message = (
            f"{emoji} *Decision #{decision.id} Auto-Closed: {result}*\n\n"
            f"*Proposal:* {decision.text}\n\n"
            f"*Final Vote Count:*\n"
            f"👍 Approvals: {decision.approval_count}\n"
            f"👎 Rejections: {decision.rejection_count}\n\n"
            f"*Reason:* This decision {reason} after {config.DECISION_TIMEOUT_HOURS} hours.\n"
            f"*Proposed by:* {decision.proposer_name}\n"
            f"*Closed at:* {decision.closed_at.strftime('%Y-%m-%d %H:%M UTC')}"
        )
        
        # Send to channel
        slack_client.send_message(
            channel=decision.channel_id,
            text=message
        )
        
        logger.info(f"📤 Sent auto-close notification for decision #{decision.id} to channel {decision.channel_id}")
        
    except Exception as e:
        logger.error(f"❌ Error sending notification for decision #{decision.id}: {e}", exc_info=True)
