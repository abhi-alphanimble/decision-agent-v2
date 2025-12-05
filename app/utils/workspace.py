"""
Workspace and team management utilities.
"""
from sqlalchemy.orm import Session
from typing import Optional
from ..config import get_context_logger
from ..models import SlackInstallation

logger = get_context_logger(__name__)


def get_workspace_token(db: Session, team_id: str) -> Optional[str]:
    """
    Get the bot access token for a Slack workspace.
    
    Args:
        db: Database session
        team_id: Slack team/workspace ID
    
    Returns:
        Bot access token or None if not found
    """
    try:
        installation = db.query(SlackInstallation).filter(
            SlackInstallation.team_id == team_id
        ).first()
        
        if installation:
            return installation.access_token
        
        logger.warning(f"No workspace token found for team {team_id}")
        return None
    except Exception as e:
        logger.error(f"Error fetching workspace token: {e}")
        return None


def get_slack_client_for_team(db: Session, team_id: str) -> Optional[object]:
    """
    Get a Slack WebClient for a specific workspace.
    
    Args:
        db: Database session
        team_id: Slack team/workspace ID
    
    Returns:
        Slack WebClient or None if token not found
    """
    # Import inside function to avoid circular imports
    from ..slack.client import get_client_for_team
    
    token = get_workspace_token(db, team_id)
    if token:
        return get_client_for_team(team_id)
    return None


def get_team_id_from_channel(db: Session, channel_id: str) -> Optional[str]:
    """
    Determine team_id from a channel_id (placeholder implementation).
    In a real multi-workspace setup, this would lookup channel membership.
    
    Args:
        db: Database session
        channel_id: Slack channel ID
    
    Returns:
        Team ID or None if not found
    """
    try:
        # In a full implementation, this would:
        # 1. Check a channel-to-team mapping
        # 2. Query Slack API if needed
        # For now, return None - caller should provide team_id
        return None
    except Exception as e:
        logger.error(f"Error getting team_id from channel: {e}")
        return None
