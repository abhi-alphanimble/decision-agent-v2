"""
Integration tests for decision handlers
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Decision
from app.handlers.decision_handlers import handle_propose_command, MVP_GROUP_SIZE, MVP_APPROVAL_THRESHOLD
from app.command_parser import parse_message
from database.base import Base

# Create in-memory test database
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


def test_propose_valid_text(db):
    """Test proposing with valid text"""
    parsed = parse_message('propose "Should we order pizza for lunch?"')
    
    response = handle_propose_command(
        parsed=parsed,
        user_id="U12345",
        user_name="Test User",
        channel_id="C12345",
        db=db
    )
    
    assert "✅" in response["text"]
    
    # Check database
    decision = db.query(Decision).first()
    assert decision is not None
    assert decision.text == "Should we order pizza for lunch?"
    assert decision.status == "pending"
    assert decision.proposer_phone == "U12345"
    assert decision.proposer_name == "Test User"
    assert decision.group_size_at_creation == MVP_GROUP_SIZE
    assert decision.approval_threshold == MVP_APPROVAL_THRESHOLD
    assert decision.approval_count == 0
    assert decision.rejection_count == 0


def test_propose_too_short(db):
    """Test proposing with text too short"""
    parsed = parse_message('propose "Short"')
    
    response = handle_propose_command(
        parsed=parsed,
        user_id="U12345",
        user_name="Test User",
        channel_id="C12345",
        db=db
    )
    
    assert "❌" in response["text"]
    assert "too short" in response["text"].lower()
    assert "10 characters" in response["text"].lower()
    
    # Check nothing was created
    decision = db.query(Decision).first()
    assert decision is None


def test_propose_too_long(db):
    """Test proposing with text too long"""
    long_text = "A" * 501
    parsed = parse_message(f'propose "{long_text}"')
    
    response = handle_propose_command(
        parsed=parsed,
        user_id="U12345",
        user_name="Test User",
        channel_id="C12345",
        db=db
    )
    
    assert "❌" in response["text"]
    assert "too long" in response["text"].lower()
    assert "500 characters" in response["text"].lower()
    
    # Check nothing was created
    decision = db.query(Decision).first()
    assert decision is None


def test_propose_minimum_length(db):
    """Test proposing with exactly 10 characters"""
    parsed = parse_message('propose "1234567890"')
    
    response = handle_propose_command(
        parsed=parsed,
        user_id="U12345",
        user_name="Test User",
        channel_id="C12345",
        db=db
    )
    
    assert "✅" in response["text"]
    
    decision = db.query(Decision).first()
    assert decision is not None
    assert len(decision.text) == 10


def test_propose_maximum_length(db):
    """Test proposing with exactly 500 characters"""
    text_500 = "A" * 500
    parsed = parse_message(f'propose "{text_500}"')
    
    response = handle_propose_command(
        parsed=parsed,
        user_id="U12345",
        user_name="Test User",
        channel_id="C12345",
        db=db
    )
    
    assert "✅" in response["text"]
    
    decision = db.query(Decision).first()
    assert decision is not None
    assert len(decision.text) == 500


def test_multiple_proposals(db):
    """Test creating multiple proposals"""
    for i in range(3):
        parsed = parse_message(f'propose "Proposal number {i + 1} for testing"')
        
        response = handle_propose_command(
            parsed=parsed,
            user_id=f"U{i}",
            user_name=f"User {i}",
            channel_id="C12345",
            db=db
        )
        
        assert "✅" in response["text"]
    
    # Check all were created
    decisions = db.query(Decision).all()
    assert len(decisions) == 3