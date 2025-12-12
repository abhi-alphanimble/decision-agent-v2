"""
Handlers for decision-related commands
"""
import math
from sqlalchemy.orm import Session
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..database import crud
from ..command_parser import ParsedCommand
from ..slack import slack_client
from ..utils.display import format_vote_summary, display_vote_list
from ..models import Decision # Import Decision model for type hinting
from ..utils import truncate_text # NEW: Import the utility function
from ..ai.ai_client import ai_client # Import AI client
from ..integrations.zoho_sync import sync_decision_to_zoho, sync_vote_to_zoho, is_zoho_enabled

from ..config import get_context_logger
logger = get_context_logger(__name__)

# Default values used when channel config or Slack API is unavailable
# These are fallbacks only - actual values come from ChannelConfig in database
# Use a conservative fallback of 1 member when Slack cannot be queried
DEFAULT_GROUP_SIZE = 1  # Fallback when Slack API fails
DEFAULT_APPROVAL_PERCENTAGE = 60  # Used in ChannelConfig default

# Helper constants
DECISION_STATUS_EMOJI = {
    "pending": "⏳",
    "approved": "✅",
    "rejected": "❌",
    "expired": "⌛",
}
DECISIONS_PER_PAGE = 10  # Pagination limit

# ============================================================================
# DECISION COMMAND HANDLERS
# ============================================================================

def handle_propose_command(
    parsed: ParsedCommand,
    user_id: str,
    user_name: str,
    channel_id: str,
    db: Session,
    team_id: str = ""
) -> Dict[str, Any]:
    """
    Handle proposal command.
    
    Args:
        parsed: Parsed command data
        user_id: Slack user ID
        user_name: User's display name
        channel_id: Slack channel ID
        db: Database session
        team_id: Slack team ID for multi-workspace support
    """
    logger = get_context_logger(__name__, user_id=user_id, channel_id=channel_id)
    logger.info("Handling PROPOSE command", extra={"user_name": user_name, "team_id": team_id})
    
    # Get workspace-specific Slack client
    from ..slack.client import get_client_for_team
    ws_client = get_client_for_team(team_id, db) if team_id else None
    
    # Extract proposal text
    if not parsed.args or len(parsed.args) == 0:
        logger.warning("❌ No proposal text provided")
        return {
            "text": "❌ Please wrap your proposal in quotes.\n\n*Example:* `/decision propose \"Should we order pizza?\"`",
            "response_type": "ephemeral"
        }
    
    proposal_text = parsed.args[0].strip()
    
    # Validate text length (minimum)
    if len(proposal_text) < 10:
        logger.warning(f"❌ Proposal too short: {len(proposal_text)} chars")
        return {
            "text": f"❌ Proposal too short. Minimum 10 characters.\n\n*You provided:* {len(proposal_text)} character(s)\n*Your text:* \"{proposal_text}\"",
            "response_type": "ephemeral"
        }
    
    # Validate text length (maximum)
    if len(proposal_text) > 500:
        logger.warning(f"❌ Proposal too long: {len(proposal_text)} chars")
        return {
            "text": f"❌ Proposal too long. Maximum 500 characters.\n\n*You provided:* {len(proposal_text)} characters\n*Limit:* 500 characters\n\n💡 *Tip:* Try to be more concise!",
            "response_type": "ephemeral"
        }
    
    # Create decision in database
    try:
        # 1. Get real member count from Slack dynamically
        try:
            if ws_client:
                group_size = ws_client.get_channel_members_count(channel_id)
            else:
                # Fallback to global client (for backward compatibility)
                group_size = slack_client.get_channel_members_count(channel_id)
            if not isinstance(group_size, int) or group_size <= 0:
                logger.warning(f"⚠️ Invalid group size from Slack: {group_size}, defaulting to DEFAULT_GROUP_SIZE")
                group_size = DEFAULT_GROUP_SIZE
            logger.info(f"📊 Fetched dynamic member count from Slack: {group_size} members in {channel_id}")
        except Exception as e:
            logger.error(f"❌ Error fetching group size: {e}")
            group_size = DEFAULT_GROUP_SIZE

        # 2. Get channel config (no longer passes group_size to it)
        config = crud.get_channel_config(db, channel_id)
        
        # 3. Calculate threshold dynamically using the real group_size from Slack
        # Threshold = ceil(group_size * percentage / 100)
        approval_threshold = math.ceil(group_size * (config.approval_percentage / 100.0))
        
        # Ensure at least 1 vote needed
        if approval_threshold < 1:
            approval_threshold = 1
            
        logger.info(f"📊 New Decision Params: Size={group_size}, %={config.approval_percentage}, Threshold={approval_threshold}")

        decision = crud.create_decision(
            db=db,
            channel_id=channel_id,
            text=proposal_text,
            created_by=user_id,
            created_by_name=user_name,
            group_size_at_creation=group_size,
            approval_threshold=approval_threshold
        )
        
        logger.info(f"✅ Created decision #{decision.id} by {user_name}: '{proposal_text[:50]}...'")
        
        # Sync to Zoho CRM
        if is_zoho_enabled():
            try:
                # Get channel name from Slack
                channel_name = ""
                try:
                    if ws_client:
                        channel_info = ws_client.get_channel_info(channel_id)
                    else:
                        channel_info = slack_client.get_channel_info(channel_id)
                    channel_name = channel_info.get("name", "")
                except Exception as e:
                    logger.debug(f"Could not fetch channel name: {e}")
                
                sync_decision_to_zoho(decision, channel_name)
                logger.info(f"✅ Synced decision #{decision.id} to Zoho CRM")
            except Exception as e:
                logger.error(f"❌ Failed to sync to Zoho: {e}", exc_info=True)
                # Continue execution - don't fail the main operation
        
        # Format success message
        response_text = format_proposal_success_message(decision)
        
        # Send to channel using workspace-specific client
        try:
            if ws_client:
                ws_client.send_message(channel=channel_id, text=response_text)
            else:
                slack_client.send_message(channel=channel_id, text=response_text)
            logger.info(f"✅ Sent proposal #{decision.id} to channel {channel_id}")
        except Exception as e:
            logger.error(f"❌ Error sending to Slack: {e}", exc_info=True)
        
        # Return acknowledgment
        return {
            "text": f"✅ Your proposal has been posted to the channel!\n\n*Decision #{decision.id}:* \"{proposal_text[:100]}{'...' if len(proposal_text) > 100 else ''}\"",
            "response_type": "ephemeral"
        }
        
    except Exception as e:
        logger.error(f"❌ Database error creating proposal: {e}", exc_info=True)
        db.rollback()
        return {
            "text": f"❌ Failed to create proposal. Please try again.\n\n*Error:* Database error occurred",
            "response_type": "ephemeral"
        }


def handle_add_command(
    parsed: ParsedCommand,
    user_id: str,
    user_name: str,
    channel_id: str,
    db: Session,
    team_id: str = ""
) -> Dict[str, Any]:
    """
    Handle add command - create a pre-approved decision.
    Command: /decision add "Decision text"
    
    Args:
        team_id: Slack team ID for multi-workspace support
    """
    logger = get_context_logger(__name__, user_id=user_id, channel_id=channel_id)
    logger.info("Handling ADD command", extra={"user_name": user_name, "team_id": team_id})
    
    # Get workspace-specific Slack client
    from ..slack.client import get_client_for_team
    ws_client = get_client_for_team(team_id, db) if team_id else None

    # Extract text (same validation as propose)
    if not parsed.args or len(parsed.args) == 0:
        logger.warning("❌ No decision text provided for add")
        return {
            "text": "❌ Please wrap the decision in quotes.\n\n*Example:* `/decision add \"Decision text\"`",
            "response_type": "ephemeral"
        }

    decision_text = parsed.args[0].strip()

    if len(decision_text) < 10:
        logger.warning(f"❌ Add text too short: {len(decision_text)} chars")
        return {
            "text": f"❌ Decision text too short. Minimum 10 characters.\n\n*You provided:* {len(decision_text)} character(s)",
            "response_type": "ephemeral"
        }

    if len(decision_text) > 500:
        logger.warning(f"❌ Add text too long: {len(decision_text)} chars")
        return {
            "text": f"❌ Decision text too long. Maximum 500 characters.",
            "response_type": "ephemeral"
        }

    try:
        # Get group size and config dynamically
        try:
            if ws_client:
                group_size = ws_client.get_channel_members_count(channel_id)
            else:
                group_size = slack_client.get_channel_members_count(channel_id)
            if not isinstance(group_size, int) or group_size <= 0:
                logger.warning(f"⚠️ Invalid group size from Slack: {group_size}, defaulting to DEFAULT_GROUP_SIZE")
                group_size = DEFAULT_GROUP_SIZE
            logger.info(f"📊 Fetched dynamic member count from Slack: {group_size} members in {channel_id}")
        except Exception as e:
            logger.error(f"❌ Error fetching group size for add: {e}")
            group_size = DEFAULT_GROUP_SIZE

        config = crud.get_channel_config(db, channel_id)
        approval_threshold = int(group_size * (config.approval_percentage / 100.0))
        if approval_threshold < 1:
            approval_threshold = 1

        # Create decision as approved
        decision = crud.create_decision(
            db=db,
            channel_id=channel_id,
            text=decision_text,
            created_by=user_id,
            created_by_name=user_name,
            group_size_at_creation=group_size,
            approval_threshold=approval_threshold,
            status="approved",
        )

        # Mark approval_count to threshold so display is consistent
        try:
            decision.approval_count = decision.approval_threshold
            db.commit()
            db.refresh(decision)
        except Exception:
            db.rollback()

        logger.info(f"✅ Added pre-approved decision #{decision.id} by {user_name}")

        # Notify channel using workspace-specific client
        try:
            if ws_client:
                ws_client.send_message(channel=channel_id, text=format_decision_approved_message(decision, db))
            else:
                slack_client.send_message(channel=channel_id, text=format_decision_approved_message(decision, db))
        except Exception as e:
            logger.error(f"❌ Error sending add notification to Slack: {e}")

        return {
            "text": f"✅ Pre-approved decision added as #{decision.id}: \"{decision_text[:100]}{'...' if len(decision_text) > 100 else ''}\"",
            "response_type": "ephemeral"
        }

    except Exception as e:
        logger.error(f"❌ Error creating pre-approved decision: {e}", exc_info=True)
        db.rollback()
        return {
            "text": "❌ Failed to add pre-approved decision. Please try again.",
            "response_type": "ephemeral"
        }


def handle_approve_command(
    parsed: ParsedCommand,
    user_id: str,
    user_name: str,
    channel_id: str,
    db: Session,
    team_id: str = ""
) -> Dict[str, Any]:
    """
    Handle approval vote command.
    Command: /decision approve <decision_id>
    
    Args:
        team_id: Slack team ID for multi-workspace support
    """
    logger = get_context_logger(__name__, user_id=user_id, channel_id=channel_id)
    logger.info("Handling APPROVE command", extra={"user_name": user_name, "team_id": team_id})
    
    # Get workspace-specific Slack client
    from ..slack.client import get_client_for_team
    ws_client = get_client_for_team(team_id, db) if team_id else None

    # 1. Extract decision_id
    if not parsed.args or len(parsed.args) == 0:
        logger.warning("❌ No decision ID provided")
        return {
            "text": "❌ Please provide a decision ID.\n\n*Example:* `/decision approve 42`",
            "response_type": "ephemeral"
        }

    try:
        decision_id = int(parsed.args[0])
    except (ValueError, TypeError):
        logger.warning(f"❌ Invalid decision ID: {parsed.args[0]}")
        return {
            "text": f"❌ Invalid decision ID: `{parsed.args[0]}`\n\nDecision ID must be a number.\n\n*Example:* `/decision approve 42`",
            "response_type": "ephemeral"
        }

    # 2. Get decision from database
    decision = crud.get_decision_by_id(db, decision_id)

    if not decision:
        logger.warning(f"❌ Decision #{decision_id} not found")
        return {
            "text": f"❌ Decision #{decision_id} not found.\n\nUse `/decision list` to see available decisions.",
            "response_type": "ephemeral"
        }

    # 3. Check if decision is still pending
    if decision.status != "pending":
        logger.warning(f"❌ Decision #{decision_id} is {decision.status}")
        return {
            "text": f"❌ Decision #{decision_id} is already closed (status: {decision.status.upper()}).\n\nYou can only vote on pending decisions.",
            "response_type": "ephemeral"
        }

    # 4. Check if user already voted
    if crud.check_if_user_voted(db, decision_id, user_id):
        logger.warning(f"❌ User {user_name} already voted on #{decision_id}")

        # Get their existing vote
        existing_vote = crud.get_user_vote(db, decision_id, user_id)
        vote_type = existing_vote.vote_type if existing_vote else "unknown"

        return {
            "text": f"❌ You already voted on this decision.\n\n*Your vote:* {vote_type.upper()}\n*Decision:* {decision.text[:100]}...\n\n💡 Use `/decision myvote {decision_id}` to see your vote details.",
            "response_type": "ephemeral"
        }

    # 5. Create vote and update counts atomically
    success, message, updated_decision = crud.vote_on_decision(
        db=db,
        decision_id=decision_id,
        voter_id=user_id,
        voter_name=user_name,
        vote_type="approve",
        return_updated_decision=True,
    )

    if not success:
        logger.error(f"❌ Vote failed: {message}")
        return {
            "text": message,
            "response_type": "ephemeral"
        }

    logger.info(f"✅ Vote recorded: User {user_id} approved #{decision_id}")

    # Sync vote to Zoho CRM
    if is_zoho_enabled():
        try:
            # Get channel name from Slack
            channel_name = ""
            try:
                if ws_client:
                    channel_info = ws_client.get_channel_info(channel_id)
                else:
                    channel_info = slack_client.get_channel_info(channel_id)
                channel_name = channel_info.get("name", "")
            except Exception as e:
                logger.debug(f"Could not fetch channel name: {e}")
            
            sync_vote_to_zoho(updated_decision, channel_name)
            logger.info(f"✅ Synced vote for decision #{decision_id} to Zoho CRM")
        except Exception as e:
            logger.error(f"❌ Failed to sync vote to Zoho: {e}", exc_info=True)
            # Continue execution - don't fail the main operation

    # 6. Format confirmation message
    confirmation = format_vote_confirmation(updated_decision, "approve", user_id)

    # 7. Check if decision was closed
    if updated_decision.status == "approved":
        logger.info(f"🎉 Decision #{decision_id} APPROVED!")

        # Send channel notification using workspace-specific client
        try:
            channel_message = format_decision_approved_message(updated_decision, db)
            if ws_client:
                ws_client.send_message(channel=channel_id, text=channel_message)
            else:
                slack_client.send_message(channel=channel_id, text=channel_message)
            logger.info(f"✅ Sent approval notification to channel {channel_id}")
        except Exception as e:
            logger.error(f"❌ Error sending approval notification: {e}")

    # 8. Return confirmation to user
    return {
        "text": confirmation,
        "response_type": "ephemeral"
    }


def handle_reject_command(
    parsed: ParsedCommand,
    user_id: str,
    user_name: str,
    channel_id: str,
    db: Session,
    team_id: str = ""
) -> Dict[str, Any]:
    """
    Handle rejection vote command.
    Command: /decision reject <decision_id>
    
    Args:
        team_id: Slack team ID for multi-workspace support
    """
    logger = get_context_logger(__name__, user_id=user_id, channel_id=channel_id)
    logger.info("Handling REJECT command", extra={"user_name": user_name, "team_id": team_id})
    
    # Get workspace-specific Slack client
    from ..slack.client import get_client_for_team
    ws_client = get_client_for_team(team_id, db) if team_id else None
    
    # 1. Extract decision_id
    if not parsed.args or len(parsed.args) == 0:
        logger.warning("❌ No decision ID provided")
        return {
            "text": "❌ Please provide a decision ID.\n\n*Example:* `/decision reject 42`",
            "response_type": "ephemeral"
        }
    
    try:
        decision_id = int(parsed.args[0])
    except (ValueError, TypeError):
        logger.warning(f"❌ Invalid decision ID: {parsed.args[0]}")
        return {
            "text": f"❌ Invalid decision ID: `{parsed.args[0]}`\n\nDecision ID must be a number.\n\n*Example:* `/decision reject 42`",
            "response_type": "ephemeral"
        }
    
    # 2. Get decision from database
    decision = crud.get_decision_by_id(db, decision_id)
    
    if not decision:
        logger.warning(f"❌ Decision #{decision_id} not found")
        return {
            "text": f"❌ Decision #{decision_id} not found.\n\nUse `/decision list` to see available decisions.",
            "response_type": "ephemeral"
        }
    
    # 3. Check if decision is still pending
    if decision.status != "pending":
        logger.warning(f"❌ Decision #{decision_id} is {decision.status}")
        return {
            "text": f"❌ Decision #{decision_id} is already closed (status: {decision.status.upper()}).\n\nYou can only vote on pending decisions.",
            "response_type": "ephemeral"
        }
    
    # 4. Check if user already voted
    if crud.check_if_user_voted(db, decision_id, user_id):
        logger.warning(f"❌ User {user_name} already voted on #{decision_id}")
        
        # Get their existing vote
        existing_vote = crud.get_user_vote(db, decision_id, user_id)
        vote_type = existing_vote.vote_type if existing_vote else "unknown"
        
        return {
            "text": f"❌ You already voted on this decision.\n\n*Your vote:* {vote_type.upper()}\n*Decision:* {decision.text[:100]}...\n\n💡 Use `/decision myvote {decision_id}` to see your vote details.",
            "response_type": "ephemeral"
        }
    
    # 5. Create vote and update counts atomically
    success, message, updated_decision = crud.vote_on_decision(
        db=db,
        decision_id=decision_id,
        voter_id=user_id,
        voter_name=user_name,
        vote_type="reject",
        return_updated_decision=True,
    )
    
    if not success:
        logger.error(f"❌ Vote failed: {message}")
        return {
            "text": message,
            "response_type": "ephemeral"
        }
    
    logger.info(f"✅ Vote recorded: User {user_id} rejected #{decision_id}")
    
    # 6. Format confirmation message
    confirmation = format_vote_confirmation(updated_decision, "reject", user_id)
    
    # 7. Check if decision was closed
    if updated_decision.status == "rejected":
        logger.info(f"❌ Decision #{decision_id} REJECTED!")
        
        # Send channel notification using workspace-specific client
        try:
            channel_message = format_decision_rejected_message(updated_decision, db)
            if ws_client:
                ws_client.send_message(channel=channel_id, text=channel_message)
            else:
                slack_client.send_message(channel=channel_id, text=channel_message)
            logger.info(f"✅ Sent rejection notification to channel {channel_id}")
        except Exception as e:
            logger.error(f"❌ Error sending rejection notification: {e}")
    
    # 8. Return confirmation to user
    return {
        "text": confirmation,
        "response_type": "ephemeral"
    }


def handle_summarize_command(
    parsed: ParsedCommand,
    user_id: str,
    user_name: str,
    channel_id: str,
    db: Session
) -> Dict[str, Any]:
    """
    Handle summarize command to generate AI summary for a decision.
    Command: /decision summarize <decision_id>
    """
    logger = get_context_logger(__name__, user_id=user_id, channel_id=channel_id)
    logger.info("Handling SUMMARIZE command", extra={"user_name": user_name})

    # 1. Extract decision_id
    if not parsed.args or len(parsed.args) == 0:
        logger.warning("❌ No decision ID provided for summary")
        return {
            "text": "❌ Please provide a decision ID to summarize.\n\n*Example:* `/decision summarize 42`",
            "response_type": "ephemeral"
        }

    try:
        decision_id = int(parsed.args[0])
    except (ValueError, TypeError):
        logger.warning(f"❌ Invalid decision ID: {parsed.args[0]}")
        return {
            "text": f"❌ Invalid decision ID: `{parsed.args[0]}`\n\nDecision ID must be a number.",
            "response_type": "ephemeral"
        }

    # 2. Get decision from database
    decision = crud.get_decision_by_id(db, decision_id)

    if not decision:
        logger.warning(f"❌ Decision #{decision_id} not found")
        return {
            "text": f"❌ Decision #{decision_id} not found.",
            "response_type": "ephemeral"
        }

    # 3. Get votes for context
    votes = crud.get_votes_by_decision(db, decision_id)

    # 4. Generate summary
    try:
        summary = ai_client.summarize_decision(decision, votes)

        if not summary:
            return {
                "text": "🤖 AI service currently unavailable or not configured for summaries.",
                "response_type": "ephemeral"
            }

        return {
            "text": f"🤖 *AI Summary for Decision #{decision_id}*\n\n{summary}",
            "response_type": "ephemeral"
        }

    except Exception as e:
        logger.error(f"❌ Error generating summary: {e}")
        return {
            "text": "❌ An error occurred while generating the summary. Please try again later.",
            "response_type": "ephemeral"
        }


def handle_suggest_command(
    parsed: ParsedCommand,
    user_id: str,
    user_name: str,
    channel_id: str,
    db: Session
) -> Dict[str, Any]:
    """
    Handle suggest command to generate AI suggestions for next steps.
    Command: /decision suggest <decision_id>
    """
    logger = get_context_logger(__name__, user_id=user_id, channel_id=channel_id)
    logger.info("Handling SUGGEST command", extra={"user_name": user_name})

    # 1. Extract decision_id
    if not parsed.args or len(parsed.args) == 0:
        logger.warning("❌ No decision ID provided for suggestions")
        return {
            "text": "❌ Please provide a decision ID to get suggestions.\n\n*Example:* `/decision suggest 42`",
            "response_type": "ephemeral"
        }

    try:
        decision_id = int(parsed.args[0])
    except (ValueError, TypeError):
        logger.warning(f"❌ Invalid decision ID: {parsed.args[0]}")
        return {
            "text": f"❌ Invalid decision ID: `{parsed.args[0]}`\n\nDecision ID must be a number.",
            "response_type": "ephemeral"
        }

    # 2. Get decision from database
    decision = crud.get_decision_by_id(db, decision_id)

    if not decision:
        logger.warning(f"❌ Decision #{decision_id} not found")
        return {
            "text": f"❌ Decision #{decision_id} not found.",
            "response_type": "ephemeral"
        }

    # 3. Get votes for context
    votes = crud.get_votes_by_decision(db, decision_id)

    # 4. Generate suggestions
    try:
        suggestions = ai_client.suggest_next_steps(decision, votes)

        if not suggestions:
            return {
                "text": "❌ Unable to generate suggestions. Please check if the AI service is configured correctly.",
                "response_type": "ephemeral"
            }

        return {
            "text": f"🤖 *AI Suggestions for Decision #{decision_id}*\n\n{suggestions}",
            "response_type": "ephemeral"
        }

    except Exception as e:
        logger.error(f"❌ Error generating suggestions: {e}")
        return {
            "text": "❌ An error occurred while generating suggestions. Please try again later.",
            "response_type": "ephemeral"
        }


def handle_show_command(
    parsed: ParsedCommand,
    user_id: str,
    user_name: str,
    channel_id: str,
    db: Session
) -> Dict[str, Any]:
    """
    Handle show/detail command.
    Command: /decision show <decision_id>
    Shows full decision details with vote list.
    """
    logger = get_context_logger(__name__, user_id=user_id, channel_id=channel_id)
    logger.info("Handling SHOW command", extra={"user_name": user_name})
    
    # 1. Extract decision_id
    if not parsed.args or len(parsed.args) == 0:
        logger.warning("❌ No decision ID provided")
        return {
            "text": "❌ Please provide a decision ID.\n\n*Example:* `/decision show 42`",
            "response_type": "ephemeral"
        }
    
    try:
        decision_id = int(parsed.args[0])
    except (ValueError, TypeError):
        logger.warning(f"❌ Invalid decision ID: {parsed.args[0]}")
        return {
            "text": f"❌ Invalid decision ID: `{parsed.args[0]}`\n\nDecision ID must be a number.",
            "response_type": "ephemeral"
        }
    
    # 2. Get decision from database
    decision = crud.get_decision_by_id(db, decision_id)
    
    if not decision:
        logger.warning(f"❌ Decision #{decision_id} not found")
        return {
            "text": f"❌ Decision #{decision_id} not found.\n\nUse `/decision list` to see available decisions.",
            "response_type": "ephemeral"
        }
    
    # 3. Get all votes for this decision
    votes = crud.get_votes_by_decision(db, decision_id)
    
    # 4. Format decision detail with votes
    detail_message = format_decision_detail(decision, votes)
    
    return {
        "text": detail_message,
        "response_type": "ephemeral"
    }


def handle_myvote_command(
    parsed: ParsedCommand,
    user_id: str,
    user_name: str,
    channel_id: str,
    db: Session
) -> Dict[str, Any]:
    """
    Handle myvote command.
    Command: /decision myvote <decision_id>
    Shows user their own vote.
    """
    logger = get_context_logger(__name__, user_id=user_id, channel_id=channel_id)
    logger.info("Handling MYVOTE command", extra={"user_name": user_name})
    
    # 1. Extract decision_id
    if not parsed.args or len(parsed.args) == 0:
        logger.warning("❌ No decision ID provided")
        return {
            "text": "❌ Please provide a decision ID.\n\n*Example:* `/decision myvote 42`",
            "response_type": "ephemeral"
        }
    
    try:
        decision_id = int(parsed.args[0])
    except (ValueError, TypeError):
        logger.warning(f"❌ Invalid decision ID: {parsed.args[0]}")
        return {
            "text": f"❌ Invalid decision ID: `{parsed.args[0]}`\n\nDecision ID must be a number.",
            "response_type": "ephemeral"
        }
    
    # 2. Get decision from database
    decision = crud.get_decision_by_id(db, decision_id)
    
    if not decision:
        logger.warning(f"❌ Decision #{decision_id} not found")
        return {
            "text": f"❌ Decision #{decision_id} not found.\n\nUse `/decision list` to see available decisions.",
            "response_type": "ephemeral"
        }
    
    # 3. Get user's vote
    vote = crud.get_user_vote(db, decision_id, user_id)
    
    if not vote:
        logger.info(f"ℹ️ User {user_id} hasn't voted on #{decision_id}")
        return {
            "text": f"ℹ️ You haven't voted on decision #{decision_id} yet.\n\n*Decision:* {decision.text}\n\n*How to vote:*\n- `/decision approve {decision_id}` - Vote to approve\n- `/decision reject {decision_id}` - Vote to reject",
            "response_type": "ephemeral"
        }
    
    # 4. Format vote info
    vote_message = format_user_vote_detail(vote, decision)
    
    return {
        "text": vote_message,
        "response_type": "ephemeral"
    }

# ============================================================================
# NEW: LIST COMMAND HANDLER
# ============================================================================

def handle_list_command(
    parsed: ParsedCommand,
    channel_id: str,
    db: Session
) -> Dict[str, Any]:
    """
    Handle decision list command with optional status filter and pagination.
    Command: /decision list [all|pending|approved|rejected] [page_number]
    """
    logger = get_context_logger(__name__, channel_id=channel_id)
    logger.info("Handling LIST command")
    
    # Initialize page to default
    page = 1
    
    # 1. Parse optional status filter (default to "all")
    status_filter_raw = (parsed.args[0] if parsed.args else "all").lower()
    
    # Determine the status filter and the expected page number index
    page_index = 0 
    
    if status_filter_raw in ["all", "any", ""]:
        status_filter = None
        filter_title = "All"
        page_index = 0 # Page number could be the first argument
    elif status_filter_raw in ["pending", "approved", "rejected", "expired"]:
        status_filter = status_filter_raw
        filter_title = status_filter.title()
        page_index = 1 # Page number is the second argument
    else:
        # If the first arg is not a recognized filter, treat it as a page number for "all"
        try:
            page = int(status_filter_raw)
            status_filter = None
            filter_title = "All"
        except (ValueError, TypeError):
             return {
                "text": f"❌ Invalid status filter or page number: `{status_filter_raw}`. Use: `all`, `pending`, `approved`, `rejected`, or a page number.",
                "response_type": "ephemeral"
            }


    # 2. Parse optional page number (default to 1) if not already parsed from first arg
    try:
        if len(parsed.args) > page_index:
            page = int(parsed.args[page_index])
            
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1 # Ignore invalid page argument

    logger.info(f"📋 LIST Query: channel={channel_id}, status={status_filter}, page={page}")

    # 3. Query all decisions for summary and the page decisions
    offset = (page - 1) * DECISIONS_PER_PAGE
    
    # Get summary counts
    summary = crud.get_decision_summary_by_channel(db, channel_id)

    # Get the paginated list of decisions
    decisions_on_page = crud.get_decisions_by_channel_paginated(
        db=db,
        channel_id=channel_id,
        status=status_filter,
        limit=DECISIONS_PER_PAGE,
        offset=offset
    )

    # Get the total count for the *filtered* set (for pagination math)
    total_filtered_count = 0
    if status_filter == "pending":
        total_filtered_count = summary.get("pending", 0)
    elif status_filter == "approved":
        total_filtered_count = summary.get("approved", 0)
    elif status_filter == "rejected":
        total_filtered_count = summary.get("rejected", 0)
    else: # "all"
        total_filtered_count = summary.get("total", 0)
        
    total_pages = (total_filtered_count + DECISIONS_PER_PAGE - 1) // DECISIONS_PER_PAGE

    # 4. Handle empty results gracefully
    if not decisions_on_page:
        status_display = filter_title if filter_title != "All" else ""
        if total_filtered_count == 0:
             # If there are zero decisions for this channel, try a helpful diagnostic.
             try:
                 total_global = db.query(Decision).count()
             except Exception:
                 total_global = None

             # If there are decisions elsewhere in the DB, hint that the channel id may not match stored entries.
             if total_global and total_global > 0 and summary.get("total", 0) == 0:
                 logger.info(f"No decisions found for channel {channel_id} but {total_global} decisions exist globally")
                 return {
                     "text": (
                         f"ℹ️ No {status_display.lower()} decisions found for this channel (ID: {channel_id}).\n\n"
                         "I can see decisions exist in other channels in the database. "
                         "This usually means the stored channel identifier for your proposals doesn't match the current channel ID.\n\n"
                         "Try running the command in the channel where proposals were originally posted, or ask an admin to check the database."
                     ),
                     "response_type": "ephemeral"
                 }

             return {
                "text": f"ℹ️ No {status_display.lower()} decisions found for this channel.",
                "response_type": "ephemeral"
            }
        # Only return this if the user requested an invalid page
        if page > total_pages: 
             return {
                "text": f"⚠️ Page {page} is empty. The last page of {status_display} decisions is page {total_pages}.",
                "response_type": "ephemeral"
            }

    # 5. Format the response
    message = format_decision_list_message(
        decisions_on_page,
        summary,
        filter_title,
        page,
        total_pages,
        total_filtered_count
    )

    return {
        "text": message,
        "response_type": "ephemeral"
    }


# ============================================================================
# FORMATTING HELPER FUNCTIONS
# ============================================================================

def format_decision_list_message(
    decisions: List[Decision], 
    summary: Dict[str, int], 
    filter_title: str,
    current_page: int,
    total_pages: int,
    total_filtered_count: int
) -> str:
    """
    Formats the complete Slack message for the decision list command.
    """
    
    # 1. Format Summary Statistics
    summary_message = f"""📋 *Decision Summary*
Total: *{summary.get('total', 0)}* decisions (⏳ *{summary.get('pending', 0)}* pending, ✅ *{summary.get('approved', 0)}* approved, ❌ *{summary.get('rejected', 0)}* rejected)

"""
    
    # 2. Format Header & Pagination
    header_message = f"""*{filter_title} Decisions* (Page {current_page}/{total_pages}, {total_filtered_count} total)
---
"""
    
    # 3. Format Decision List Items
    list_items = []
    for decision in decisions:
        status_emoji = DECISION_STATUS_EMOJI.get(decision.status, "❓")
        
        # Truncate text to 50 characters (plus "...")
        truncated_text = truncate_text(decision.text, 50)
        
        # Format date as YYYY-MM-DD
        date_str = decision.created_at.strftime('%Y-%m-%d')
        
        # Assemble line: ID, truncated text, status, vote counts, date
        item = (
            f"*{decision.id}:* {truncated_text} "
            f"({status_emoji} {decision.status.title()}) "
            f"[👍 {decision.approval_count} | 👎 {decision.rejection_count}] "
            f"_({date_str})_"
        )
        list_items.append(item)
        
    list_message = "\n".join(list_items)
    
    # 4. Format Footer (Pagination hint)
    footer_message = ""
    if total_pages > 1:
        next_page = current_page + 1
        prev_page = current_page - 1
        
        # Handle filter argument for pagination command
        filter_arg = filter_title.lower() if filter_title != 'All' else ''
        
        pagination_links = []
        if prev_page >= 1:
             pagination_links.append(f"Prev: `/decision list {filter_arg} {prev_page}`".strip())
        if next_page <= total_pages:
             pagination_links.append(f"Next: `/decision list {filter_arg} {next_page}`".strip())
             
        if pagination_links:
            # Clean up the command format in case filter_arg was empty
            final_links = [link.replace('list  ', 'list ').strip() for link in pagination_links]
            footer_message = f"\n\n--- \n{ ' | '.join(final_links) }"

    return summary_message + header_message + list_message + footer_message


def format_proposal_success_message(decision) -> str:
    """Format a success message for a new proposal."""
    return f"""🗳️ *New Decision Proposal*

*Decision #{decision.id}*
{decision.text}

📊 *Status:* PENDING ⏳
👤 *Proposed by:* {decision.proposer_name}
✅ *Required approvals:* {decision.approval_threshold}/{decision.group_size_at_creation}
📈 *Current votes:* 0 approvals, 0 rejections

*How to vote:*
- `/decision approve {decision.id}` - Vote to approve
- `/decision reject {decision.id}` - Vote to reject

💡 *Tip:* Use `/decision show {decision.id}` to see details anytime
"""


def format_vote_confirmation(decision, vote_type: str, user_id: str) -> str:
    """Format vote confirmation message."""
    emoji = "✅" if vote_type == "approve" else "❌"
    vote_word = "approved" if vote_type == "approve" else "rejected"
    
    message = f"""{emoji} *Vote Recorded*

You voted to *{vote_word}* this decision:
"{decision.text}"

📊 *Current Status:*
- ✅ Approvals: {decision.approval_count}/{decision.approval_threshold}
- ❌ Rejections: {decision.rejection_count}/{decision.approval_threshold}
- 📈 Status: {decision.status.upper()}
"""
    
    if decision.status == "pending":
        remaining = decision.approval_threshold - max(decision.approval_count, decision.rejection_count)
        message += f"\n💡 *{remaining} more vote(s) needed to close this decision*"
    
    message += f"\n\n💡 Use `/decision myvote {decision.id}` to check your vote anytime"
    
    return message


def format_decision_approved_message(decision, db: Session) -> str:
    """Format message when decision is approved."""
    # Get votes to show who voted
    votes = crud.get_votes_by_decision(db, decision.id)
    vote_summary = display_vote_list(votes)
    
    return f"""🎉 *DECISION APPROVED!*

*Decision #{decision.id}*
{decision.text}

✅ *Final Vote:* {decision.approval_count}/{decision.group_size_at_creation} approvals
📊 *Rejections:* {decision.rejection_count}
👤 *Proposed by:* {decision.proposer_name}
⏰ *Closed:* {decision.closed_at.strftime('%Y-%m-%d %H:%M UTC')}

*Votes:*
{vote_summary}

The team has approved this proposal! 🎊
"""


def format_decision_rejected_message(decision, db: Session) -> str:
    """Format message when decision is rejected."""
    # Get votes to show who voted
    votes = crud.get_votes_by_decision(db, decision.id)
    vote_summary = display_vote_list(votes)
    
    return f"""❌ *DECISION REJECTED*

*Decision #{decision.id}*
{decision.text}

❌ *Final Vote:* {decision.rejection_count}/{decision.group_size_at_creation} rejections
📊 *Approvals:* {decision.approval_count}
👤 *Proposed by:* {decision.proposer_name}
⏰ *Closed:* {decision.closed_at.strftime('%Y-%m-%d %H:%M UTC')}

*Votes:*
{vote_summary}

The team has rejected this proposal.
"""


def format_decision_detail(decision, votes: list) -> str:
    """
    Format full decision detail view with vote list.
    """
    # Status emoji
    status_emoji = {
        "pending": "⏳",
        "approved": "✅",
        "rejected": "❌"
    }.get(decision.status, "❓")
    
    # Format vote summary
    vote_summary = display_vote_list(votes)
    
    message = f"""📋 *Decision #{decision.id}*

*Proposal:*
{decision.text}

📊 *Status:* {status_emoji} {decision.status.upper()}
👤 *Proposed by:* {decision.proposer_name}
✅ *Approval threshold:* {decision.approval_threshold}/{decision.group_size_at_creation}
📈 *Current votes:* {decision.approval_count} approvals, {decision.rejection_count} rejections
"""
    
    if decision.closed_at:
        message += f"⏰ *Closed:* {decision.closed_at.strftime('%Y-%m-%d %H:%M UTC')}\n"
    
    message += f"\n*Votes:*\n{vote_summary}"
    
    if decision.status == "pending":
        message += f"\n\n*How to vote:*\n- `/decision approve {decision.id}` - Vote to approve\n- `/decision reject {decision.id}` - Vote to reject"
    
    return message


def format_user_vote_detail(vote, decision) -> str:
    """
    Format user's own vote details.
    """
    vote_emoji = "👍" if vote.vote_type == "approve" else "👎"
    vote_text = "approved" if vote.vote_type == "approve" else "rejected"
    
    message = f"""*Your Vote on Decision #{decision.id}*

*Decision:*
{decision.text}

{vote_emoji} You {vote_text} this decision
"""
    
    # Add timestamp if available
    if hasattr(vote, 'created_at') and vote.created_at:
        message += f"\n📅 *Voted on:* {vote.created_at.strftime('%Y-%m-%d %H:%M UTC')}"
    elif hasattr(vote, 'voted_at') and vote.voted_at:
        message += f"\n📅 *Voted on:* {vote.voted_at.strftime('%Y-%m-%d %H:%M UTC')}"
    
    message += f"\n📊 *Decision status:* {decision.status.upper()}\n"
    
    return message


def handle_search_command(
    parsed: ParsedCommand,
    user_id: str,
    user_name: str,
    channel_id: str,
    db: Session
) -> Dict[str, Any]:
    """Handle search command - search decisions by keyword."""
    logger.info(f"🔍 Handling SEARCH from {user_name} in {channel_id}")
    
    # Extract search keyword from args
    if not parsed.args or len(parsed.args) == 0:
        logger.warning("❌ No search keyword provided")
        return {
            "text": "❌ Please provide search keyword.\\n\\n*Example:* `/decision search \"postgres\"`",
            "response_type": "ephemeral"
        }
    
    keyword = parsed.args[0].strip()
    
    if not keyword:
        logger.warning("❌ Empty search keyword")
        return {
            "text": "❌ Please provide search keyword.\\n\\n*Example:* `/decision search \"postgres\"`",
            "response_type": "ephemeral"
        }
    
    logger.info(f"🔍 SEARCH Query: keyword='{keyword}', channel={channel_id}")
    
    # Search decisions
    results = crud.search_decisions(db, channel_id, keyword)
    
    # Limit to max 10 results
    MAX_RESULTS = 10
    total_found = len(results)
    results = results[:MAX_RESULTS]
    
    if not results:
        logger.info(f"🔍 No results found for '{keyword}'")
        return {
            "text": f"🔍 No decisions found matching '{keyword}'",
            "response_type": "ephemeral"
        }
    
    # Sort by relevance: exact match first, then by date
    keyword_lower = keyword.lower()
    
    def relevance_score(decision):
        text_lower = decision.text.lower()
        # Exact match gets highest score
        if keyword_lower == text_lower:
            return 3
        # Starts with keyword
        elif text_lower.startswith(keyword_lower):
            return 2
        # Contains keyword
        elif keyword_lower in text_lower:
            return 1
        else:
            return 0
    
    results.sort(key=lambda d: (relevance_score(d), d.created_at), reverse=True)
    
    # Format results
    message = format_search_results(results, keyword, total_found)
    
    return {
        "text": message,
        "response_type": "ephemeral"
    }


def format_search_results(results: List[Decision], keyword: str, total_found: int) -> str:
    """Format search results with context snippets."""
    MAX_SNIPPET_LENGTH = 100
    
    # Header with result count
    if total_found > len(results):
        header = f"🔍 *Found {total_found} results for '{keyword}'* (showing first {len(results)})\\n\\n"
    else:
        header = f"🔍 *Found {total_found} result{'s' if total_found != 1 else ''} for '{keyword}'*\\n\\n"
    
    # Format each result
    result_items = []
    for decision in results:
        status_emoji = DECISION_STATUS_EMOJI.get(decision.status, "❓")
        
        # Create snippet with keyword highlighted
        text = decision.text
        if len(text) > MAX_SNIPPET_LENGTH:
            # Try to center the keyword in the snippet
            keyword_lower = keyword.lower()
            text_lower = text.lower()
            keyword_pos = text_lower.find(keyword_lower)
            
            if keyword_pos != -1:
                # Calculate snippet start/end to center keyword
                snippet_start = max(0, keyword_pos - (MAX_SNIPPET_LENGTH // 2))
                snippet_end = min(len(text), snippet_start + MAX_SNIPPET_LENGTH)
                
                # Adjust start if we're at the end
                if snippet_end == len(text):
                    snippet_start = max(0, snippet_end - MAX_SNIPPET_LENGTH)
                
                snippet = text[snippet_start:snippet_end]
                
                # Add ellipsis
                if snippet_start > 0:
                    snippet = "..." + snippet
                if snippet_end < len(text):
                    snippet = snippet + "..."
            else:
                # Keyword not found (shouldn't happen), just truncate
                snippet = text[:MAX_SNIPPET_LENGTH] + "..."
        else:
            snippet = text
        
        # Format date
        date_str = decision.created_at.strftime('%Y-%m-%d')
        
        # Build result item
        item = f"""*#{decision.id}* {status_emoji} {decision.status.title()}
_{snippet}_
👍 {decision.approval_count} | 👎 {decision.rejection_count} | 📅 {date_str}
"""
        result_items.append(item)
    
    # Join all results
    results_text = "\\n".join(result_items)
    
    # Footer with usage tip
    footer = "\\n💡 *Tip:* Use `/decision show <id>` to view full details"
    
    return header + results_text + footer


def handle_config_command(
    parsed: ParsedCommand,
    user_id: str,
    user_name: str,
    channel_id: str,
    db: Session,
    team_id: str = ""
) -> Dict[str, Any]:
    """
    Handle config command to view or update channel settings.
    Command: /decision config [setting] [value]
    
    Args:
        parsed: Parsed command data
        user_id: Slack user ID
        user_name: User's display name
        channel_id: Slack channel ID
        db: Database session
        team_id: Slack team ID for multi-workspace support
    """
    logger.info(f"⚙️ Handling CONFIG from {user_name} in {channel_id}")
    
    # Get workspace-specific client for API calls
    from ..slack.client import get_client_for_team
    ws_client = get_client_for_team(team_id, db) if team_id else None
    
    # 1. If no args OR first arg is "show", show current config
    if not parsed.args or len(parsed.args) == 0 or (len(parsed.args) == 1 and parsed.args[0].lower() == "show"):
        # Fetch real member count for display using workspace-specific client
        try:
            if ws_client:
                real_count = ws_client.get_channel_members_count(channel_id)
                if isinstance(real_count, int) and real_count > 0:
                    member_count_display = real_count
                else:
                    member_count_display = "Unknown"
            else:
                logger.warning(f"No workspace client available for team {team_id}")
                member_count_display = "Unknown (no workspace client)"
        except Exception as e:
            logger.error(f"Error fetching member count for config: {e}")
            member_count_display = "Unknown"
        
        config = crud.get_channel_config(db, channel_id)
        
        message = f"""⚙️ *Channel Configuration*
        
*Approval Threshold:* {config.approval_percentage}%
*Auto-close Hours:* {config.auto_close_hours}h
*Current Members:* {member_count_display} (fetched dynamically from Slack)

*How to change settings:*
`/decision config approval_percentage 75` - Set approval to 75%
`/decision config auto_close_hours 24` - Set auto-close to 24 hours
"""
        return {
            "text": message,
            "response_type": "ephemeral"
        }
        
    # 2. Parse setting and value
    if len(parsed.args) < 2:
        return {
            "text": "❌ Please provide both a setting name and a value.\n\n*Example:* `/decision config approval_percentage 75`",
            "response_type": "ephemeral"
        }
        
    setting_name = parsed.args[0].lower()
    value_str = parsed.args[1]
    
    # 3. Validate setting name
    # Note: group_size is no longer configurable here - it's always fetched dynamically from Slack
    valid_settings = ["approval_percentage", "auto_close_hours"]
    if setting_name not in valid_settings:
        return {
            "text": f"❌ Invalid setting: `{setting_name}`\n\n*Valid settings:* {', '.join(valid_settings)}\n\n*Note:* Group size is now fetched dynamically from Slack channel members.",
            "response_type": "ephemeral"
        }
        
    # 4. Validate value
    is_valid, error_msg = crud.validate_config_value(setting_name, value_str)
    if not is_valid:
        return {
            "text": f"❌ {error_msg}",
            "response_type": "ephemeral"
        }
        
    # 5. Update config
    try:
        # Convert value to int (validation ensured it's safe)
        value = int(value_str)
        
        update_kwargs = {setting_name: value}
        
        updated_config = crud.update_channel_config(
            db=db,
            channel_id=channel_id,
            updated_by=user_id,
            updated_by_name=user_name,
            **update_kwargs
        )
        
        if updated_config:
            return {
                "text": f"✅ Configuration updated!\n\n*{setting_name}* is now set to *{value}*",
                "response_type": "ephemeral"
            }
        else:
            return {
                "text": "❌ Failed to update configuration. Database error.",
                "response_type": "ephemeral"
            }
            
    except Exception as e:
        logger.error(f"❌ Error updating config: {e}", exc_info=True)
        return {
            "text": f"❌ An error occurred: {str(e)}",
            "response_type": "ephemeral"
        }


# --- FINAL HELP OVERRIDE (appended at EOF) ---
def _help_command_final(parsed: Optional[ParsedCommand] = None, user_id: Optional[str] = None, user_name: Optional[str] = None, channel_id: Optional[str] = None, db: Optional[Session] = None) -> Dict[str, Any]:
    logger.info("📖 Handling HELP command (EOF final override)")
    help_text = """📚 *Decision Agent Help Guide*

*Propose & Create*
• `/decision propose "text"` - Create a new decision
• `/decision add "text"` - Add a pre-approved decision (admin)

*Vote & Participate*
• `/decision approve <id>` - Vote YES
• `/decision reject <id>` - Vote NO

*View & Track*
• `/decision list` - Show active decisions
• `/decision list pending` - Show pending items
• `/decision list approved` - Show approved history
• `/decision show <id>` - See full details and votes
• `/decision search "keyword"` - Search decisions

*AI Insights*
• `/decision summarize <id>` - AI-generated summary of the decision
• `/decision suggest <id>` - AI suggestions for next steps

*Pro Tips*
• Check `/decision myvote <id>` to see your vote.

"""
    return {"text": help_text, "response_type": "ephemeral"}


# Ensure the module symbol points to the final override
handle_help_command = _help_command_final
