"""
Helper functions for Slack workspace management
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session
from slack_sdk import WebClient

from app.models import SlackInstallation
from app.config import config

logger = logging.getLogger(__name__)


def get_workspace_token(db: Session, team_id: str) -> Optional[str]:
    """
    Get the bot token for a specific workspace.
    
    Args:
        db: Database session
        team_id: Slack team/workspace ID
        
    Returns:
        Bot token string or None if not found
    """
    installation = db.query(SlackInstallation).filter(
        SlackInstallation.team_id == team_id
    ).first()
    
    if installation:
        return installation.access_token
    
    logger.warning(f"No installation found for team_id: {team_id}")
    return None


def get_slack_client_for_team(db: Session, team_id: str) -> Optional[WebClient]:
    """
    Get a Slack WebClient configured for a specific workspace.
    
    Args:
        db: Database session
        team_id: Slack team/workspace ID
        
    Returns:
        WebClient instance or None if token not found
    """
    token = get_workspace_token(db, team_id)
    
    if token:
        return WebClient(token=token)
    
    # Fallback to default token from config
    logger.warning(f"Using fallback token from config for team_id: {team_id}")
    return WebClient(token=config.SLACK_BOT_TOKEN)


def get_team_id_from_channel(channel_id: str) -> Optional[str]:
    """
    Extract team ID from channel ID if possible.
    
    Note: This is a placeholder. In practice, you might need to:
    1. Store team_id with each decision in the database
    2. Call Slack API to get channel info
    3. Use a different approach based on your architecture
    
    For now, returns None and relies on fallback token.
    """
    # TODO: Implement proper team_id extraction
    return None
