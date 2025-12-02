import pytest
from unittest.mock import MagicMock, patch
from app.handlers.decision_handlers import handle_suggest_command
from app.command_parser import ParsedCommand, CommandType, DecisionAction
from app.models import Decision, Vote
from datetime import datetime

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_ai_client():
    with patch('app.handlers.decision_handlers.ai_client') as mock:
        yield mock

def test_handle_suggest_command_valid(mock_db, mock_ai_client):
    # Setup
    decision = Decision(
        id=42,
        text="Should we order pizza?",
        status="pending",
        proposer_name="Alice",
        created_at=datetime.utcnow(),
        approval_threshold=3,
        group_size_at_creation=5
    )
    mock_db.query.return_value.filter.return_value.first.return_value = decision
    # Mock crud.get_decision_by_id
    with patch('app.handlers.decision_handlers.crud.get_decision_by_id', return_value=decision):
        with patch('app.handlers.decision_handlers.crud.get_votes_by_decision', return_value=[]):
            mock_ai_client.suggest_next_steps.return_value = "Here are some suggestions..."
            
            parsed = ParsedCommand(
                command_type=CommandType.DECISION,
                action=DecisionAction.SUGGEST,
                args=[42],
                raw_text="suggest 42"
            )
            
            response = handle_suggest_command(parsed, "user1", "User 1", "C123", mock_db)
            
            assert "AI Suggestions for Decision #42" in response["text"]
            assert "Here are some suggestions..." in response["text"]
            mock_ai_client.suggest_next_steps.assert_called_once()

def test_handle_suggest_command_invalid_id(mock_db):
    parsed = ParsedCommand(
        command_type=CommandType.DECISION,
        action=DecisionAction.SUGGEST,
        args=["invalid"],
        raw_text="suggest invalid"
    )
    
    response = handle_suggest_command(parsed, "user1", "User 1", "C123", mock_db)
    assert "Invalid decision ID" in response["text"]

def test_handle_suggest_command_not_found(mock_db):
    with patch('app.handlers.decision_handlers.crud.get_decision_by_id', return_value=None):
        parsed = ParsedCommand(
            command_type=CommandType.DECISION,
            action=DecisionAction.SUGGEST,
            args=[999],
            raw_text="suggest 999"
        )
        
        response = handle_suggest_command(parsed, "user1", "User 1", "C123", mock_db)
        assert "Decision #999 not found" in response["text"]

def test_handle_suggest_command_ai_failure(mock_db, mock_ai_client):
    decision = Decision(id=42, status="pending", text="test")
    with patch('app.handlers.decision_handlers.crud.get_decision_by_id', return_value=decision):
        with patch('app.handlers.decision_handlers.crud.get_votes_by_decision', return_value=[]):
            mock_ai_client.suggest_next_steps.return_value = None
            
            parsed = ParsedCommand(
                command_type=CommandType.DECISION,
                action=DecisionAction.SUGGEST,
                args=[42],
                raw_text="suggest 42"
            )
            
            response = handle_suggest_command(parsed, "user1", "User 1", "C123", mock_db)
            assert "Unable to generate suggestions" in response["text"]
