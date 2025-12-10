"""
Workspace and team management utilities.
"""
from sqlalchemy.orm import Session
from typing import Optional, TYPE_CHECKING

from ..config import get_context_logger
from ..models import SlackInstallation
from ..utils.encryption import encrypt_token, decrypt_token

if TYPE_CHECKING:
    from ..slack.client import WorkspaceSlackClient

logger = get_context_logger(__name__)


def get_workspace_token(db: Session, team_id: str) -> Optional[str]:
    """
    Get the decrypted bot access token for a Slack workspace.
    
    Args:
        db: Database session
        team_id: Slack team/workspace ID
    
    Returns:
        Decrypted bot access token or None if not found
    """
    try:
        installation = db.query(SlackInstallation).filter(
            SlackInstallation.team_id == team_id
        ).first()
        
        if installation:
            return decrypt_token(installation.access_token)
        
        logger.warning(f"No workspace token found for team {team_id}")
        return None
    except Exception as e:
        logger.error(f"Error fetching workspace token: {e}")
        return None


def get_slack_client_for_team(db: Session, team_id: str) -> Optional["WorkspaceSlackClient"]:
    """
    Get a Slack client for a specific workspace.
    
    Args:
        db: Database session
        team_id: Slack team/workspace ID
    
    Returns:
        WorkspaceSlackClient or None if token not found
    """
    from ..slack.client import get_client_for_team
    return get_client_for_team(team_id, db)


def save_installation(
    db: Session,
    team_id: str,
    team_name: str,
    access_token: str,
    bot_user_id: str
) -> SlackInstallation:
    """
    Save or update a Slack workspace installation.
    
    Tokens are encrypted before storage.
    
    Args:
        db: Database session
        team_id: Slack team ID
        team_name: Slack team name
        access_token: Bot access token (will be encrypted)
        bot_user_id: Bot user ID
        
    Returns:
        The saved SlackInstallation record
    """
    from ..utils import get_utc_now
    
    # Encrypt the token before storage
    encrypted_token = encrypt_token(access_token)
    
    # Check if installation already exists
    installation = db.query(SlackInstallation).filter(
        SlackInstallation.team_id == team_id
    ).first()
    
    if installation:
        # Update existing installation
        installation.access_token = encrypted_token
        installation.bot_user_id = bot_user_id
        installation.team_name = team_name
        installation.installed_at = get_utc_now()
        logger.info(f"🔄 Updated existing installation for {team_name}")
    else:
        # Create new installation
        installation = SlackInstallation(
            team_id=team_id,
            team_name=team_name,
            access_token=encrypted_token,
            bot_user_id=bot_user_id
        )
        db.add(installation)
        logger.info(f"✨ Created new installation for {team_name}")
    
    db.commit()
    db.refresh(installation)
    return installation


def remove_installation(db: Session, team_id: str) -> bool:
    """
    Remove a workspace installation (on app uninstall).
    
    Args:
        db: Database session
        team_id: Slack team ID to remove
        
    Returns:
        True if removed, False if not found
    """
    installation = db.query(SlackInstallation).filter(
        SlackInstallation.team_id == team_id
    ).first()
    
    if installation:
        db.delete(installation)
        db.commit()
        logger.info(f"🗑️ Removed installation for team {team_id}")
        return True
    
    logger.warning(f"No installation found for team {team_id} to remove")
    return False


def get_all_installations(db: Session) -> list[SlackInstallation]:
    """
    Get all workspace installations.
    
    Useful for batch operations like sending announcements.
    
    Args:
        db: Database session
        
    Returns:
        List of all SlackInstallation records
    """
    return db.query(SlackInstallation).all()


def get_installation(db: Session, team_id: str) -> Optional[SlackInstallation]:
    """
    Get a specific workspace installation.
    
    Args:
        db: Database session
        team_id: Slack team ID
        
    Returns:
        SlackInstallation or None
    """
    return db.query(SlackInstallation).filter(
        SlackInstallation.team_id == team_id
    ).first()


def is_workspace_installed(db: Session, team_id: str) -> bool:
    """
    Check if a workspace has the app installed.
    
    Args:
        db: Database session
        team_id: Slack team ID
        
    Returns:
        True if installed, False otherwise
    """
    return get_installation(db, team_id) is not None
