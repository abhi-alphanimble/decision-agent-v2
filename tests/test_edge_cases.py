"""
Tests for edge cases
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Decision, Vote
from app.handlers.decision_handlers import (
    handle_propose_command,
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


def test_propose_too_short(db):
    """Test proposal text too short"""
    parsed = parse_message('propose "Short"')
    
    response = handle_propose_command(
        parsed=parsed,
        user_id="U001",
        user_name="Alice",
        channel_id="C001",
        db=db
    )
    
    # Should show error
    assert "❌" in response["text"]
    assert "too short" in response["text"].lower()
    assert "10 character" in response["text"].lower()
    
    # Should not create decision
    decisions = db.query(Decision).all()
    assert len(decisions) == 0


def test_propose_too_long(db):
    """Test proposal text too long"""
    long_text = "A" * 501
    parsed = parse_message(f'propose "{long_text}"')
    
    response = handle_propose_command(
        parsed=parsed,
        user_id="U001",
        user_name="Alice",
        channel_id="C001",
        db=db
    )
    
    # Should show error
    assert "❌" in response["text"]
    assert "too long" in response["text"].lower()
    assert "500 character" in response["text"].lower()
    
    # Should not create decision
    decisions = db.query(Decision).all()
    assert len(decisions) == 0


def test_approve_nonexistent_decision(db):
    """Test approving decision that doesn't exist"""
    parsed = parse_message("approve 999")
    
    response = handle_approve_command(
        parsed=parsed,
        user_id="U001",
        user_name="Alice",
        channel_id="C001",
        db=db
    )
    
    # Should show error
    assert "❌" in response["text"]
    assert "not found" in response["text"].lower()
    assert "999" in response["text"]


def test_approve_closed_decision(db):
    """Test approving already closed decision"""
    # Create and close a decision
    decision = crud.create_decision(
        db=db,
        text="Test decision",
        created_by="U001",           # <-- FIX: Changed from proposer_phone
        created_by_name="Alice",     # <-- FIX: Changed from proposer_name
        channel_id="C001",
        group_size_at_creation=MVP_GROUP_SIZE,
        approval_threshold=MVP_APPROVAL_THRESHOLD
    )
    
    decision.status = "approved"
    decision.approval_count = 6
    db.commit()
    
    # Try to vote
    parsed = parse_message(f"approve {decision.id}")
    
    response = handle_approve_command(
        parsed=parsed,
        user_id="U002",
        user_name="Bob",
        channel_id="C001",
        db=db
    )
    
    # Should show error
    assert "❌" in response["text"]
    assert "already closed" in response["text"].lower()
    assert "APPROVED" in response["text"]


def test_duplicate_vote_error(db):
    """Test duplicate vote shows proper error"""
    # Create decision
    decision = crud.create_decision(
        db=db,
        text="Test decision",
        created_by="U001",           # <-- FIX: Changed from proposer_phone
        created_by_name="Alice",     # <-- FIX: Changed from proposer_name
        channel_id="C001",
        group_size_at_creation=MVP_GROUP_SIZE,
        approval_threshold=MVP_APPROVAL_THRESHOLD
    )
    
    parsed = parse_message(f"approve {decision.id}")
    
    # First vote - should succeed
    response1 = handle_approve_command(
        parsed=parsed,
        user_id="U002",
        user_name="Bob",
        channel_id="C001",
        db=db
    )
    assert "✅" in response1["text"]
    
    # Second vote - should fail
    response2 = handle_approve_command(
        parsed=parsed,
        user_id="U002",
        user_name="Bob",
        channel_id="C001",
        db=db
    )
    
    # Should show error
    assert "❌" in response2["text"]
    assert "already voted" in response2["text"].lower()
    assert "APPROVE" in response2["text"]  # Shows original vote


def test_reject_nonexistent_decision(db):
    """Test rejecting decision that doesn't exist"""
    parsed = parse_message("reject 999")
    
    response = handle_reject_command(
        parsed=parsed,
        user_id="U001",
        user_name="Alice",
        channel_id="C001",
        db=db
    )
    
    # Should show error
    assert "❌" in response["text"]
    assert "not found" in response["text"].lower()


def test_reject_closed_decision(db):
    """Test rejecting already closed decision"""
    # Create and close a decision
    decision = crud.create_decision(
        db=db,
        text="Test decision",
        created_by="U001",           # <-- FIX: Changed from proposer_phone
        created_by_name="Alice",     # <-- FIX: Changed from proposer_name
        channel_id="C001",
        group_size_at_creation=MVP_GROUP_SIZE,
        approval_threshold=MVP_APPROVAL_THRESHOLD
    )
    
    decision.status = "rejected"
    decision.rejection_count = 6
    db.commit()
    
    # Try to vote
    parsed = parse_message(f"reject {decision.id}")
    
    response = handle_reject_command(
        parsed=parsed,
        user_id="U002",
        user_name="Bob",
        channel_id="C001",
        db=db
    )
    
    # Should show error
    assert "❌" in response["text"]
    assert "already closed" in response["text"].lower()
    assert "REJECTED" in response["text"]