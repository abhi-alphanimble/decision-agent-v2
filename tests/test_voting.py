"""
Integration tests for voting functionality
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Decision, Vote
from app.handlers.decision_handlers import (
    handle_approve_command, 
    handle_reject_command,
    MVP_GROUP_SIZE,
    MVP_APPROVAL_THRESHOLD
)
from app.command_parser import parse_message
from app import crud
from database.base import Base

# Test database
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_decision(db):
    """Create a sample decision for testing"""
    decision = crud.create_decision(
        db=db,
        channel_id="C001",
        text="Should we order pizza?",
        created_by="U001",
        created_by_name="Alice",
        group_size_at_creation=MVP_GROUP_SIZE,
        approval_threshold=MVP_APPROVAL_THRESHOLD
    )
    return decision


def test_approve_vote(db, sample_decision):
    """Test approving a decision"""
    parsed = parse_message("approve 1")
    
    response = handle_approve_command(
        parsed=parsed,
        user_id="U002",
        user_name="Bob",
        channel_id="C001",
        db=db
    )
    
    assert "✅" in response["text"]
    assert "Vote Recorded" in response["text"]
    
    # Check database
    decision = crud.get_decision_by_id(db, sample_decision.id)
    assert decision.approval_count == 1
    assert decision.rejection_count == 0
    assert decision.status == "pending"
    
    # Check vote was created
    vote = crud.get_vote_by_decision_and_voter(db, sample_decision.id, "U002")
    assert vote is not None
    assert vote.vote_type == "approve"
    assert vote.voter_name == "Bob"


def test_reject_vote(db, sample_decision):
    """Test rejecting a decision"""
    parsed = parse_message("reject 1")
    
    response = handle_reject_command(
        parsed=parsed,
        user_id="U002",
        user_name="Bob",
        channel_id="C001",
        db=db
    )
    
    assert "✅" in response["text"] or "❌" in response["text"]
    assert "Vote Recorded" in response["text"]
    
    # Check database
    decision = crud.get_decision_by_id(db, sample_decision.id)
    assert decision.approval_count == 0
    assert decision.rejection_count == 1
    assert decision.status == "pending"


def test_duplicate_vote(db, sample_decision):
    """Test voting twice on same decision"""
    parsed = parse_message("approve 1")
    
    # First vote
    response1 = handle_approve_command(
        parsed=parsed,
        user_id="U002",
        user_name="Bob",
        channel_id="C001",
        db=db
    )
    assert "✅" in response1["text"]
    
    # Second vote (should fail)
    response2 = handle_approve_command(
        parsed=parsed,
        user_id="U002",
        user_name="Bob",
        channel_id="C001",
        db=db
    )
    assert "❌" in response2["text"]
    assert "already voted" in response2["text"].lower()
    
    # Check only one vote exists
    decision = crud.get_decision_by_id(db, sample_decision.id)
    assert decision.approval_count == 1


def test_vote_on_nonexistent_decision(db):
    """Test voting on decision that doesn't exist"""
    parsed = parse_message("approve 999")
    
    response = handle_approve_command(
        parsed=parsed,
        user_id="U002",
        user_name="Bob",
        channel_id="C001",
        db=db
    )
    
    assert "❌" in response["text"]
    assert "not found" in response["text"].lower()


def test_decision_approved_at_threshold(db, sample_decision):
    """Test decision automatically approved when threshold reached"""
    # Cast 6 approval votes (threshold)
    for i in range(6):
        parsed = parse_message("approve 1")
        handle_approve_command(
            parsed=parsed,
            user_id=f"U{i+2}",
            user_name=f"User{i+2}",
            channel_id="C001",
            db=db
        )
    
    # Check status changed
    decision = crud.get_decision_by_id(db, sample_decision.id)
    assert decision.approval_count == 6
    assert decision.status == "approved"
    assert decision.closed_at is not None


def test_decision_rejected_at_threshold(db, sample_decision):
    """Test decision automatically rejected when threshold reached"""
    # Cast 6 rejection votes (threshold)
    for i in range(6):
        parsed = parse_message("reject 1")
        handle_reject_command(
            parsed=parsed,
            user_id=f"U{i+2}",
            user_name=f"User{i+2}",
            channel_id="C001",
            db=db
        )
    
    # Check status changed
    decision = crud.get_decision_by_id(db, sample_decision.id)
    assert decision.rejection_count == 6
    assert decision.status == "rejected"
    assert decision.closed_at is not None


def test_cannot_vote_on_closed_decision(db, sample_decision):
    """Test cannot vote on already closed decision"""
    # Close the decision manually
    sample_decision.status = "approved"
    db.commit()
    
    # Try to vote
    parsed = parse_message("approve 1")
    response = handle_approve_command(
        parsed=parsed,
        user_id="U002",
        user_name="Bob",
        channel_id="C001",
        db=db
    )
    
    assert "❌" in response["text"]
    assert "already closed" in response["text"].lower()


def test_anonymous_vote(db, sample_decision):
    """Test anonymous voting"""
    parsed = parse_message("approve 1 --anonymous")
    
    response = handle_approve_command(
        parsed=parsed,
        user_id="U002",
        user_name="Bob",
        channel_id="C001",
        db=db
    )
    
    assert "✅" in response["text"]
    assert "anonymously" in response["text"].lower()
    
    # Check vote is marked anonymous
    vote = crud.get_vote_by_decision_and_voter(db, sample_decision.id, "U002")
    assert vote.is_anonymous is True


def test_mixed_votes(db, sample_decision):
    """Test mixture of approve and reject votes"""
    # 3 approvals
    for i in range(3):
        parsed = parse_message("approve 1")
        handle_approve_command(
            parsed=parsed,
            user_id=f"UA{i}",
            user_name=f"Approver{i}",
            channel_id="C001",
            db=db
        )
    
    # 2 rejections
    for i in range(2):
        parsed = parse_message("reject 1")
        handle_reject_command(
            parsed=parsed,
            user_id=f"UR{i}",
            user_name=f"Rejecter{i}",
            channel_id="C001",
            db=db
        )
    
    # Check counts
    decision = crud.get_decision_by_id(db, sample_decision.id)
    assert decision.approval_count == 3
    assert decision.rejection_count == 2
    assert decision.status == "pending"