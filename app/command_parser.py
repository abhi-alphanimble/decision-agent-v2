"""
Command Parser for Slack Decision Agent
Parses incoming Slack commands into structured data
"""
from enum import Enum
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
import re
import logging

logger = logging.getLogger(__name__)


class CommandType(str, Enum):
    """Type of command received"""
    DECISION = "decision"
    HELP = "help"
    UNKNOWN = "unknown"


class DecisionAction(str, Enum):
    """Specific action within decision command"""
    PROPOSE = "propose"
    APPROVE = "approve"
    REJECT = "reject"
    ADD = "add"
    LIST = "list"
    SEARCH = "search"
    SHOW = "show"
    MYVOTE = "myvote"
    SUMMARIZE = "summarize"
    SUGGEST = "suggest"


class ParsedCommand(BaseModel):
    """Structured representation of a parsed command"""
    command_type: CommandType
    action: Optional[DecisionAction] = None
    args: List[Any] = Field(default_factory=list)
    flags: Dict[str, bool] = Field(default_factory=dict)
    raw_text: str
    is_valid: bool = True
    error_message: Optional[str] = None
    
    class Config:
        use_enum_values = True


def extract_quoted_text(text: str) -> Optional[str]:
    """Extract text within quotes (single or double)."""
    if not text:
        return None
    
    # Try double quotes first
    double_quote_pattern = r'"((?:[^"\\]|\\.)*)"'
    match = re.search(double_quote_pattern, text)
    if match:
        extracted = match.group(1)
        extracted = extracted.replace('\\"', '"')
        extracted = extracted.replace("\\'", "'")
        return extracted.strip()
    
    # Try single quotes
    single_quote_pattern = r"'((?:[^'\\]|\\.)*)'"
    match = re.search(single_quote_pattern, text)
    if match:
        extracted = match.group(1)
        extracted = extracted.replace("\\'", "'")
        extracted = extracted.replace('\\"', '"')
        return extracted.strip()
    
    return None


def extract_id_from_command(text: str) -> Optional[int]:
    """Extract numeric ID from command text."""
    match = re.search(r'\b(\d+)\b', text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def parse_flags(text: str) -> Dict[str, bool]:
    """
    Parse command flags including aliases.
    Supports: --anonymous, --anon, -a
    """
    flags = {}
    
    # Long form flags (--flag-name)
    long_flag_pattern = r'--(\w+)'
    matches = re.findall(long_flag_pattern, text)
    
    for flag_name in matches:
        normalized = flag_name.lower()
        # Normalize aliases to 'anonymous'
        if normalized in ['anonymous', 'anon']:
            flags['anonymous'] = True
        else:
            flags[normalized] = True
    
    # Short form flags (-a)
    short_flag_pattern = r'\s-([a-zA-Z])\b'
    short_matches = re.findall(short_flag_pattern, text)
    
    for flag_char in short_matches:
        # Map single character flags
        if flag_char.lower() == 'a':
            flags['anonymous'] = True
        else:
            flags[flag_char.lower()] = True
    
    return flags


def parse_message(text: str) -> ParsedCommand:
    """Parse incoming message text into structured command."""
    text = text.strip()
    
    if not text:
        return ParsedCommand(
            command_type=CommandType.UNKNOWN,
            raw_text=text,
            is_valid=False,
            error_message="Empty command"
        )
    
    raw_text = text
    flags = parse_flags(text)
    
    # Remove flags from text
    text_without_flags = re.sub(r'--\w+', '', text)  # Remove long flags
    text_without_flags = re.sub(r'\s-[a-zA-Z]\b', '', text_without_flags)  # Remove short flags
    text_without_flags = text_without_flags.strip()
    
    parts = text_without_flags.split(maxsplit=1)
    
    if not parts:
        return ParsedCommand(
            command_type=CommandType.UNKNOWN,
            raw_text=raw_text,
            is_valid=False,
            error_message="No command found"
        )
    
    action_str = parts[0].lower()
    remaining_text = parts[1] if len(parts) > 1 else ""
    
    # Check for help
    if action_str in ["help", "h", "?"]:
        return ParsedCommand(
            command_type=CommandType.HELP,
            raw_text=raw_text,
            args=[],
            flags=flags
        )
    
    # Try to match decision action
    try:
        action = DecisionAction(action_str)
    except ValueError:
        return ParsedCommand(
            command_type=CommandType.UNKNOWN,
            raw_text=raw_text,
            is_valid=False,
            error_message=f"Unknown action: '{action_str}'. Valid: {', '.join([a.value for a in DecisionAction])}"
        )
    
    # Parse arguments based on action
    args = []
    
    if action == DecisionAction.PROPOSE:
        quoted_text = extract_quoted_text(remaining_text)
        if quoted_text:
            args = [quoted_text]
        else:
            return ParsedCommand(
                command_type=CommandType.DECISION,
                action=action,
                raw_text=raw_text,
                is_valid=False,
                error_message='Propose requires quoted text. Example: propose "Should we order pizza?"'
            )
    
    elif action in [DecisionAction.APPROVE, DecisionAction.REJECT, DecisionAction.SHOW, DecisionAction.MYVOTE]:
        decision_id = extract_id_from_command(remaining_text)
        if decision_id is not None:
            args = [decision_id]
        else:
            return ParsedCommand(
                command_type=CommandType.DECISION,
                action=action,
                raw_text=raw_text,
                is_valid=False,
                error_message=f'{action.value.capitalize()} requires a decision ID. Example: {action.value} 42'
            )
    
    elif action == DecisionAction.SEARCH:
        quoted_text = extract_quoted_text(remaining_text)
        if quoted_text:
            args = [quoted_text]
        elif remaining_text:
            args = [remaining_text.strip()]
        else:
            return ParsedCommand(
                command_type=CommandType.DECISION,
                action=action,
                raw_text=raw_text,
                is_valid=False,
                error_message='Search requires a keyword. Example: search "pizza"'
            )
    
    elif action == DecisionAction.LIST:
        if remaining_text:
            status = remaining_text.strip().lower()
            if status in ["pending", "approved", "rejected", "expired"]:
                args = [status]
            else:
                return ParsedCommand(
                    command_type=CommandType.DECISION,
                    action=action,
                    raw_text=raw_text,
                    is_valid=False,
                    error_message=f'Invalid status: "{status}". Valid: pending, approved, rejected, expired'
                )
    
    elif action in [DecisionAction.SUMMARIZE, DecisionAction.SUGGEST]:
        pass
    
    elif action == DecisionAction.ADD:
        quoted_text = extract_quoted_text(remaining_text)
        if quoted_text:
            args = [quoted_text]
        else:
            return ParsedCommand(
                command_type=CommandType.DECISION,
                action=action,
                raw_text=raw_text,
                is_valid=False,
                error_message='Add requires quoted text. Example: add "Should we have a meeting?"'
            )
    
    return ParsedCommand(
        command_type=CommandType.DECISION,
        action=action,
        args=args,
        flags=flags,
        raw_text=raw_text,
        is_valid=True
    )


def get_help_text() -> str:
    """Get help text for available commands"""
    return """*Decision Agent Commands:*

📝 *Creating Decisions:*
- `propose "decision text"` - Create a new decision
- `add "decision text"` - Same as propose

🗳️ *Voting:*
- `approve <id>` - Vote to approve a decision
- `reject <id>` - Vote to reject a decision
- `approve <id> --anonymous` - Vote anonymously (long form)
- `approve <id> --anon` - Vote anonymously (short form)
- `approve <id> -a` - Vote anonymously (shortest form)
- `myvote <id>` - Check your vote on a decision

📋 *Viewing Decisions:*
- `list` - List all pending decisions
- `list pending` - List pending decisions
- `list approved` - List approved decisions
- `list rejected` - List rejected decisions
- `show <id>` - Show details of a specific decision
- `search "keyword"` - Search decisions

📊 *Analysis:*
- `summarize` - Get summary of all decisions
- `suggest` - Get AI suggestions

❓ *Help:*
- `help` - Show this help message

*Examples:*
- `/decision propose "Should we order lunch?"`
- `/decision approve 42`
- `/decision reject 42 --anonymous`
- `/decision approve 42 -a`
- `/decision list pending`
- `/decision myvote 42`

*Privacy:*
🔒 Anonymous votes hide your identity from others, but you can always check your own vote with `myvote`.
"""