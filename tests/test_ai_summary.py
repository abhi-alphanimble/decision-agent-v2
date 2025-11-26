import sys
import os
import io
from unittest.mock import MagicMock, patch
from datetime import datetime

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
sys.path.append(os.getcwd())

from app.command_parser import ParsedCommand, CommandType, DecisionAction
from app.models import Decision, Vote
from app.handlers.decision_handlers import handle_summarize_command

def test_summarize_handler():
    print("🧪 Testing handle_summarize_command...")
    
    # Mock DB session
    mock_db = MagicMock()
    
    # Mock decision
    mock_decision = Decision(
        id=42,
        text="Should we adopt Python?",
        status="pending",
        proposer_name="Alice",
        created_at=datetime.utcnow(),
        approval_threshold=3
    )
    
    # Mock votes
    mock_votes = [
        Vote(vote_type="approve", is_anonymous=False),
        Vote(vote_type="approve", is_anonymous=True),
        Vote(vote_type="reject", is_anonymous=False)
    ]
    
    # Setup mocks
    mock_db.query.return_value.filter.return_value.first.return_value = mock_decision
    
    # Mock crud functions
    with patch('app.crud.get_decision_by_id', return_value=mock_decision), \
         patch('app.crud.get_votes_by_decision', return_value=mock_votes), \
         patch('app.handlers.decision_handlers.ai_client') as mock_ai:
        
        # Setup AI mock
        mock_ai.summarize_decision.return_value = "This is a mock summary."
        
        # Test case 1: Valid ID
        parsed = ParsedCommand(
            command_type=CommandType.DECISION,
            action=DecisionAction.SUMMARIZE,
            args=[42],
            raw_text="summarize 42"
        )
        
        result = handle_summarize_command(parsed, "U1", "User", "C1", mock_db)
        
        result = handle_summarize_command(parsed, "U1", "User", "C1", mock_db)
        
        # Strip emojis for safe printing
        safe_text = result.get("text", "").encode('ascii', 'ignore').decode('ascii')
        
        if "AI Summary" in result.get("text", ""):
            print("Test Case 1 Passed: Summary generated")
        else:
            print(f"Test Case 1 Failed: {safe_text}")
            
        # Test case 2: Invalid ID
        parsed_invalid = ParsedCommand(
            command_type=CommandType.DECISION,
            action=DecisionAction.SUMMARIZE,
            args=["invalid"],
            raw_text="summarize invalid"
        )
        
        result_invalid = handle_summarize_command(parsed_invalid, "U1", "User", "C1", mock_db)
        
        # Strip emojis for safe printing
        safe_text_invalid = result_invalid.get("text", "").encode('ascii', 'ignore').decode('ascii')
        
        if "Invalid decision ID" in result_invalid.get("text", ""):
            print("Test Case 2 Passed: Invalid ID handled")
        else:
            print(f"Test Case 2 Failed: {safe_text_invalid}")

if __name__ == "__main__":
    test_summarize_handler()
