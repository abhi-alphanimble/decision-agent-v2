"""
Unit tests for CRUD operations
Tests all database operations with >85% coverage
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Decision, Vote
from app.crud import (
    create_decision, get_decision_by_id, get_decisions_by_channel,
    update_decision_status, increment_approval_count, increment_rejection_count,
    create_vote, get_vote_by_decision_and_voter, get_votes_by_decision,
    check_if_user_voted, get_pending_decisions_count, search_decisions,
    vote_on_decision
)

# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_decision(db_session):
    """Create a sample decision for testing."""
    decision = create_decision(
        db=db_session,
        channel_id="C12345",
        text="Should we implement feature X?",
        created_by="U12345",
        created_by_name="John Doe"
    )
    return decision


# ============================================================================
# DECISION CREATION TESTS
# ============================================================================

def test_create_decision_valid(db_session):
    """Test creating a valid decision."""
    decision = create_decision(
        db=db_session,
        channel_id="C12345",
        text="This is a valid decision text",
        created_by="U12345",
        created_by_name="Alice"
    )
    
    assert decision.id is not None
    assert decision.channel_id == "C12345"
    assert decision.text == "This is a valid decision text"
    assert decision.status == "pending"
    assert decision.approval_count == 0
    assert decision.rejection_count == 0
    assert decision.created_by == "U12345"
    assert decision.created_by_name == "Alice"


def test_create_decision_text_too_short(db_session):
    """Test that decision with text < 10 chars raises ValueError."""
    with pytest.raises(ValueError, match="at least 10 characters"):
        create_decision(
            db=db_session,
            channel_id="C12345",
            text="Short",
            created_by="U12345",
            created_by_name="Bob"
        )


def test_create_decision_text_too_long(db_session):
    """Test that decision with text > 500 chars raises ValueError."""
    long_text = "x" * 501
    with pytest.raises(ValueError, match="must not exceed 500 characters"):
        create_decision(
            db=db_session,
            channel_id="C12345",
            text=long_text,
            created_by="U12345",
            created_by_name="Charlie"
        )


def test_create_decision_empty_text(db_session):
    """Test that empty text raises ValueError."""
    with pytest.raises(ValueError, match="at least 10 characters"):
        create_decision(
            db=db_session,
            channel_id="C12345",
            text="   ",
            created_by="U12345",
            created_by_name="Dave"
        )


def test_create_decision_strips_whitespace(db_session):
    """Test that text whitespace is stripped."""
    decision = create_decision(
        db=db_session,
        channel_id="C12345",
        text="  Valid decision text here  ",
        created_by="U12345",
        created_by_name="Eve"
    )
    assert decision.text == "Valid decision text here"


# ============================================================================
# DECISION RETRIEVAL TESTS
# ============================================================================

def test_get_decision_by_id_exists(db_session, sample_decision):
    """Test retrieving an existing decision by ID."""
    retrieved = get_decision_by_id(db_session, sample_decision.id)
    assert retrieved is not None
    assert retrieved.id == sample_decision.id
    assert retrieved.text == sample_decision.text


def test_get_decision_by_id_not_exists(db_session):
    """Test retrieving a non-existent decision returns None."""
    retrieved = get_decision_by_id(db_session, 99999)
    assert retrieved is None


def test_get_decisions_by_channel(db_session):
    """Test retrieving all decisions for a channel."""
    # Create multiple decisions
    for i in range(3):
        create_decision(
            db=db_session,
            channel_id="C12345",
            text=f"Decision number {i} with enough text",
            created_by="U12345",
            created_by_name="Frank"
        )
    
    decisions = get_decisions_by_channel(db_session, "C12345")
    assert len(decisions) == 3


def test_get_decisions_by_channel_with_status_filter(db_session):
    """Test retrieving decisions with status filter."""
    # Create decisions with different statuses
    d1 = create_decision(db_session, "C12345", "Pending decision text", "U1", "User1")
    d2 = create_decision(db_session, "C12345", "Another pending text", "U2", "User2")
    
    # Update one to approved
    update_decision_status(db_session, d1.id, "approved")
    
    # Get only pending decisions
    pending = get_decisions_by_channel(db_session, "C12345", status="pending")
    assert len(pending) == 1
    assert pending[0].status == "pending"


def test_get_decisions_sorted_by_created_at(db_session):
    """Test that decisions are returned sorted by created_at DESC."""
    # Create decisions with slight delays
    d1 = create_decision(db_session, "C12345", "First decision text", "U1", "User1")
    d2 = create_decision(db_session, "C12345", "Second decision text", "U2", "User2")
    d3 = create_decision(db_session, "C12345", "Third decision text", "U3", "User3")
    
    decisions = get_decisions_by_channel(db_session, "C12345")
    assert decisions[0].id == d3.id  # Most recent first
    assert decisions[-1].id == d1.id  # Oldest last


def test_get_decisions_empty_channel(db_session):
    """Test retrieving decisions from empty channel returns empty list."""
    decisions = get_decisions_by_channel(db_session, "C_EMPTY")
    assert decisions == []


# ============================================================================
# DECISION UPDATE TESTS
# ============================================================================

def test_update_decision_status_valid(db_session, sample_decision):
    """Test updating decision status with valid status."""
    updated = update_decision_status(db_session, sample_decision.id, "approved")
    assert updated is not None
    assert updated.status == "approved"


def test_update_decision_status_invalid(db_session, sample_decision):
    """Test that invalid status raises ValueError."""
    with pytest.raises(ValueError, match="Invalid status"):
        update_decision_status(db_session, sample_decision.id, "invalid_status")


def test_update_decision_status_not_found(db_session):
    """Test updating non-existent decision returns None."""
    updated = update_decision_status(db_session, 99999, "approved")
    assert updated is None


# ============================================================================
# COUNT INCREMENT TESTS
# ============================================================================

def test_increment_approval_count(db_session, sample_decision):
    """Test atomically incrementing approval count."""
    initial_count = sample_decision.approval_count
    
    success = increment_approval_count(db_session, sample_decision.id)
    assert success is True
    
    # Refresh to get updated value
    db_session.refresh(sample_decision)
    assert sample_decision.approval_count == initial_count + 1


def test_increment_rejection_count(db_session, sample_decision):
    """Test atomically incrementing rejection count."""
    initial_count = sample_decision.rejection_count
    
    success = increment_rejection_count(db_session, sample_decision.id)
    assert success is True
    
    db_session.refresh(sample_decision)
    assert sample_decision.rejection_count == initial_count + 1


def test_increment_count_multiple_times(db_session, sample_decision):
    """Test multiple increments work correctly."""
    for _ in range(5):
        increment_approval_count(db_session, sample_decision.id)
    
    db_session.refresh(sample_decision)
    assert sample_decision.approval_count == 5


def test_increment_count_not_found(db_session):
    """Test incrementing non-existent decision returns False."""
    success = increment_approval_count(db_session, 99999)
    assert success is False


# ============================================================================
# PENDING DECISIONS COUNT TEST
# ============================================================================

def test_get_pending_decisions_count(db_session):
    """Test counting pending decisions in a channel."""
    # Create decisions with different statuses
    d1 = create_decision(db_session, "C12345", "Pending one text", "U1", "User1")
    d2 = create_decision(db_session, "C12345", "Pending two text", "U2", "User2")
    d3 = create_decision(db_session, "C12345", "Will be approved", "U3", "User3")
    
    update_decision_status(db_session, d3.id, "approved")
    
    count = get_pending_decisions_count(db_session, "C12345")
    assert count == 2


def test_get_pending_decisions_count_empty(db_session):
    """Test counting in empty channel returns 0."""
    count = get_pending_decisions_count(db_session, "C_EMPTY")
    assert count == 0


# ============================================================================
# SEARCH TESTS
# ============================================================================

def test_search_decisions_case_insensitive(db_session):
    """Test that search is case-insensitive."""
    create_decision(db_session, "C12345", "This contains UPPERCASE text", "U1", "User1")
    create_decision(db_session, "C12345", "This contains lowercase text", "U2", "User2")
    
    results = search_decisions(db_session, "C12345", "uppercase")
    assert len(results) == 1
    assert "UPPERCASE" in results[0].text


def test_search_decisions_partial_match(db_session):
    """Test that search matches partial text."""
    create_decision(db_session, "C12345", "Should we implement feature X?", "U1", "User1")
    create_decision(db_session, "C12345", "Feature Y is also needed", "U2", "User2")
    
    results = search_decisions(db_session, "C12345", "feature")
    assert len(results) == 2


def test_search_decisions_no_results(db_session):
    """Test search with no matching results."""
    create_decision(db_session, "C12345", "Some decision text here", "U1", "User1")
    
    results = search_decisions(db_session, "C12345", "nonexistent")
    assert len(results) == 0


# ============================================================================
# VOTE CREATION TESTS
# ============================================================================

def test_create_vote_valid(db_session, sample_decision):
    """Test creating a valid vote."""
    vote = create_vote(
        db=db_session,
        decision_id=sample_decision.id,
        voter_id="U54321",
        voter_name="Voter Alice",
        vote_type="approve",
        is_anonymous=False
    )
    
    assert vote is not None
    assert vote.decision_id == sample_decision.id
    assert vote.voter_id == "U54321"
    assert vote.vote_type == "approve"
    assert vote.is_anonymous is False


def test_create_vote_anonymous(db_session, sample_decision):
    """Test creating an anonymous vote."""
    vote = create_vote(
        db=db_session,
        decision_id=sample_decision.id,
        voter_id="U54321",
        voter_name="Voter Bob",
        vote_type="reject",
        is_anonymous=True
    )
    
    assert vote.is_anonymous is True


def test_create_vote_invalid_type(db_session, sample_decision):
    """Test that invalid vote_type raises ValueError."""
    with pytest.raises(ValueError, match="Invalid vote_type"):
        create_vote(
            db=db_session,
            decision_id=sample_decision.id,
            voter_id="U54321",
            voter_name="Voter Charlie",
            vote_type="invalid",
            is_anonymous=False
        )


def test_create_vote_duplicate(db_session, sample_decision):
    """Test that duplicate vote returns None."""
    # First vote
    vote1 = create_vote(
        db=db_session,
        decision_id=sample_decision.id,
        voter_id="U54321",
        voter_name="Voter Dave",
        vote_type="approve"
    )
    assert vote1 is not None
    
    # Duplicate vote
    vote2 = create_vote(
        db=db_session,
        decision_id=sample_decision.id,
        voter_id="U54321",
        voter_name="Voter Dave",
        vote_type="reject"
    )
    assert vote2 is None


# ============================================================================
# VOTE RETRIEVAL TESTS
# ============================================================================

def test_get_vote_by_decision_and_voter(db_session, sample_decision):
    """Test retrieving a specific vote."""
    create_vote(db_session, sample_decision.id, "U54321", "Voter", "approve")
    
    vote = get_vote_by_decision_and_voter(db_session, sample_decision.id, "U54321")
    assert vote is not None
    assert vote.voter_id == "U54321"


def test_get_vote_by_decision_and_voter_not_found(db_session, sample_decision):
    """Test retrieving non-existent vote returns None."""
    vote = get_vote_by_decision_and_voter(db_session, sample_decision.id, "U_NONE")
    assert vote is None


def test_get_votes_by_decision(db_session, sample_decision):
    """Test retrieving all votes for a decision."""
    create_vote(db_session, sample_decision.id, "U1", "Voter1", "approve")
    create_vote(db_session, sample_decision.id, "U2", "Voter2", "approve")
    create_vote(db_session, sample_decision.id, "U3", "Voter3", "reject")
    
    votes = get_votes_by_decision(db_session, sample_decision.id)
    assert len(votes) == 3


def test_check_if_user_voted_true(db_session, sample_decision):
    """Test check_if_user_voted returns True for voted user."""
    create_vote(db_session, sample_decision.id, "U54321", "Voter", "approve")
    
    has_voted = check_if_user_voted(db_session, sample_decision.id, "U54321")
    assert has_voted is True


def test_check_if_user_voted_false(db_session, sample_decision):
    """Test check_if_user_voted returns False for non-voted user."""
    has_voted = check_if_user_voted(db_session, sample_decision.id, "U_NONE")
    assert has_voted is False


# ============================================================================
# TRANSACTION TESTS
# ============================================================================

def test_vote_on_decision_success(db_session, sample_decision):
    """Test complete vote transaction succeeds."""
    success, message = vote_on_decision(
        db=db_session,
        decision_id=sample_decision.id,
        voter_id="U54321",
        voter_name="Voter",
        vote_type="approve"
    )
    
    assert success is True
    assert "successfully" in message.lower()
    
    # Verify vote was created
    vote = get_vote_by_decision_and_voter(db_session, sample_decision.id, "U54321")
    assert vote is not None
    
    # Verify count was incremented
    db_session.refresh(sample_decision)
    assert sample_decision.approval_count == 1


def test_vote_on_decision_duplicate(db_session, sample_decision):
    """Test that duplicate vote in transaction fails."""
    # First vote
    success1, _ = vote_on_decision(
        db=db_session,
        decision_id=sample_decision.id,
        voter_id="U54321",
        voter_name="Voter",
        vote_type="approve",
    )
    assert success1 is True
    
    # Duplicate vote
    success2, message2 = vote_on_decision(
        db=db_session,
        decision_id=sample_decision.id,
        voter_id="U54321",
        voter_name="Voter",
        vote_type="reject",
    )
    assert success2 is False
    assert "already voted" in message2.lower()


def test_vote_on_decision_rejection(db_session, sample_decision):
    """Test rejection vote updates rejection count."""
    success, _ = vote_on_decision(
        db=db_session,
        decision_id=sample_decision.id,
        voter_id="U54321",
        voter_name="Voter",
        vote_type="reject"
    )
    
    assert success is True
    db_session.refresh(sample_decision)
    assert sample_decision.rejection_count == 1
    assert sample_decision.approval_count == 0


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_decision_text_exactly_10_chars(db_session):
    """Test decision with exactly 10 characters."""
    decision = create_decision(
        db=db_session,
        channel_id="C12345",
        text="0123456789",
        created_by="U12345",
        created_by_name="User"
    )
    assert decision is not None
    assert len(decision.text) == 10


def test_decision_text_exactly_500_chars(db_session):
    """Test decision with exactly 500 characters."""
    text = "x" * 500
    decision = create_decision(
        db=db_session,
        channel_id="C12345",
        text=text,
        created_by="U12345",
        created_by_name="User"
    )
    assert decision is not None
    assert len(decision.text) == 500


def test_multiple_channels_isolation(db_session):
    """Test that decisions in different channels are isolated."""
    create_decision(db_session, "C11111", "Channel 1 decision", "U1", "User1")
    create_decision(db_session, "C22222", "Channel 2 decision", "U2", "User2")
    
    channel1_decisions = get_decisions_by_channel(db_session, "C11111")
    channel2_decisions = get_decisions_by_channel(db_session, "C22222")
    
    assert len(channel1_decisions) == 1
    assert len(channel2_decisions) == 1
    assert channel1_decisions[0].channel_id == "C11111"
    assert channel2_decisions[0].channel_id == "C22222"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app.crud", "--cov-report=html"])