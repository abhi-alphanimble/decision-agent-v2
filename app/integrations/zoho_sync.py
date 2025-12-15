"""
Zoho CRM sync utilities for Decision Agent.
Handles syncing decisions and votes to Zoho CRM with multi-tenant support.

Each team's data is synced to their own Zoho CRM account.
"""
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models import Decision
from .zoho_crm import ZohoCRMClient

logger = logging.getLogger(__name__)


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime to ISO string for Zoho API (without microseconds)"""
    if dt is None:
        return None
    # Format as ISO datetime without microseconds: 2025-12-09T14:02:06
    return dt.strftime('%Y-%m-%dT%H:%M:%S')


def map_decision_to_zoho(decision: Decision, channel_name: Optional[str] = None) -> dict:
    """
    Map Decision model to Zoho CRM field names.
    Returns a dictionary ready for Zoho API.
    
    Zoho field mappings:
    - Decision_Id: Our internal decision ID
    - Decision: The proposal text
    - Decision_By: The proposer name
    - Approve_Count: Approval vote count
    - Reject_Count: Rejection vote count
    - Total_Vote: Total vote count
    - Status: Decision status (Pending, Approved, Rejected, Expired)
    - Propose_Time: When the decision was proposed/created
    
    Args:
        decision: Decision instance
        channel_name: Optional Slack channel name
        
    Returns:
        Dictionary with Zoho CRM fields
    """
    return {
        "Name": f"Decision #{decision.id}: {decision.text[:50]}",
        "Decision_Id": decision.id,
        "Decision": decision.text,
        "Decision_By": decision.proposer_name or "",
        "Approve_Count": decision.approval_count or 0,
        "Reject_Count": decision.rejection_count or 0,
        "Total_Vote": (decision.approval_count or 0) + (decision.rejection_count or 0),
        "Status": map_status(decision.status),
        "Propose_Time": format_datetime(decision.created_at),
    }


def map_status(status: str) -> str:
    """Map Decision Agent status to Zoho CRM status"""
    status_map = {
        "pending": "Pending",
        "approved": "Approved",
        "rejected": "Rejected",
        "expired": "Expired",
    }
    return status_map.get(status, "Pending")


def sync_decision_to_zoho(
    decision: Decision,
    team_id: str,
    db: Session,
    channel_name: Optional[str] = None
) -> bool:
    """
    Sync a decision to Zoho CRM for a specific team.
    Creates a new record if it doesn't exist, updates if it does.
    
    Args:
        decision: Decision instance to sync
        team_id: Slack team ID
        db: Database session
        channel_name: Optional Slack channel name
        
    Returns:
        True if successful or team has no Zoho connection, False if sync failed
    """
    if not team_id:
        logger.warning("No team_id provided for Zoho sync - skipping")
        return True
    
    try:
        # Create Zoho client for this team
        try:
            zoho_client = ZohoCRMClient(team_id, db)
        except ValueError as e:
            # Team has no Zoho connection - this is OK, just skip sync
            logger.debug(f"Team {team_id} has no Zoho connection - skipping sync: {e}")
            return False  # Return False so auto-prompt can show dashboard URL
        
        zoho_data = map_decision_to_zoho(decision, channel_name)
        
        # Check if record exists in Zoho by searching for Decision_ID
        existing = zoho_client.search_decision_by_id(decision.id)
        
        if existing:
            # Update existing record (use Zoho's record ID)
            zoho_record_id = existing.get("id")
            result = zoho_client.update_decision(str(zoho_record_id), zoho_data)
            if result:
                logger.info(
                    f"✅ Updated decision #{decision.id} in Zoho CRM for team {team_id}"
                )
                return True
        else:
            # Create new record
            result = zoho_client.create_decision(zoho_data)
            if result:
                logger.info(
                    f"✅ Created decision #{decision.id} in Zoho CRM for team {team_id}"
                )
                return True
        
        logger.error(
            f"❌ Failed to sync decision #{decision.id} to Zoho CRM for team {team_id}"
        )
        return False
        
    except Exception as e:
        logger.error(
            f"❌ Error syncing decision #{decision.id} to Zoho for team {team_id}: {e}",
            exc_info=True
        )
        return False


def sync_vote_to_zoho(
    decision: Decision,
    team_id: str,
    db: Session,
    channel_name: Optional[str] = None
) -> bool:
    """
    Sync vote counts to Zoho CRM for a specific team.
    Updates existing decision record with new vote counts.
    Called after a vote is cast or decision status changes.
    
    Args:
        decision: Decision instance with updated vote counts
        team_id: Slack team ID
        db: Database session
        channel_name: Optional Slack channel name
        
    Returns:
        True if successful or team has no Zoho connection, False if sync failed
    """
    if not team_id:
        logger.warning("No team_id provided for Zoho vote sync - skipping")
        return True
    
    try:
        # Create Zoho client for this team
        try:
            zoho_client = ZohoCRMClient(team_id, db)
        except ValueError as e:
            # Team has no Zoho connection - this is OK, just skip sync
            logger.debug(f"Team {team_id} has no Zoho connection - skipping vote sync: {e}")
            return False  # Return False so caller knows sync didn't happen
        
        zoho_data = map_decision_to_zoho(decision, channel_name)
        
        # Find the Zoho record by Decision_ID
        existing = zoho_client.search_decision_by_id(decision.id)
        if not existing:
            logger.warning(
                f"Decision #{decision.id} not found in Zoho CRM for team {team_id} - "
                "may need to create it first"
            )
            # Try to create it
            result = zoho_client.create_decision(zoho_data)
            if result:
                logger.info(
                    f"✅ Created decision #{decision.id} in Zoho CRM for team {team_id}"
                )
                return True
            return False
        
        # Update the record with new vote counts (use Zoho's record ID)
        zoho_record_id = existing.get("id")
        result = zoho_client.update_decision(str(zoho_record_id), zoho_data)
        
        if result:
            logger.info(
                f"✅ Updated vote counts for decision #{decision.id} in Zoho CRM "
                f"for team {team_id}"
            )
            return True
        else:
            logger.error(
                f"❌ Failed to update vote counts for decision #{decision.id} "
                f"in Zoho CRM for team {team_id}"
            )
            return False
            
    except Exception as e:
        logger.error(
            f"❌ Error updating votes in Zoho for team {team_id}: {e}",
            exc_info=True
        )
        return False


def handle_zoho_sync_error(error: Exception, context: str = "") -> None:
    """
    Log and handle Zoho sync errors gracefully.
    The main operation should continue even if sync fails.
    
    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
    """
    logger.error(
        f"❌ Zoho sync error{' in ' + context if context else ''}: {str(error)}",
        exc_info=True
    )
