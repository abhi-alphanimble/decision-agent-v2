"""
Command Parser for Slack Decision Agent
Parses incoming Slack commands into structured data
"""
from enum import Enum
from typing import Optional, Dict, List, Any, Tuple
from pydantic import BaseModel, Field, ConfigDict
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
    CONFIG = "config"


VALID_CONFIG_SETTINGS = {"approval_percentage", "auto_close_hours", "group_size"}


ACTION_ALIASES: Dict[str, DecisionAction] = {
    # Approve variations
    "approved": DecisionAction.APPROVE,
    "approves": DecisionAction.APPROVE,
    "approving": DecisionAction.APPROVE,
    # Reject variations
    "rejected": DecisionAction.REJECT,
    "rejects": DecisionAction.REJECT,
    "rejecting": DecisionAction.REJECT,
    # List variations
    "listed": DecisionAction.LIST,
    "listing": DecisionAction.LIST,
    # Show variations
    "showed": DecisionAction.SHOW,
    "showing": DecisionAction.SHOW,
    # Myvote variations
    "myvotes": DecisionAction.MYVOTE,
    "myvoted": DecisionAction.MYVOTE,
    # Config variations
    "settings": DecisionAction.CONFIG,
    "configure": DecisionAction.CONFIG,
}


class ParsedCommand(BaseModel):
    """Structured representation of a parsed command"""
    command_type: CommandType
    action: Optional[DecisionAction] = None
    args: List[Any] = Field(default_factory=list)
    flags: Dict[str, bool] = Field(default_factory=dict)
    raw_text: str
    is_valid: bool = True
    error_message: Optional[str] = None
    
    model_config = ConfigDict(use_enum_values=True)


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
    action = resolve_action(action_str)
    if not action:
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
            # Allow handler to validate arguments (supports status, page number, etc.)
            args = remaining_text.strip().split()

    elif action == DecisionAction.SUMMARIZE:
        decision_id = extract_id_from_command(remaining_text)
        if decision_id is not None:
            args = [decision_id]
        # If no ID, args remains empty (implies summarize all/dashboard)
    
    elif action == DecisionAction.SUGGEST:
        # Suggest can operate on a specific decision (by ID) or broadly.
        decision_id = extract_id_from_command(remaining_text)
        if decision_id is not None:
            args = [decision_id]
        # If no ID provided, treat as request for suggestions (empty args)
    
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
    
    elif action == DecisionAction.CONFIG:
        # Parse config subcommand: "show" or "set <key> <value>"
        if not remaining_text:
            return ParsedCommand(
                command_type=CommandType.DECISION,
                action=action,
                raw_text=raw_text,
                is_valid=False,
                error_message='Config requires a subcommand. Example: config show OR config set approval_percentage 70'
            )
        
        config_parts = remaining_text.strip().split()
        if not config_parts:
            return ParsedCommand(
                command_type=CommandType.DECISION,
                action=action,
                raw_text=raw_text,
                is_valid=False,
                error_message='Config requires a subcommand. Example: config show OR config set approval_percentage 70'
            )
        
        subcommand = config_parts[0].lower()
        
        if subcommand == "show":
            args = ["show"]
        elif subcommand == "set":
            result = parse_config_set_arguments(config_parts[1:])
            if not result:
                return ParsedCommand(
                    command_type=CommandType.DECISION,
                    action=action,
                    raw_text=raw_text,
                    is_valid=False,
                    error_message='Config set requires <setting> <value>. Example: config set approval_percentage 70'
                )
            setting_name, value = result
            if setting_name not in VALID_CONFIG_SETTINGS:
                return ParsedCommand(
                    command_type=CommandType.DECISION,
                    action=action,
                    raw_text=raw_text,
                    is_valid=False,
                    error_message=f"Unknown setting: {setting_name}. Valid: {', '.join(sorted(VALID_CONFIG_SETTINGS))}"
                )
            args = [setting_name, normalize_config_value(setting_name, value)]
        elif subcommand in VALID_CONFIG_SETTINGS:
            if len(config_parts) < 2:
                return ParsedCommand(
                    command_type=CommandType.DECISION,
                    action=action,
                    raw_text=raw_text,
                    is_valid=False,
                    error_message=f'Config setting `{subcommand}` requires a value. Example: config {subcommand} 70'
                )
            args = [subcommand, normalize_config_value(subcommand, config_parts[1])]
        elif "=" in subcommand:
            setting_name, value = subcommand.split("=", 1)
            setting_name = setting_name.strip().lower()
            if setting_name not in VALID_CONFIG_SETTINGS or not value.strip():
                return ParsedCommand(
                    command_type=CommandType.DECISION,
                    action=action,
                    raw_text=raw_text,
                    is_valid=False,
                    error_message='Unknown config subcommand. Use: config show OR config set <setting> <value>'
                )
            args = [setting_name, normalize_config_value(setting_name, value)]
        else:
            return ParsedCommand(
                command_type=CommandType.DECISION,
                action=action,
                raw_text=raw_text,
                is_valid=False,
                error_message='Unknown config subcommand. Use: config show OR config set <setting> <value>'
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
    return """*🤖 Decision Agent Help Guide*

Welcome! I help teams make decisions faster and more democratically.

*📝 Propose & Create*
• `/decision propose "text"` - Create a new decision
  _Example: `/decision propose "Should we switch to Python 3.11?"`_
• `/decision add "text"` - Alias for propose

*🗳️ Vote & Participate*
• `/decision approve <id>` - Vote YES
• `/decision reject <id>` - Vote NO
• `/decision approve <id> --anonymous` - Vote anonymously (hidden from others)
• `/decision myvote <id>` - Check how you voted

*📋 View & Track*
• `/decision list` - Show all active decisions
• `/decision list pending` - Show only pending items
• `/decision list approved` - Show approved history
• `/decision show <id>` - See full details and who voted
• `/decision search "keyword"` - Find past decisions

*🧠 AI Insights*
• `/decision summarize <id>` - Get an AI summary of the decision
• `/decision suggest <id>` - Get AI advice on next steps

*⚙️ Configuration (Admin Only)*
• `/decision config show` - View current channel settings
• `/decision config set <setting> <value>` - Update channel settings
  - Available settings: `approval_percentage`, `auto_close_hours`, `group_size`
  - Example: `/decision config set auto_close_hours 72`

*💡 Pro Tips*
• Use `--anonymous` (or `-a`) for sensitive topics.
• You can change your vote anytime while the decision is pending.
• Use `list` to find the ID of a decision.

"""

parse_command = parse_message


def resolve_action(action_str: str) -> Optional[DecisionAction]:
    """
    Resolve an action string (including aliases) to a DecisionAction.
    """
    normalized = action_str.lower()
    if normalized in DecisionAction._value2member_map_:
        return DecisionAction(normalized)
    return ACTION_ALIASES.get(normalized)


def parse_config_set_arguments(parts: List[str]) -> Optional[Tuple[str, str]]:
    """
    Parse the arguments that follow `config set`.
    Supports both `config set key value` and `config set key=value`.
    """
    if not parts:
        return None
    
    first = parts[0]
    # Handle "key=value" as a single token
    if "=" in first:
        key, value = first.split("=", 1)
        key = key.strip().lower()
        value = value.strip()
        if key and value:
            return key, value
        # Allow "config set key= 70"
        if key and len(parts) > 1 and not value:
            return key, parts[1].strip()
        return None
    
    if len(parts) < 2:
        return None
    
    key = first.strip().lower()
    value = parts[1].strip()
    if not key or not value:
        return None
    return key, value


def normalize_config_value(setting_name: str, raw_value: str) -> str:
    """
    Normalize config values before passing them downstream.
    Example: strip '%' for approval percentages.
    """
    value = (raw_value or "").strip()
    if setting_name == "approval_percentage" and value.endswith("%"):
        value = value[:-1].strip()
    return value