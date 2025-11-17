from datetime import datetime
import logging
from typing import List, Optional, Tuple, Dict

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models import Decision, Vote

logger = logging.getLogger(__name__)

VALID_DECISION_STATUSES = {"pending", "approved", "rejected", "expired"}
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
    created_by: str,
    created_by_name: str,
    group_size_at_creation: int = 1,
    approval_threshold: int = 1,
    status: str = "pending",
) -> Decision:
    """
    Create a new decision record with validation for text length and status.
    """
    cleaned_text = _normalize_text(text)

    if len(cleaned_text) < 10:
        raise ValueError("Decision text must be at least 10 characters long.")
    if len(cleaned_text) > 500:
        raise ValueError("Decision text must not exceed 500 characters.")
    if status not in VALID_DECISION_STATUSES:
        raise ValueError("Invalid status provided for decision creation.")
    if group_size_at_creation <= 0:
        raise ValueError("group_size_at_creation must be greater than 0.")
    if approval_threshold <= 0:
        raise ValueError("approval_threshold must be greater than 0.")

    now = datetime.utcnow()
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
    )

    try:
        db.add(decision)
        db.commit()
        db.refresh(decision)
        logger.info(f"✅ Created decision #{decision.id}: {cleaned_text[:50]}...")
        return decision
    except Exception as exc:
        logger.error("Database error in create_decision: %s", exc)
        db.rollback()
        raise


def get_decision_by_id(db: Session, decision_id: int) -> Optional[Decision]:
    """Get a decision by its ID."""
    try:
        return db.query(Decision).filter(Decision.id == decision_id).first()
    except Exception as e:
        logger.error(f"Database error in get_decision_by_id: {str(e)}")
        return None


def get_decisions_by_channel(
    db: Session, 
    channel_id: str, 
    status: Optional[str] = None
) -> List[Decision]:
    """Get all decisions for a channel, optionally filtered by status."""
    try:
        query = db.query(Decision).filter(Decision.channel_id == channel_id)
        
        if status:
            query = query.filter(Decision.status == status)
        
        return query.order_by(Decision.created_at.desc()).all()
    except Exception as e:
        logger.error(f"Database error in get_decisions_by_channel: {str(e)}")
        return []

# --- NEW FUNCTION FOR PAGINATION ---
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
            
        return (
            query
            .order_by(Decision.created_at.desc()) # Sort by created_at descending (newest first)
            .limit(limit)
            .offset(offset)
            .all()
        )
    except Exception as e:
        logger.error(f"Database error in get_decisions_by_channel_paginated: {str(e)}")
        return []
# --- END NEW FUNCTION ---


def get_pending_decisions(db: Session, channel_id: Optional[str] = None) -> List[Decision]:
    """Get all pending decisions, optionally filtered by channel."""
    try:
        query = db.query(Decision).filter(Decision.status == "pending")
        
        if channel_id:
            query = query.filter(Decision.channel_id == channel_id)
        
        return query.order_by(Decision.created_at.desc()).all()
    except Exception as e:
        logger.error(f"Database error in get_pending_decisions: {str(e)}")
        return []


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
    decision.closed_at = datetime.utcnow() if new_status != "pending" else None

    try:
        db.commit()
        db.refresh(decision)
        logger.info(f"✅ Updated decision #{decision_id} status to {new_status}")
        return decision
    except Exception as exc:
        logger.error("Database error in update_decision_status: %s", exc)
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

# --- NEW FUNCTION FOR SUMMARY STATISTICS ---
def get_decision_summary_by_channel(db: Session, channel_id: str) -> Dict[str, int]:
    """
    Calculates the total count and counts per status for a given channel.
    Returns: {"total": 25, "pending": 5, "approved": 18, "rejected": 2, "expired": 0}
    """
    try:
        # Query to count total decisions
        total_count = db.query(Decision).filter(Decision.channel_id == channel_id).count()

        # Query to count decisions grouped by status
        status_counts = (
            db.query(Decision.status, func.count())
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
            summary[status] = count
            
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
    voter_phone: str,
    voter_name: str,
    vote_type: str,
    is_anonymous: bool = False
) -> Optional[Vote]:
    """
    Create a vote for a decision.
    """
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
        db_vote = Vote(
            decision_id=decision_id,
            voter_phone=voter_phone,
            voter_name=voter_name,
            vote_type=vote_type,
            is_anonymous=is_anonymous,
            voted_at=datetime.utcnow()
        )
        
        db.add(db_vote)
        db.flush()
        
        anon_text = " (anonymous)" if is_anonymous else ""
        logger.info(f"✅ Recorded {vote_type} vote{anon_text} for decision #{decision_id} by {voter_name}")
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
        decision.closed_at = datetime.utcnow()
        logger.info(
            f"🎉 Decision #{decision_id} APPROVED! "
            f"({decision.approval_count}/{decision.approval_threshold})"
        )
    
    # Check if threshold reached for rejection
    elif decision.rejection_count >= decision.approval_threshold:
        decision.status = "rejected"
        decision.closed_at = datetime.utcnow()
        logger.info(
            f"❌ Decision #{decision_id} REJECTED! "
            f"({decision.rejection_count}/{decision.approval_threshold})"
        )
    
    try:
        db.commit()
        db.refresh(decision)
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
    is_anonymous: bool = False,
) -> Tuple[bool, str, Optional[Decision]]:
    """
    Orchestrate the complete vote transaction.
    Returns: (success: bool, message: str, updated_decision: Optional[Decision])
    """
    # 1. Get and validate decision
    decision = get_decision_by_id(db, decision_id)
    if decision is None:
        return False, f"❌ Decision #{decision_id} not found", None

    # 2. Check if decision is still pending
    if decision.status != "pending":
        return False, f"❌ Decision already closed (status: {decision.status.upper()})", None

    # 3. Validate vote type
    if vote_type not in VALID_VOTE_TYPES:
        return False, f"❌ Invalid vote type: {vote_type}", None

    # 4. Check for duplicate vote
    if check_if_user_voted(db, decision_id, voter_id):
        return False, "❌ You already voted on this decision", None

    # 5. Create vote record
    vote = create_vote(
        db=db,
        decision_id=decision_id,
        voter_phone=voter_id,
        voter_name=voter_name,
        vote_type=vote_type,
        is_anonymous=is_anonymous,
    )

    if vote is None:
        return False, "❌ Unable to record vote. Please try again.", None

    # 6. Update counts and check if threshold reached
    updated_decision = update_vote_counts_and_status(db, decision_id, vote_type)

    if updated_decision is None:
        return False, "❌ Failed to update vote counts", None

    # Success
    return True, "✅ Vote recorded successfully", updated_decision