"""
Script to add close_decision_as_unreachable function to crud.py
"""

# Read the file
with open('app/crud.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the location to insert (after update_decision_status function)
insert_marker = """        logger.error("Database error in update_decision_status: %s", exc)
        db.rollback()
        return None


def get_pending_decisions_count"""

new_function = """        logger.error("Database error in update_decision_status: %s", exc)
        db.rollback()
        return None


def close_decision_as_unreachable(db: Session, decision_id: int) -> Optional[Decision]:
    \"\"\"
    Close a decision as unreachable due to insufficient channel members.
    Sets status to 'expired_unreachable' and closed_at timestamp.
    
    Args:
        db: Database session
        decision_id: ID of the decision to close
        
    Returns:
        Updated Decision object or None if not found
    \"\"\"
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    
    if decision is None:
        logger.warning(f"Decision #{decision_id} not found for unreachable closure")
        return None
    
    decision.status = "expired_unreachable"
    decision.closed_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(decision)
        logger.info(f"🔒 Closed decision #{decision_id} as unreachable")
        return decision
    except Exception as exc:
        logger.error(f"Database error in close_decision_as_unreachable: {exc}")
        db.rollback()
        return None


def get_pending_decisions_count"""

# Replace
content = content.replace(insert_marker, new_function)

# Write back
with open('app/crud.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully added close_decision_as_unreachable function to crud.py")
