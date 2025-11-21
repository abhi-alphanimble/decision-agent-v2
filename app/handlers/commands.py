# app/handlers/commands.py (Assuming this is where the main handlers live)
# You must ensure 'from app import crud' and 'from app.command_parser import parse_command' 
# are correct for your environment.

import logging
from typing import Dict, Any

from sqlalchemy.orm import Session
# Assuming these exist in your project structure
from app import crud 
from app.command_parser import ParsedCommand 
# Assuming you have imports for other handlers (propose, approve, etc.) here

logger = logging.getLogger(__name__)

# --- EXISTING HANDLERS (propose, approve, reject, show, myvote) ---
# ... (Their definitions are assumed to be here) ...


def handle_list_command(parsed: ParsedCommand, user_id: str, user_name: str, channel_id: str, db: Session) -> Dict[str, Any]:
    """
    Handle list command - shows all pending decisions.
    Command: /decision list
    """
    # NOTE: The actual implementation is simplified here; 
    # the full pagination/filtering logic should be in crud/handlers
    logger.info(f"📋 Handling LIST from {user_name} in {channel_id}")
    
    # Get all pending decisions (or filter by channel if crud supports it)
    # The list logic in the original main.py did not filter by channel.
    pending_decisions = crud.get_pending_decisions(db)
    
    if not pending_decisions:
        return {
            "text": "ℹ️ No pending decisions at the moment.\n\nCreate one with `/decision propose \"Your proposal\"`",
            "response_type": "ephemeral"
        }
    
    # Format list
    message = "📋 *Pending Decisions*\n\n"
    
    for decision in pending_decisions:
        message += f"*#{decision.id}* - {decision.text[:80]}{'...' if len(decision.text) > 80 else ''}\n"
        message += f"   👍 {decision.approval_count} approvals • 👎 {decision.rejection_count} rejections\n"
        message += f"   Proposed by: {decision.proposer_name}\n\n"
    
    message += f"\n*Commands:*\n"
    message += f"• `/decision show <id>` - View details\n"
    message += f"• `/decision approve <id>` - Vote to approve\n"
    message += f"• `/decision reject <id>` - Vote to reject\n"
    message += f"• Add `--anonymous` to any vote to keep it private"
    
    return {
        "text": message,
        "response_type": "ephemeral"
    }


def handle_help_command() -> Dict[str, Any]:
    """
    Handle help command - shows all available commands.
    Command: /decision help
    """
    logger.info("📖 Handling HELP command")
    
    help_text = """📚 *Slack Decision Agent - Command Reference*

*Creating Proposals:*
`/decision propose "Your proposal text"`
Create a new decision for the team to vote on.

*Voting Commands:*
`/decision approve <id>` - Vote to approve
`/decision reject <id>` - Vote to reject

*Anonymous Voting:*
`/decision approve <id> --anonymous` - Vote anonymously (long form)
`/decision approve <id> --anon` - Vote anonymously (short form)
`/decision approve <id> -a` - Vote anonymously (shortest form)

*Viewing Decisions:*
`/decision list` - Show all pending decisions
`/decision show <id>` - View decision details with votes
`/decision myvote <id>` - Check your vote on a decision

*Other Commands:*
`/decision help` - Show this help message

*Examples:*
• `/decision propose "Should we order pizza for lunch?"`
• `/decision approve 42`
• `/decision reject 42 --anonymous`
• `/decision show 42`
• `/decision myvote 42`

*Privacy Note:*
🔒 Anonymous votes hide your identity from other users, but you can always check your own vote using `/decision myvote <id>`.

*Questions?*
Contact your workspace admin for assistance.
"""
    
    return {
        "text": help_text,
        "response_type": "ephemeral"
    }