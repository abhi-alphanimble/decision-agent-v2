"""
Common utility functions for the application.
"""
from datetime import datetime, UTC
from typing import Tuple


def get_utc_now() -> datetime:
    """Get current UTC time as timezone-aware datetime."""
    return datetime.now(UTC)


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length, adding ellipsis if truncated.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
    
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def extract_decision_id(text: str) -> int:
    """
    Extract decision ID from text (e.g., "vote 123" -> 123).
    
    Args:
        text: Input text containing decision ID
    
    Returns:
        Decision ID as integer, or 0 if not found
    """
    parts = text.strip().split()
    for part in parts:
        if part.isdigit():
            return int(part)
    return 0


def check_admin_permission(
    user_id: str,
    channel_id: str,
    team_id: str
) -> bool:
    """
    Check if a user has admin permissions in a channel.
    
    Args:
        user_id: Slack user ID
        channel_id: Slack channel ID
        team_id: Slack team/workspace ID
    
    Returns:
        True if user is admin, False otherwise
    """
    try:
        # Import inside function to avoid circular imports
        from ..slack.client import get_client_for_team
        
        # Get channel info
        sc = get_client_for_team(team_id)
        if not sc:
            return False
        
        channel_info = sc.conversations_info(channel=channel_id)
        is_creator = channel_info.get('channel', {}).get('creator') == user_id
        
        # Get user info
        user_info = sc.users_info(user=user_id)
        is_admin = user_info.get('user', {}).get('is_admin', False)
        is_owner = user_info.get('user', {}).get('is_owner', False)
        
        return is_admin or is_owner or is_creator
    except Exception:
        return False