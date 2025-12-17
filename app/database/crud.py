from datetime import datetime, UTC, timedelta
import logging
from typing import Any, List, Optional, Tuple, Dict

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from ..models import Decision, Vote, ChannelConfig, ConfigChangeLog
from ..utils.common import get_utc_now
from ..utils.db_errors import handle_db_errors, safe_commit
from ..config.logging import get_context_logger

logger = get_context_logger(__name__)

VALID_DECISION_STATUSES = {"pending", "approved", "rejected", "expired", "expired_unreachable"}
VALID_VOTE_TYPES = {"approve", "reject"}


def _normalize_text(text: str) -> str:
    """Normalize text by stripping whitespace."""
    return (text or "").strip()


# ============================================================================
# DECISION CRUD OPERATIONS
# ============================================================================

def create_decision(
    db: Session,
    channel_id: str,
    text: str,
    created_by: Optional[str] = None,
    created_by_name: Optional[str] = None,
    user_id: Optional[str] = None,
    group_size_at_creation: int = 1,
    approval_threshold: int = 1,
    status: str = "pending",
    team_id: Optional[str] = None,
) -> Decision:
    """
    Create a new decision record. Now uses dynamic group_size and threshold.
    """
    # Support older callers that pass `user_id` instead of `created_by`
    if not created_by and user_id:
        created_by = user_id

    # Ensure we always have a proposer display name to satisfy NOT NULL DB constraint
    if not created_by_name:
        created_by_name = created_by or "Unknown"

    cleaned_text = _normalize_text(text)

    if len(cleaned_text) < 10:
        raise ValueError("Decision text must be at least 10 characters long.")
    if len(cleaned_text) > 500:
        raise ValueError("Decision text must not exceed 500 characters.")
    if status not in VALID_DECISION_STATUSES:
        raise ValueError("Invalid status provided for decision creation.")
    if group_size_at_creation <= 0:
        # NOTE: This should technically not happen if Slack API is used, but useful fallback
        group_size_at_creation = 1
        logger.warning("group_size_at_creation was <= 0, defaulting to 1.")
    if approval_threshold <= 0:
        approval_threshold = 1
        logger.warning("approval_threshold was <= 0, defaulting to 1.")

    now = get_utc_now()
    closed_at = now if status in {"approved", "rejected", "expired"} else None

    decision = Decision(
        channel_id=channel_id,
        text=cleaned_text,
        status=status,
        proposer_phone=created_by,
        proposer_name=created_by_name,
        group_size_at_creation=group_size_at_creation,
        approval_threshold=approval_threshold,
        approval_count=0,
        rejection_count=0,
        created_at=now,
        closed_at=closed_at,
        team_id=team_id,
    )

    try:
        db.add(decision)
        db.commit()
        db.refresh(decision)
        logger.info("Created decision", extra={"decision_id": decision.id, "channel_id": channel_id, "user_id": created_by})
        return decision
    except Exception as exc:
        logger.error("Database error in create_decision: %s", exc)
        db.rollback()
        raise


@handle_db_errors("get_decision_by_id", default_return=None)
def get_decision_by_id(db: Session, decision_id: int) -> Optional[Decision]:
    """Get a decision by its ID."""
    return db.query(Decision).filter(Decision.id == decision_id).first()


@handle_db_errors("get_decisions_by_channel", default_return=[])
def get_decisions_by_channel(
    db: Session, 
    channel_id: str, 
    status: Optional[str] = None
) -> List[Decision]:
    """Get all decisions for a channel, optionally filtered by status."""
    query = db.query(Decision).filter(Decision.channel_id == channel_id)
    
    if status:
        query = query.filter(Decision.status == status)
    
    return query.order_by(Decision.created_at.desc()).all()

# --- FUNCTION FOR PAGINATION ---
def get_decisions_by_channel_paginated(
    db: Session, 
    channel_id: str, 
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
) -> List[Decision]:
    """Get decisions for a channel, filtered by status, sorted by newest first, with pagination."""
    try:
        query = db.query(Decision).filter(Decision.channel_id == channel_id)
        
        if status:
            query = query.filter(Decision.status == status)
            
        results = (
            query
            .order_by(Decision.created_at.desc()) # Sort by created_at descending (newest first)
            .limit(limit)
            .offset(offset)
            .all()
        )
        logger.debug("Fetched paginated decisions", extra={"channel_id": channel_id, "status": status, "limit": limit, "offset": offset, "returned": len(results)})
        return results
    except Exception as e:
        logger.error(f"Database error in get_decisions_by_channel_paginated: {str(e)}")
        return []
# --- END NEW FUNCTION ---


@handle_db_errors("get_pending_decisions", default_return=[])
def get_pending_decisions(db: Session, channel_id: Optional[str] = None) -> List[Decision]:
    """Get all pending decisions, optionally filtered by channel."""
    query = db.query(Decision).filter(Decision.status == "pending")
    
    if channel_id:
        query = query.filter(Decision.channel_id == channel_id)
    
    return query.order_by(Decision.created_at.desc()).all()


def get_decisions_by_status(db: Session, status: str, channel_id: Optional[str] = None) -> List[Decision]:
    """Get all decisions with a specific status."""
    try:
        query = db.query(Decision).filter(Decision.status == status)
        
        if channel_id:
            query = query.filter(Decision.channel_id == channel_id)
        
        return query.order_by(Decision.created_at.desc()).all()
    except Exception as e:
        logger.error(f"Database error in get_decisions_by_status: {str(e)}")
        return []


def get_all_decisions(db: Session, channel_id: Optional[str] = None) -> List[Decision]:
    """Get all decisions, optionally filtered by channel."""
    try:
        query = db.query(Decision)
        
        if channel_id:
            query = query.filter(Decision.channel_id == channel_id)
        
        return query.order_by(Decision.created_at.desc()).all()
    except Exception as e:
        logger.error(f"Database error in get_all_decisions: {str(e)}")
        return []


def update_decision_status(
    db: Session, 
    decision_id: int, 
    new_status: str
) -> Optional[Decision]:
    """Update the status of a decision."""
    if new_status not in VALID_DECISION_STATUSES:
        raise ValueError(f"Invalid status: {new_status}. Must be one of {VALID_DECISION_STATUSES}")

    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if decision is None:
        logger.warning(f"Decision #{decision_id} not found for status update")
        return None

    decision.status = new_status
    decision.closed_at = get_utc_now() if new_status != "pending" else None

    try:
        db.commit()
        db.refresh(decision)
        logger.info(f"✅ Updated decision #{decision_id} status to {new_status}")
        return decision
    except Exception as exc:
        logger.error("Database error in update_decision_status: %s", exc)
        db.rollback()
        return None


def close_decision_as_unreachable(db: Session, decision_id: int) -> Optional[Decision]:
    """
    Close a decision as unreachable due to insufficient channel members.
    Sets status to 'expired_unreachable' and closed_at timestamp.
    """
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    
    if decision is None:
        logger.warning(f"Decision #{decision_id} not found for unreachable closure")
        return None
    
    decision.status = "expired_unreachable"
    decision.closed_at = get_utc_now()
    
    try:
        db.commit()
        db.refresh(decision)
        logger.info(f"🔒 Closed decision #{decision_id} as unreachable")
        return decision
    except Exception as exc:
        logger.error(f"Database error in close_decision_as_unreachable: {exc}")
        db.rollback()
        return None


def get_pending_decisions_count(db: Session, channel_id: Optional[str] = None) -> int:
    """Get the count of pending decisions."""
    try:
        query = db.query(Decision).filter(Decision.status == "pending")

        if channel_id is not None:
            query = query.filter(Decision.channel_id == channel_id)
        
        return query.count()
    except Exception as e:
        logger.error(f"Database error in get_pending_decisions_count: {str(e)}")
        return 0


def search_decisions(
    db: Session, 
    channel_id: Optional[str], 
    search_term: str
) -> List[Decision]:
    """Search decisions by text content (case-insensitive)."""
    try:
        query = db.query(Decision).filter(Decision.text.ilike(f"%{search_term}%"))

        if channel_id is not None:
            query = query.filter(Decision.channel_id == channel_id)

        return query.order_by(Decision.created_at.desc()).all()
    except Exception as e:
        logger.error(f"Database error in search_decisions: {str(e)}")
        return []

# --- FUNCTION FOR SUMMARY STATISTICS ---
def get_decision_summary_by_channel(db: Session, channel_id: str) -> Dict[str, int]:
    """
    Calculates the total count and counts per status for a given channel.
    """
    try:
        # Query to count total decisions
        total_count = db.query(Decision).filter(Decision.channel_id == channel_id).count()

        # Query to count decisions grouped by status
        status_counts = (
            db.query(Decision.status, func.count(Decision.id))
            .filter(Decision.channel_id == channel_id)
            .group_by(Decision.status)
            .all()
        )

        summary = {"total": total_count}
        
        # Initialize all known statuses to 0
        for status in VALID_DECISION_STATUSES:
            summary[status] = 0

        # Update with actual counts
        for status, count in status_counts:
            # Only add if status is in VALID_DECISION_STATUSES to avoid clutter
            if status in VALID_DECISION_STATUSES:
                summary[status] = count
            
        logger.debug("Computed decision summary", extra={"channel_id": channel_id, **summary})
        return summary

    except Exception as e:
        logger.error(f"Database error in get_decision_summary_by_channel: {str(e)}")
        return {"total": 0, "pending": 0, "approved": 0, "rejected": 0, "expired": 0}
# --- END NEW FUNCTION ---


# ============================================================================
# VOTE CRUD OPERATIONS
# ============================================================================

def create_vote(
    db: Session,
    decision_id: int,
    voter_phone: Optional[str] = None,
    voter_name: Optional[str] = None,
    vote_type: Optional[str] = None,
    # Backwards-compatible aliases
    voter_id: Optional[str] = None,
    user_id: Optional[str] = None,
    vote_value: Optional[str] = None,
) -> Optional[Vote]:
    """
    Create a vote for a decision.
    """
    # Support legacy/alternate arg names
    # Map legacy aliases
    if not voter_phone and voter_id:
        voter_phone = voter_id
    if not voter_phone and user_id:
        voter_phone = user_id
    if not vote_type and vote_value:
        vote_type = vote_value

    if vote_type not in VALID_VOTE_TYPES:
        logger.error(f"Invalid vote_type: {vote_type}")
        raise ValueError(f"Invalid vote_type. Must be one of {VALID_VOTE_TYPES}")

    try:
        # Check if user already voted (safety check)
        existing_vote = db.query(Vote).filter(
            and_(
                Vote.decision_id == decision_id, 
                Vote.voter_phone == voter_phone
            )
        ).first()
        
        if existing_vote:
            logger.warning(f"User {voter_phone} already voted on decision {decision_id}")
            return None

        # Verify decision exists
        decision = db.query(Decision).filter(Decision.id == decision_id).first()
        if decision is None:
            logger.warning(f"Decision {decision_id} not found when creating vote")
            return None

        # Create new vote
        # Ensure voter_name is present to satisfy DB NOT NULL
        if not voter_name:
            voter_name = voter_phone or "Unknown"

        db_vote = Vote(
            decision_id=decision_id,
            voter_phone=voter_phone,
            voter_name=voter_name,
            vote_type=vote_type,
            voted_at=get_utc_now()
        )
        
        db.add(db_vote)
        db.flush()
        logger.info("Recorded vote", extra={"decision_id": decision_id, "voter_id": voter_phone, "voter_name": voter_name, "vote_type": vote_type})
        return db_vote
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creating vote: {e}")
        return None


def check_if_user_voted(db: Session, decision_id: int, voter_phone: str) -> bool:
    """Check if a user has already voted on a decision."""
    try:
        existing_vote = db.query(Vote).filter(
            and_(
                Vote.decision_id == decision_id,
                Vote.voter_phone == voter_phone
            )
        ).first()
        
        return existing_vote is not None
    except Exception as e:
        logger.error(f"Database error in check_if_user_voted: {str(e)}")
        return False


def get_votes_by_decision(db: Session, decision_id: int) -> List[Vote]:
    """Get all votes for a decision."""
    try:
        return db.query(Vote).filter(Vote.decision_id == decision_id).order_by(Vote.voted_at.asc()).all()
    except Exception as e:
        logger.error(f"Database error in get_votes_by_decision: {str(e)}")
        return []


def get_user_vote(db: Session, decision_id: int, voter_phone: str) -> Optional[Vote]:
    """Get a user's vote on a specific decision."""
    try:
        return db.query(Vote).filter(
            Vote.decision_id == decision_id,
            Vote.voter_phone == voter_phone
        ).first()
    except Exception as e:
        logger.error(f"Database error in get_user_vote: {str(e)}")
        return None


# ============================================================================
# VOTE ORCHESTRATION & BUSINESS LOGIC
# ============================================================================

def update_vote_counts_and_status(
    db: Session, 
    decision_id: int, 
    vote_type: str
) -> Optional[Decision]:
    """Update vote counts and check if decision should be closed."""
    decision = get_decision_by_id(db, decision_id)
    if not decision:
        logger.warning(f"Decision #{decision_id} not found for count update")
        return None
    
    # Increment vote count
    if vote_type == "approve":
        decision.approval_count += 1
    elif vote_type == "reject":
        decision.rejection_count += 1
    else:
        logger.error(f"Invalid vote_type in update_vote_counts_and_status: {vote_type}")
        return None
    
    # Check if threshold reached for approval
    if decision.approval_count >= decision.approval_threshold:
        decision.status = "approved"
        decision.closed_at = get_utc_now()
        logger.info(
            f"🎉 Decision #{decision_id} APPROVED! "
            f"({decision.approval_count}/{decision.approval_threshold})"
        )
    
    # Check if threshold reached for rejection
    elif decision.rejection_count >= decision.approval_threshold:
        decision.status = "rejected"
        decision.closed_at = get_utc_now()
        logger.info(
            f"❌ Decision #{decision_id} REJECTED! "
            f"({decision.rejection_count}/{decision.approval_threshold})"
        )
    
    try:
        db.commit()
        db.refresh(decision)
        logger.info("Updated vote counts", extra={"decision_id": decision_id, "approval_count": decision.approval_count, "rejection_count": decision.rejection_count, "status": decision.status})
        return decision
    except Exception as exc:
        logger.error(f"Database error in update_vote_counts_and_status: {exc}")
        db.rollback()
        return None


def vote_on_decision(
    db: Session,
    decision_id: int,
    voter_id: str,
    voter_name: str,
    vote_type: str,
    return_updated_decision: bool = False,
) -> Tuple:
    """
    Orchestrate the complete vote transaction.
    Returns: (success: bool, message: str, updated_decision: Optional[Decision])
    """
    # 1. Get and validate decision
    decision = get_decision_by_id(db, decision_id)
    if decision is None:
        msg = f"❌ Decision #{decision_id} not found"
        if return_updated_decision:
            return False, msg, None
        return False, msg

    # 2. Check for duplicate vote first (so duplicate errors are reported
    #    even if the decision becomes closed by the previous vote)
    if check_if_user_voted(db, decision_id, voter_id):
        msg = "❌ You already voted on this decision"
        if return_updated_decision:
            return False, msg, None
        return False, msg

    # 3. Check if decision is still pending
    if decision.status != "pending":
        msg = f"❌ Decision already closed (status: {decision.status.upper()})"
        if return_updated_decision:
            return False, msg, None
        return False, msg

    # 4. Validate vote type
    if vote_type not in VALID_VOTE_TYPES:
        msg = f"❌ Invalid vote type: {vote_type}"
        if return_updated_decision:
            return False, msg, None
        return False, msg

    # 5. Create vote record
    vote = create_vote(
        db=db,
        decision_id=decision_id,
        voter_phone=voter_id,
        voter_name=voter_name,
        vote_type=vote_type,
    )

    if vote is None:
        msg = "❌ Unable to record vote. Please try again."
        if return_updated_decision:
            return False, msg, None
        return False, msg

    # 6. Update counts and check if threshold reached
    updated_decision = update_vote_counts_and_status(db, decision_id, vote_type)

    if updated_decision is None:
        msg = "❌ Failed to update vote counts"
        if return_updated_decision:
            return False, msg, None
        return False, msg

    # Success
    # Backwards-compatible behaviour:
    # - Older callers/tests expect a (success, message) 2-tuple
    # - Handlers may need the updated Decision object as a third value
    if return_updated_decision:
        return True, "✅ Vote recorded successfully", updated_decision
    return True, "✅ Vote recorded successfully"


# ============================================================================
# CHANNEL CONFIG CRUD OPERATIONS (Updated default percentage)
# ============================================================================

def get_channel_config(db: Session, channel_id: str) -> ChannelConfig:
    """
    Get channel configuration or create default if not exists.
    Group size is now fetched dynamically from Slack for each decision.
    """
    try:
        logger.info(f"🔍 Fetching config for channel {channel_id}")
        config = db.query(ChannelConfig).filter(ChannelConfig.channel_id == channel_id).first()
        
        if config is None:
            # Create default config for this channel
            logger.info(f"📝 Creating new config for channel {channel_id}")
            config = ChannelConfig(
                channel_id=channel_id,
                approval_percentage=60  # DEFAULT: 60%
            )
            db.add(config)
            db.commit()
            db.refresh(config)
            logger.info(f"✅ Created default config for channel {channel_id}")
        else:
            logger.info(f"✅ Config exists for channel {channel_id}")
        
        logger.info(f"✅ Returning config for channel {channel_id}")
        return config
    except Exception as e:
        logger.error(f"Database error in get_channel_config: {str(e)}", exc_info=True)
        db.rollback()
        # Return default config object (not persisted)
        return ChannelConfig(
            channel_id=channel_id,
            approval_percentage=60
        )


def update_channel_config(
    db: Session,
    channel_id: str,
    updated_by: str,
    updated_by_name: Optional[str] = None,
    **kwargs
) -> Optional[ChannelConfig]:
    """
    Update channel configuration settings.
    Logs all changes to ConfigChangeLog table.
    Note: group_size is no longer stored - it's fetched dynamically from Slack.
    """
    try:
        config = get_channel_config(db, channel_id)
        
        # Track changes for logging
        changes = []
        
        # Update fields if provided and track changes
        if 'approval_percentage' in kwargs:
            old_value = config.approval_percentage
            new_value = kwargs['approval_percentage']
            if old_value != new_value:
                config.approval_percentage = new_value
                changes.append(('approval_percentage', old_value, new_value))
        
        # Note: auto_close_hours has been removed - decisions no longer auto-close
        
        # Note: group_size is no longer handled here - it's always fetched from Slack
        
        config.updated_by = updated_by
        config.updated_at = get_utc_now()
        
        db.commit()
        db.refresh(config)
        
        # Log all changes
        for setting_name, old_val, new_val in changes:
            log_config_change(
                db=db,
                channel_id=channel_id,
                setting_name=setting_name,
                old_value=old_val,
                new_value=new_val,
                changed_by=updated_by,
                changed_by_name=updated_by_name or updated_by
            )
        
        logger.info(f"✅ Updated config for channel {channel_id} by {updated_by}")
        return config
    except Exception as e:
        logger.error(f"Database error in update_channel_config: {str(e)}")
        db.rollback()
        return None


def log_config_change(
    db: Session,
    channel_id: str,
    setting_name: str,
    old_value: int,
    new_value: int,
    changed_by: str,
    changed_by_name: str
) -> Optional[ConfigChangeLog]:
    """
    Log a configuration change to the audit trail.
    
    Args:
        db: Database session
        channel_id: Channel ID where config was changed
        setting_name: Name of the setting (approval_percentage)
        old_value: Previous value
        new_value: New value
        changed_by: User ID who made the change
        changed_by_name: Username for display
    
    Returns:
        ConfigChangeLog object or None on error
    """
    try:
        log_entry = ConfigChangeLog(
            channel_id=channel_id,
            setting_name=setting_name,
            old_value=old_value,
            new_value=new_value,
            changed_by=changed_by,
            changed_by_name=changed_by_name,
            changed_at=get_utc_now()
        )
        
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        
        logger.info(
            f"📝 Logged config change: {channel_id} - {setting_name}: "
            f"{old_value} → {new_value} by {changed_by_name}"
        )
        
        return log_entry
    except Exception as e:
        logger.error(f"Error logging config change: {str(e)}")
        db.rollback()
        return None


def get_config_change_logs(
    db: Session,
    channel_id: str,
    limit: int = 50
) -> List[ConfigChangeLog]:
    """
    Get config change history for a channel.
    
    Args:
        db: Database session
        channel_id: Channel ID
        limit: Maximum number of logs to return (default 50)
    
    Returns:
        List of ConfigChangeLog objects, newest first
    """
    try:
        return (
            db.query(ConfigChangeLog)
            .filter(ConfigChangeLog.channel_id == channel_id)
            .order_by(ConfigChangeLog.changed_at.desc())
            .limit(limit)
            .all()
        )
    except Exception as e:
        logger.error(f"Error fetching config change logs: {str(e)}")
        return []


def validate_config_value(setting: str, value: Any) -> Tuple[bool, str]:
    """
    Validate configuration values.
    Note: group_size is no longer validated here as it's fetched dynamically from Slack.
    """
    if setting == "approval_percentage":
        try:
            val = int(value)
            if val <= 0 or val > 100:
                return False, "Approval percentage must be between 1 and 100"
            return True, ""
        except (ValueError, TypeError):
            return False, "Approval percentage must be a valid integer"
    
    else:
        return False, f"Unknown setting: {setting}"
