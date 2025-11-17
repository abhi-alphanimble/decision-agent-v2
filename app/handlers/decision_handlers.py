"""
Handlers for decision-related commands
"""
from sqlalchemy.orm import Session
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app import crud
from app.command_parser import ParsedCommand
from app.slack_client import slack_client
from app.display import format_vote_summary, display_vote_list
from app.models import Decision # Import Decision model for type hinting
from app.utils import truncate_text # NEW: Import the utility function

logger = logging.getLogger(__name__)

# MVP Hardcoded values
MVP_GROUP_SIZE = 5
MVP_APPROVAL_THRESHOLD = 2  # Example value

# Helper constants
DECISION_STATUS_EMOJI = {
    "pending": "⏳",
    "approved": "✅",
    "rejected": "❌",
    "expired": "⌛",
}
DECISIONS_PER_PAGE = 10 # Pagination limit

# ============================================================================
# DECISION COMMAND HANDLERS
# ============================================================================

def handle_propose_command(
    parsed: ParsedCommand,
    user_id: str,
    user_name: str,
    channel_id: str,
    db: Session
) -> Dict[str, Any]:
    """
    Handle proposal command.
    """
    logger.info(f"📝 Handling PROPOSE from {user_name} in {channel_id}")
    
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
        decision = crud.create_decision(
            db=db,
            channel_id=channel_id,
            text=proposal_text,
            created_by=user_id,
            created_by_name=user_name,
            group_size_at_creation=MVP_GROUP_SIZE,
            approval_threshold=MVP_APPROVAL_THRESHOLD
        )
        
        logger.info(f"✅ Created decision #{decision.id} by {user_name}: '{proposal_text[:50]}...'")
        
        # Format success message
        response_text = format_proposal_success_message(decision)
        
        # Send to channel
        try:
            slack_client.send_message(
                channel=channel_id,
                text=response_text
            )
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


def handle_approve_command(
    parsed: ParsedCommand,
    user_id: str,
    user_name: str,
    channel_id: str,
    db: Session
) -> Dict[str, Any]:
    """
    Handle approval vote command.
    Command: /decision approve <decision_id> [--anonymous|--anon|-a]
    """
    logger.info(f"👍 Handling APPROVE from {user_name} in {channel_id}")
    
    # 1. Extract decision_id
    if not parsed.args or len(parsed.args) == 0:
        logger.warning("❌ No decision ID provided")
        return {
            "text": "❌ Please provide a decision ID.\n\n*Example:* `/decision approve 42`\n*Anonymous:* `/decision approve 42 --anonymous`",
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
    
    # 2. Check if vote is anonymous (support --anonymous, --anon, -a)
    is_anonymous = parsed.flags.get("anonymous", False)
    logger.info(f"🔒 Anonymous vote: {is_anonymous}")
    
    # 3. Get decision from database
    decision = crud.get_decision_by_id(db, decision_id)
    
    if not decision:
        logger.warning(f"❌ Decision #{decision_id} not found")
        return {
            "text": f"❌ Decision #{decision_id} not found.\n\nUse `/decision list` to see available decisions.",
            "response_type": "ephemeral"
        }
    
    # 4. Check if decision is still pending
    if decision.status != "pending":
        logger.warning(f"❌ Decision #{decision_id} is {decision.status}")
        return {
            "text": f"❌ Decision #{decision_id} is already *{decision.status.upper()}*.\n\nYou can only vote on pending decisions.",
            "response_type": "ephemeral"
        }
    
    # 5. Check if user already voted
    if crud.check_if_user_voted(db, decision_id, user_id):
        logger.warning(f"❌ User {user_name} already voted on #{decision_id}")
        
        # Get their existing vote
        existing_vote = crud.get_user_vote(db, decision_id, user_id)
        vote_type = existing_vote.vote_type if existing_vote else "unknown"
        
        return {
            "text": f"❌ You already voted on this decision.\n\n*Your vote:* {vote_type.upper()}\n*Decision:* {decision.text[:100]}...\n\n💡 Use `/decision myvote {decision_id}` to see your vote details.",
            "response_type": "ephemeral"
        }
    
    # 6. Create vote and update counts atomically
    success, message, updated_decision = crud.vote_on_decision(
        db=db,
        decision_id=decision_id,
        voter_id=user_id,
        voter_name=user_name,
        vote_type="approve",
        is_anonymous=is_anonymous
    )
    
    if not success:
        logger.error(f"❌ Vote failed: {message}")
        return {
            "text": message,
            "response_type": "ephemeral"
        }
    
    logger.info(f"✅ Vote recorded: User {user_id} {'anonymously ' if is_anonymous else ''}approved #{decision_id}")
    
    # 7. Format confirmation message
    confirmation = format_vote_confirmation(updated_decision, "approve", is_anonymous, user_id)
    
    # 8. Check if decision was closed
    if updated_decision.status == "approved":
        logger.info(f"🎉 Decision #{decision_id} APPROVED!")
        
        # Send channel notification
        try:
            channel_message = format_decision_approved_message(updated_decision, db)
            slack_client.send_message(
                channel=channel_id,
                text=channel_message
            )
            logger.info(f"✅ Sent approval notification to channel {channel_id}")
        except Exception as e:
            logger.error(f"❌ Error sending approval notification: {e}")
    
    # 9. Return confirmation to user
    return {
        "text": confirmation,
        "response_type": "ephemeral"
    }


def handle_reject_command(
    parsed: ParsedCommand,
    user_id: str,
    user_name: str,
    channel_id: str,
    db: Session
) -> Dict[str, Any]:
    """
    Handle rejection vote command.
    Command: /decision reject <decision_id> [--anonymous|--anon|-a]
    """
    logger.info(f"👎 Handling REJECT from {user_name} in {channel_id}")
    
    # 1. Extract decision_id
    if not parsed.args or len(parsed.args) == 0:
        logger.warning("❌ No decision ID provided")
        return {
            "text": "❌ Please provide a decision ID.\n\n*Example:* `/decision reject 42`\n*Anonymous:* `/decision reject 42 --anonymous`",
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
    
    # 2. Check if vote is anonymous (support --anonymous, --anon, -a)
    is_anonymous = parsed.flags.get("anonymous", False)
    logger.info(f"🔒 Anonymous vote: {is_anonymous}")
    
    # 3. Get decision from database
    decision = crud.get_decision_by_id(db, decision_id)
    
    if not decision:
        logger.warning(f"❌ Decision #{decision_id} not found")
        return {
            "text": f"❌ Decision #{decision_id} not found.\n\nUse `/decision list` to see available decisions.",
            "response_type": "ephemeral"
        }
    
    # 4. Check if decision is still pending
    if decision.status != "pending":
        logger.warning(f"❌ Decision #{decision_id} is {decision.status}")
        return {
            "text": f"❌ Decision #{decision_id} is already *{decision.status.upper()}*.\n\nYou can only vote on pending decisions.",
            "response_type": "ephemeral"
        }
    
    # 5. Check if user already voted
    if crud.check_if_user_voted(db, decision_id, user_id):
        logger.warning(f"❌ User {user_name} already voted on #{decision_id}")
        
        # Get their existing vote
        existing_vote = crud.get_user_vote(db, decision_id, user_id)
        vote_type = existing_vote.vote_type if existing_vote else "unknown"
        
        return {
            "text": f"❌ You already voted on this decision.\n\n*Your vote:* {vote_type.upper()}\n*Decision:* {decision.text[:100]}...\n\n💡 Use `/decision myvote {decision_id}` to see your vote details.",
            "response_type": "ephemeral"
        }
    
    # 6. Create vote and update counts atomically
    success, message, updated_decision = crud.vote_on_decision(
        db=db,
        decision_id=decision_id,
        voter_id=user_id,
        voter_name=user_name,
        vote_type="reject",
        is_anonymous=is_anonymous
    )
    
    if not success:
        logger.error(f"❌ Vote failed: {message}")
        return {
            "text": message,
            "response_type": "ephemeral"
        }
    
    logger.info(f"✅ Vote recorded: User {user_id} {'anonymously ' if is_anonymous else ''}rejected #{decision_id}")
    
    # 7. Format confirmation message
    confirmation = format_vote_confirmation(updated_decision, "reject", is_anonymous, user_id)
    
    # 8. Check if decision was closed
    if updated_decision.status == "rejected":
        logger.info(f"❌ Decision #{decision_id} REJECTED!")
        
        # Send channel notification
        try:
            channel_message = format_decision_rejected_message(updated_decision, db)
            slack_client.send_message(
                channel=channel_id,
                text=channel_message
            )
            logger.info(f"✅ Sent rejection notification to channel {channel_id}")
        except Exception as e:
            logger.error(f"❌ Error sending rejection notification: {e}")
    
    # 9. Return confirmation to user
    return {
        "text": confirmation,
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
    Shows full decision details with vote list (respecting anonymity).
    """
    logger.info(f"📋 Handling SHOW from {user_name} in {channel_id}")
    
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
    Shows user their own vote (even if anonymous to others).
    """
    logger.info(f"🔍 Handling MYVOTE from {user_name} in {channel_id}")
    
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
            "text": f"ℹ️ You haven't voted on decision #{decision_id} yet.\n\n*Decision:* {decision.text}\n\n*How to vote:*\n- `/decision approve {decision_id}` - Vote to approve\n- `/decision reject {decision_id}` - Vote to reject\n- Add `--anonymous` to vote anonymously",
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
    logger.info(f"📋 Handling LIST in {channel_id}")
    
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
        
        # If we got here, page is already set, so skip to step 3.
        pass


    # 2. Parse optional page number (default to 1) if not already parsed
    if 'page' not in locals():
        page = 1
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
- `/decision approve {decision.id} --anonymous` - Vote anonymously

💡 *Tip:* Use `/decision show {decision.id}` to see details anytime
"""


def format_vote_confirmation(decision, vote_type: str, is_anonymous: bool, user_id: str) -> str:
    """Format vote confirmation message."""
    emoji = "✅" if vote_type == "approve" else "❌"
    vote_word = "approved" if vote_type == "approve" else "rejected"
    anon_text = " anonymously" if is_anonymous else ""
    
    message = f"""{emoji} *Vote Recorded{anon_text}*

You voted to *{vote_word}* this decision{anon_text}:
"{decision.text}"

📊 *Current Status:*
- ✅ Approvals: {decision.approval_count}/{decision.approval_threshold}
- ❌ Rejections: {decision.rejection_count}/{decision.approval_threshold}
- 📈 Status: {decision.status.upper()}
"""
    
    if decision.status == "pending":
        remaining = decision.approval_threshold - max(decision.approval_count, decision.rejection_count)
        message += f"\n💡 *{remaining} more vote(s) needed to close this decision*"
    
    if is_anonymous:
        message += f"\n\n🔒 Your vote is anonymous - your identity won't be shown to others."
    
    message += f"\n\n💡 Use `/decision myvote {decision.id}` to check your vote anytime"
    
    return message


def format_decision_approved_message(decision, db: Session) -> str:
    """Format message when decision is approved."""
    # Get votes to show who voted (respecting anonymity)
    votes = crud.get_votes_by_decision(db, decision.id)
    vote_summary = format_vote_summary(votes)
    
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
    # Get votes to show who voted (respecting anonymity)
    votes = crud.get_votes_by_decision(db, decision.id)
    vote_summary = format_vote_summary(votes)
    
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
    Respects vote anonymity.
    """
    # Status emoji
    status_emoji = {
        "pending": "⏳",
        "approved": "✅",
        "rejected": "❌"
    }.get(decision.status, "❓")
    
    # Format vote summary
    vote_summary = format_vote_summary(votes)
    
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
        message += f"\n\n*How to vote:*\n- `/decision approve {decision.id}` - Vote to approve\n- `/decision reject {decision.id}` - Vote to reject\n- Add `--anonymous` to vote anonymously"
    
    return message


def format_user_vote_detail(vote, decision) -> str:
    """
    Format user's own vote details.
    Shows everything including anonymity status.
    """
    vote_emoji = "👍" if vote.vote_type == "approve" else "👎"
    vote_text = "approved" if vote.vote_type == "approve" else "rejected"
    anonymity_status = "🔒 Anonymous vote" if vote.is_anonymous else "👤 Public vote"
    
    message = f"""*Your Vote on Decision #{decision.id}*

*Decision:*
{decision.text}

{vote_emoji} You {vote_text} this decision
{anonymity_status}
"""
    
    # Add timestamp if available
    if hasattr(vote, 'created_at') and vote.created_at:
        message += f"\n📅 *Voted on:* {vote.created_at.strftime('%Y-%m-%d %H:%M UTC')}"
    elif hasattr(vote, 'voted_at') and vote.voted_at:
        message += f"\n📅 *Voted on:* {vote.voted_at.strftime('%Y-%m-%d %H:%M UTC')}"
    
    message += f"\n📊 *Decision status:* {decision.status.upper()}\n"
    
    if vote.is_anonymous:
        message += "\n🔒 Your identity is hidden from other users"
    else:
        message += "\n👤 Your vote is visible to other users"
    
    return message