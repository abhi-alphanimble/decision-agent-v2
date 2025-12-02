# app/utils.py
import logging
from datetime import datetime, UTC
from typing import Optional
from app.slack_client import slack_client

logger = logging.getLogger(__name__)


def get_utc_now() -> datetime:
    """Get current UTC datetime (replacement for deprecated datetime.utcnow())."""
    return datetime.now(UTC)


def truncate_text(text: str, max_length: int = 50, ellipsis: str = "...") -> str:
    """
    Truncates a string to max_length and appends ellipsis if truncated.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + ellipsis


def check_admin_permission(user_id: str) -> bool:
    """
    Check if a user is a Slack workspace admin.
    
    Args:
        user_id: Slack user ID
        
    Returns:
        True if user is admin, False otherwise
    """
    try:
        if not slack_client:
            logger.error("Slack client not available for admin check")
            return False
        
        # Call users.info API to get user details
        response = slack_client.client.users_info(user=user_id)
        
        if not response["ok"]:
            logger.error(f"Failed to get user info for {user_id}: {response.get('error')}")
            return False
        
        user = response["user"]
        
        # Check if user is admin or owner
        is_admin = user.get("is_admin", False)
        is_owner = user.get("is_owner", False)
        is_primary_owner = user.get("is_primary_owner", False)
        
        return is_admin or is_owner or is_primary_owner
        
    except Exception as e:
        logger.error(f"Error checking admin permission for {user_id}: {e}")
        return False