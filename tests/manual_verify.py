import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.getcwd())

# Mock google module before importing app
sys.modules["google"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()

try:
    from app.handlers.decision_handlers import handle_suggest_command
    from app.command_parser import ParsedCommand, CommandType, DecisionAction
    from app.models import Decision
    print("✅ Imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def run_test():
    print("Running manual test...")
    
    mock_db = MagicMock()
    
    # Mock AI Client
    with patch('app.handlers.decision_handlers.ai_client') as mock_ai:
        mock_ai.suggest_next_steps.return_value = "AI Suggestions"
        
        # Mock CRUD
        decision = Decision(id=42, status="pending", text="Test Decision", proposer_name="Tester", approval_threshold=3, group_size_at_creation=5)
        with patch('app.handlers.decision_handlers.crud.get_decision_by_id', return_value=decision):
            with patch('app.handlers.decision_handlers.crud.get_votes_by_decision', return_value=[]):
                
                parsed = ParsedCommand(
                    command_type=CommandType.DECISION,
                    action=DecisionAction.SUGGEST,
                    args=[42],
                    raw_text="suggest 42"
                )
                
                response = handle_suggest_command(parsed, "u1", "User", "c1", mock_db)
                print(f"Response: {response}")
                
                if "AI Suggestions" in response["text"]:
                    print("✅ Test Passed")
                else:
                    print("❌ Test Failed")

if __name__ == "__main__":
    run_test()
