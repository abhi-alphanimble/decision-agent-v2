"""
Handlers for member-related Slack events
"""
from sqlalchemy.orm import Session
import logging
from typing import Dict, Any

from ..database import crud
from ..slack import slack_client

logger = logging.getLogger(__name__)


def handle_member_joined_channel(
    user_id: str,
    user_name: str,
    channel_id: str,
    db: Session
) -> None:
    """
    Handle member_joined_channel event.
    Sends welcome message to new member with list of pending decisions.
    
    Args:
        user_id: Slack user ID of the member who joined
        user_name: Display name of the member
        channel_id: Channel ID where member joined
        db: Database session
    """
    logger.info(f"👋 Member {user_name} ({user_id}) joined channel {channel_id}")
    
    try:
        # Note: group_size is no longer tracked in ChannelConfig
        # It will be fetched dynamically from Slack when decisions are proposed

        # Get pending decisions for this channel
        pending_decisions = crud.get_pending_decisions(db, channel_id=channel_id)
        
        # Format welcome message
        welcome_message = format_welcome_message(user_name, pending_decisions)
        
        # Send ephemeral message to the new member
        try:
            slack_client.send_ephemeral_message(
                channel=channel_id,
                user=user_id,
                text=welcome_message
            )
            logger.info(f"✅ Sent welcome message to {user_name} with {len(pending_decisions)} pending decisions")
        except Exception as e:
            logger.error(f"❌ Error sending welcome message to {user_name}: {e}")
            
    except Exception as e:
        logger.error(f"❌ Error handling member join for {user_name}: {e}", exc_info=True)


def format_welcome_message(user_name: str, pending_decisions: list) -> str:
    """
    Format welcome message for new channel member.
    
    Args:
        user_name: Display name of the new member
        pending_decisions: List of pending Decision objects
        
    Returns:
        Formatted welcome message string
    """
    message_parts = [
        f"👋 *Welcome to the channel, {user_name}!*\n",
        "I'm the Decision Agent bot. I help teams make decisions together.\n"
    ]
    
    if not pending_decisions:
        message_parts.append(
            "\n✨ There are currently no pending decisions in this channel.\n\n"
            "💡 *How to use me:*\n"
            "• `/decision propose \"Your decision text\"` - Propose a new decision\n"
            "• `/decision add \"Decision text\"` - Add a pre-approved decision\n"
            "• `/decision list` - View all decisions\n"
            "• `/decision help` - See all available commands"
        )
    else:
        message_parts.append(
            f"\n📋 *There {'is' if len(pending_decisions) == 1 else 'are'} "
            f"{len(pending_decisions)} pending decision{'s' if len(pending_decisions) != 1 else ''} "
            f"awaiting votes:*\n"
        )
        
        # List pending decisions
        for decision in pending_decisions[:5]:  # Show max 5
            votes_needed = decision.approval_threshold - decision.approval_count
            message_parts.append(
                f"\n*Decision #{decision.id}*\n"
                f"_{decision.text}_\n"
                f"👍 {decision.approval_count}/{decision.approval_threshold} approvals "
                f"({votes_needed} more needed)\n"
                f"👎 {decision.rejection_count} rejections\n"
                f"Proposed by: {decision.proposer_name}\n"
            )
        
        if len(pending_decisions) > 5:
            message_parts.append(f"\n_...and {len(pending_decisions) - 5} more_\n")
        
        message_parts.append(
            "\n💡 *You can vote on these decisions:*\n"
            "• `/decision approve <id>` - Vote to approve\n"
            "• `/decision reject <id>` - Vote to reject\n"
            "• `/decision show <id>` - View decision details\n"
            "• `/decision list pending` - See all pending decisions\n\n"
            "Use `/decision help` to see all available commands."
        )
    
    return "".join(message_parts)


def handle_member_left_channel(
    user_id: str,
    user_name: str,
    channel_id: str,
    db: Session
) -> None:
    """
    Handle member_left_channel event.
    Checks for unreachable pending decisions and closes them.
    
    Args:
        user_id: Slack user ID of the member who left
        user_name: Display name of the member
        channel_id: Channel ID where member left
        db: Database session
    """
    logger.info(f"👋 Member {user_name} ({user_id}) left channel {channel_id}")
    
    try:
        # Get current channel member count from Slack
        try:
            current_member_count = slack_client.get_channel_members_count(channel_id)
            logger.info(f"📊 Current channel human member count: {current_member_count}")
            # Note: group_size is no longer stored in ChannelConfig
            # It will be fetched dynamically when decisions are proposed
        except Exception as e:
            logger.error(f"❌ Error getting channel members count: {e}")
            # Can't proceed without member count
            return
        
        # Get all pending decisions for this channel
        pending_decisions = crud.get_pending_decisions(db, channel_id=channel_id)
        
        if not pending_decisions:
            logger.info(f"ℹ️ No pending decisions in channel {channel_id}")
            return
        
        # Find unreachable decisions
        unreachable_decisions = []
        for decision in pending_decisions:
            if decision.approval_threshold > current_member_count:
                unreachable_decisions.append(decision)
                logger.info(
                    f"🚫 Decision #{decision.id} is unreachable: "
                    f"needs {decision.approval_threshold} approvals but only {current_member_count} members"
                )
        
        if not unreachable_decisions:
            logger.info(f"✅ All pending decisions are still reachable")
            return
        
        # Close unreachable decisions
        closed_decisions = []
        for decision in unreachable_decisions:
            try:
                # Update decision status
                updated_decision = crud.close_decision_as_unreachable(db, decision.id)
                if updated_decision:
                    closed_decisions.append(updated_decision)
                    logger.info(f"🔒 Closed decision #{decision.id} as unreachable")
            except Exception as e:
                logger.error(f"❌ Error closing decision #{decision.id}: {e}")
        
        # Send notification to channel about closed decisions
        if closed_decisions:
            notification = format_unreachable_notification(closed_decisions, user_name, current_member_count)
            try:
                slack_client.send_message(
                    channel=channel_id,
                    text=notification
                )
                logger.info(f"📢 Sent notification about {len(closed_decisions)} closed decisions")
            except Exception as e:
                logger.error(f"❌ Error sending notification: {e}")
                
    except Exception as e:
        logger.error(f"❌ Error handling member leave for {user_name}: {e}", exc_info=True)


def format_unreachable_notification(decisions: list, leaving_member: str, current_count: int) -> str:
    """
    Format notification message for closed unreachable decisions.
    
    Args:
        decisions: List of Decision objects that were closed
        leaving_member: Name of the member who left
        current_count: Current number of members in channel
        
    Returns:
        Formatted notification message
    """
    message_parts = [
        f"⚠️ *{len(decisions)} decision{'s' if len(decisions) != 1 else ''} closed due to member departure*\n\n",
        f"_{leaving_member} left the channel. The following pending decisions can no longer reach their approval threshold:_\n\n"
    ]
    
    for decision in decisions:
        message_parts.append(
            f"*Decision #{decision.id}* - ❌ Closed as Unreachable\n"
            f"_{decision.text}_\n"
            f"• Required: {decision.approval_threshold} approvals\n"
            f"• Current members: {current_count}\n"
            f"• Had: {decision.approval_count} approvals, {decision.rejection_count} rejections\n"
            f"• Proposed by: {decision.proposer_name}\n\n"
        )
    
    message_parts.append(
        f"💡 *Note:* Vote history has been preserved. "
        f"You can view these decisions with `/decision show <id>` or `/decision list`."
    )
    
    return "".join(message_parts)

