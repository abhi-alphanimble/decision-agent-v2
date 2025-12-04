"""
Slack event and command parsing utilities.
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

def parse_slash_command(payload: Dict) -> Dict:
    """
    Parse Slack slash command payload.
    
    Args:
        payload: Slash command payload from Slack
        
    Returns:
        Parsed command data
    """
    command = payload.get('command', '')
    text = payload.get('text', '').strip()
    user_id = payload.get('user_id', '')
    user_name = payload.get('user_name', '')
    channel_id = payload.get('channel_id', '')
    channel_name = payload.get('channel_name', '')
    response_url = payload.get('response_url', '')
    
    # Parse subcommand and arguments
    parts = text.split(maxsplit=1)
    subcommand = parts[0].lower() if parts else ''
    arguments = parts[1] if len(parts) > 1 else ''
    
    # Extract quoted text if present
    quoted_text = None
    if '"' in arguments:
        try:
            start = arguments.index('"')
            end = arguments.index('"', start + 1)
            quoted_text = arguments[start + 1:end]
        except ValueError:
            pass
    
    return {
        'command': command,
        'subcommand': subcommand,
        'arguments': arguments,
        'quoted_text': quoted_text,
        'user_id': user_id,
        'user_name': user_name,
        'channel_id': channel_id,
        'channel_name': channel_name,
        'response_url': response_url,
        'raw_text': text
    }

def parse_event_message(event: Dict) -> Optional[Dict]:
    """
    Parse Slack event (message) payload.
    
    Args:
        event: Event data from Slack
        
    Returns:
        Parsed message data or None if not a valid message
    """
    event_type = event.get('type', '')
    
    if event_type not in ['message', 'app_mention']:
        return None
    
    text = event.get('text', '')
    user = event.get('user', '')
    channel = event.get('channel', '')
    ts = event.get('ts', '')
    thread_ts = event.get('thread_ts', ts)
    
    # Check if bot is mentioned
    bot_mentioned = '<@' in text
    
    return {
        'type': event_type,
        'text': text,
        'user': user,
        'channel': channel,
        'ts': ts,
        'thread_ts': thread_ts,
        'bot_mentioned': bot_mentioned
    }

def parse_member_event(event: Dict) -> Optional[Dict]:
    """
    Parse Slack member event (member_joined_channel, member_left_channel).
    
    Args:
        event: Event data from Slack
        
    Returns:
        Parsed member event data or None if not a valid member event
    """
    event_type = event.get('type', '')
    
    if event_type not in ['member_joined_channel', 'member_left_channel']:
        return None
    
    user_id = event.get('user', '')
    channel_id = event.get('channel', '')
    team_id = event.get('team', '')
    event_ts = event.get('event_ts', '')
    
    return {
        'type': event_type,
        'user_id': user_id,
        'channel_id': channel_id,
        'team_id': team_id,
        'event_ts': event_ts
    }

def extract_command_from_mention(text: str, bot_user_id: str) -> Optional[str]:
    """
    Extract command from a message that mentions the bot.
    
    Args:
        text: Message text
        bot_user_id: Bot's user ID
        
    Returns:
        Command text without the mention, or None
    """
    mention = f'<@{bot_user_id}>'
    if mention in text:
        # Remove mention and clean up
        command = text.replace(mention, '').strip()
        return command
    return None

def format_decision_message(decision_text: str, proposer_name: str, decision_id: int) -> Dict:
    """
    Format a decision proposal message with interactive buttons.
    
    Args:
        decision_text: The decision text
        proposer_name: Name of person who proposed
        decision_id: Database ID of decision
        
    Returns:
        Slack Block Kit formatted message
    """
    return {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🗳️ New Decision Proposal"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{decision_text}*\n\nProposed by: {proposer_name}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Cast your vote:"
                }
            },
            {
                "type": "actions",
                "block_id": f"decision_{decision_id}",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✅ Approve"
                        },
                        "style": "primary",
                        "value": f"approve_{decision_id}",
                        "action_id": "vote_approve"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "❌ Reject"
                        },
                        "style": "danger",
                        "value": f"reject_{decision_id}",
                        "action_id": "vote_reject"
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Decision ID: {decision_id} | Votes: 0 approve, 0 reject"
                    }
                ]
            }
        ]
    }
