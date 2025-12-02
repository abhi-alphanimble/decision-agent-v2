import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.getcwd())

# Mock google module before importing app
sys.modules["google"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()

import pytest
from app.handlers.decision_handlers import handle_help_command
from app.command_parser import ParsedCommand, CommandType, DecisionAction

@pytest.fixture
def mock_db():
    return MagicMock()

def test_handle_help_command(mock_db):
    parsed = ParsedCommand(
        command_type=CommandType.HELP,
        action=None,
        args=[],
        raw_text="help"
    )
    
    response = handle_help_command(parsed, "user1", "User 1", "C123", mock_db)
    
    assert "Decision Agent Help Guide" in response["text"]
    assert "Propose & Create" in response["text"]
    assert "Vote & Participate" in response["text"]
    assert "View & Track" in response["text"]
    assert "AI Insights" in response["text"]
    assert "Pro Tips" in response["text"]
    assert response["response_type"] == "ephemeral"
