"""
Zoho CRM sync utilities for Decision Agent.
Handles syncing decisions and votes to Zoho CRM with multi-tenant support.

Each organization's data is synced to their Zoho CRM account.
Uses zoho_org_id as the primary identifier.
"""
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models import Decision, SlackInstallation
from .zoho_crm import ZohoCRMClient

logger = logging.getLogger(__name__)


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime to ISO string for Zoho API (without microseconds)"""
    if dt is None:
        return None
    # Format as ISO datetime without microseconds: 2025-12-09T14:02:06
    return dt.strftime('%Y-%m-%dT%H:%M:%S')


def get_org_id_from_team_id(team_id: str, db: Session) -> Optional[str]:
    """
    Get zoho_org_id from team_id by looking up SlackInstallation.
    
    Args:
        team_id: Slack team ID
        db: Database session
        
    Returns:
        zoho_org_id if found, None otherwise
    """
    slack_install = db.query(SlackInstallation).filter(
        SlackInstallation.team_id == team_id
    ).first()
    
    if slack_install:
        return slack_install.zoho_org_id
    return None


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
    - Zoho_Org_Id: Zoho organization ID
    - Slack_Team_Id: Source Slack workspace ID
    - Slack_Channel_Id: Source Slack channel ID
    
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
        "Zoho_Org_Id": decision.zoho_org_id or "",
        "Slack_Team_Id": decision.team_id or "",
        "Slack_Channel_Id": decision.channel_id or "",
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
    org_id: str,
    db: Session,
    channel_name: Optional[str] = None
) -> bool:
    """
    Sync a decision to Zoho CRM for a specific organization.
    Creates a new record if it doesn't exist, updates if it does.
    
    Args:
        decision: Decision instance to sync
        org_id: Zoho organization ID
        db: Database session
        channel_name: Optional Slack channel name
        
    Returns:
        True if successful, False if sync failed or no Zoho connection
    """
    if not org_id:
        logger.warning("No org_id provided for Zoho sync - skipping")
        return False
    
    try:
        # Create Zoho client for this organization
        try:
            zoho_client = ZohoCRMClient(org_id, db)
        except ValueError as e:
            # Organization has no Zoho connection - this is OK, just skip sync
            logger.debug(f"Org {org_id} has no Zoho connection - skipping sync: {e}")
            return False
        
        zoho_data = map_decision_to_zoho(decision, channel_name)
        
        # Check if record exists in Zoho by searching for Decision_ID
        existing = zoho_client.search_decision_by_id(decision.id)
        
        if existing:
            # Update existing record (use Zoho's record ID)
            zoho_record_id = existing.get("id")
            result = zoho_client.update_decision(str(zoho_record_id), zoho_data)
            if result:
                logger.info(
                    f"✅ Updated decision #{decision.id} in Zoho CRM for org {org_id}"
                )
                return True
        else:
            # Create new record
            result = zoho_client.create_decision(zoho_data)
            if result:
                logger.info(
                    f"✅ Created decision #{decision.id} in Zoho CRM for org {org_id}"
                )
                return True
        
        logger.error(
            f"❌ Failed to sync decision #{decision.id} to Zoho CRM for org {org_id}"
        )
        return False
        
    except Exception as e:
        logger.error(
            f"❌ Error syncing decision #{decision.id} to Zoho for org {org_id}: {e}",
            exc_info=True
        )
        return False


def sync_vote_to_zoho(
    decision: Decision,
    org_id: str,
    db: Session,
    channel_name: Optional[str] = None
) -> bool:
    """
    Sync vote counts to Zoho CRM for a specific organization.
    Updates existing decision record with new vote counts.
    Called after a vote is cast or decision status changes.
    
    Args:
        decision: Decision instance with updated vote counts
        org_id: Zoho organization ID
        db: Database session
        channel_name: Optional Slack channel name
        
    Returns:
        True if successful, False if sync failed or no Zoho connection
    """
    if not org_id:
        logger.warning("No org_id provided for Zoho vote sync - skipping")
        return False
    
    try:
        # Create Zoho client for this organization
        try:
            zoho_client = ZohoCRMClient(org_id, db)
        except ValueError as e:
            # Organization has no Zoho connection - this is OK, just skip sync
            logger.debug(f"Org {org_id} has no Zoho connection - skipping vote sync: {e}")
            return False
        
        zoho_data = map_decision_to_zoho(decision, channel_name)
        
        # Find the Zoho record by Decision_ID
        existing = zoho_client.search_decision_by_id(decision.id)
        if not existing:
            logger.warning(
                f"Decision #{decision.id} not found in Zoho CRM for org {org_id} - "
                "may need to create it first"
            )
            # Try to create it
            result = zoho_client.create_decision(zoho_data)
            if result:
                logger.info(
                    f"✅ Created decision #{decision.id} in Zoho CRM for org {org_id}"
                )
                return True
            return False
        
        # Update the record with new vote counts (use Zoho's record ID)
        zoho_record_id = existing.get("id")
        result = zoho_client.update_decision(str(zoho_record_id), zoho_data)
        
        if result:
            logger.info(
                f"✅ Updated vote counts for decision #{decision.id} in Zoho CRM "
                f"for org {org_id}"
            )
            return True
        else:
            logger.error(
                f"❌ Failed to update vote counts for decision #{decision.id} "
                f"in Zoho CRM for org {org_id}"
            )
            return False
            
    except Exception as e:
        logger.error(
            f"❌ Error updating votes in Zoho for org {org_id}: {e}",
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
