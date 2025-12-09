"""
Zoho CRM sync utilities for Decision Agent.
Handles syncing decisions and votes to Zoho CRM.
"""
import logging
import os
from datetime import datetime
from typing import Optional
from app.models import Decision, Vote
from .zoho_crm import zoho_client

logger = logging.getLogger(__name__)


def is_zoho_enabled() -> bool:
    """Check if Zoho integration is enabled"""
    return os.getenv("ZOHO_ENABLED", "false").lower() == "true"


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
    decision: Decision, channel_name: Optional[str] = None
) -> bool:
    """
    Sync a decision to Zoho CRM.
    Creates a new record if it doesn't exist, updates if it does.
    Returns True if successful, False otherwise.
    """
    if not is_zoho_enabled():
        logger.debug("Zoho integration is disabled")
        return True
    
    try:
        zoho_data = map_decision_to_zoho(decision, channel_name)
        
        # Check if record exists in Zoho by searching for Decision_ID
        existing = zoho_client.search_decision_by_id(decision.id)
        
        if existing:
            # Update existing record (use Zoho's record ID)
            zoho_record_id = existing.get("id")
            result = zoho_client.update_decision(str(zoho_record_id), zoho_data)
            if result:
                logger.info(f"✅ Updated decision #{decision.id} in Zoho CRM")
                return True
        else:
            # Create new record
            result = zoho_client.create_decision(zoho_data)
            if result:
                logger.info(f"✅ Created decision #{decision.id} in Zoho CRM")
                return True
        
        logger.error(f"❌ Failed to sync decision #{decision.id} to Zoho CRM")
        return False
    except Exception as e:
        logger.error(f"❌ Error syncing decision to Zoho: {e}", exc_info=True)
        return False


def sync_vote_to_zoho(decision: Decision, channel_name: Optional[str] = None) -> bool:
    """
    Sync vote counts to Zoho CRM (updates existing decision record).
    Called after a vote is cast or decision status changes.
    Returns True if successful, False otherwise.
    """
    if not is_zoho_enabled():
        logger.debug("Zoho integration is disabled")
        return True
    
    try:
        zoho_data = map_decision_to_zoho(decision, channel_name)
        
        # Find the Zoho record by Decision_ID
        existing = zoho_client.search_decision_by_id(decision.id)
        if not existing:
            logger.error(f"❌ Decision #{decision.id} not found in Zoho CRM")
            return False
        
        # Update the record with new vote counts (use Zoho's record ID)
        zoho_record_id = existing.get("id")
        result = zoho_client.update_decision(str(zoho_record_id), zoho_data)
        
        if result:
            logger.info(f"✅ Updated vote counts for decision #{decision.id} in Zoho CRM")
            return True
        else:
            logger.error(f"❌ Failed to update vote counts for decision #{decision.id} in Zoho CRM")
            return False
    except Exception as e:
        logger.error(f"❌ Error updating votes in Zoho: {e}", exc_info=True)
        return False


def handle_zoho_sync_error(error: Exception, context: str = "") -> None:
    """
    Log and handle Zoho sync errors gracefully.
    The main operation should continue even if sync fails.
    """
    logger.error(
        f"❌ Zoho sync error{' in ' + context if context else ''}: {str(error)}",
        exc_info=True
    )
