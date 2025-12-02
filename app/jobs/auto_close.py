"""
Auto-close stale decisions background job

This module handles automatically closing pending decisions that have exceeded
the timeout period (default 48 hours) based on their vote counts.
"""
import logging
from datetime import datetime, UTC, timedelta
from typing import List
from sqlalchemy.orm import Session

from app.config import config
from app.models import Decision, ChannelConfig
from app.slack_client import slack_client
from app.utils import get_utc_now
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
        
        # Get all pending decisions
        all_pending = db.query(Decision).filter(Decision.status == "pending").all()
        
        if not all_pending:
            logger.info("✅ No pending decisions found")
            return
        
        # Build dict of channel_id -> auto_close_hours
        channel_configs = {}
        for decision in all_pending:
            if decision.channel_id not in channel_configs:
                config_obj = db.query(ChannelConfig).filter(
                    ChannelConfig.channel_id == decision.channel_id
                ).first()
                # Use channel config or global default
                timeout = config_obj.auto_close_hours if config_obj else config.DECISION_TIMEOUT_HOURS
                channel_configs[decision.channel_id] = timeout
        
        # Filter to only stale decisions (using per-channel timeout)
        stale_decisions = []
        for decision in all_pending:
            timeout_hours = channel_configs.get(decision.channel_id, config.DECISION_TIMEOUT_HOURS)
            cutoff_time = get_utc_now() - timedelta(hours=timeout_hours)
            if decision.created_at < cutoff_time:
                stale_decisions.append(decision)
        
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
                decision.closed_at = get_utc_now()
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


def determine_final_status(decision: Decision) -> str:
    """
    Determine the final status of a decision based on vote counts.
    
    Logic:
    - If approvals > rejections → "approved"
    - If rejections > approvals → "rejected"
    - If tied → "rejected" (conservative: treat tie as rejection)
    
    Args:
        decision: Decision object
        
    Returns:
        Final status string
    """
    if decision.approval_count > decision.rejection_count:
        return "approved"
    else:
        # Tied or more rejections → rejected (conservative default)
        return "rejected"


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
            reason = "did not receive enough approvals (tied or more rejections)"
        
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
        
        # Get channel-specific timeout for accurate message
        db = SessionLocal()
        try:
            config_obj = db.query(ChannelConfig).filter(
                ChannelConfig.channel_id == decision.channel_id
            ).first()
            timeout_hours = config_obj.auto_close_hours if config_obj else config.DECISION_TIMEOUT_HOURS
        finally:
            db.close()
        
        # Format notification message with channel-specific timeout
        message = (
            f"{emoji} *Decision #{decision.id} Auto-Closed: {result}*\n\n"
            f"*Proposal:* {decision.text}\n\n"
            f"*Final Vote Count:*\n"
            f"👍 Approvals: {decision.approval_count}\n"
            f"👎 Rejections: {decision.rejection_count}\n\n"
            f"*Reason:* This decision {reason} after {timeout_hours} hours of pending.\n"
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
