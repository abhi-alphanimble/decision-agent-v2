import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.getcwd())

# Mock google module before importing app
sys.modules["google"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()

try:
    from app.handlers.decision_handlers import handle_help_command
    from app.command_parser import ParsedCommand, CommandType, DecisionAction
    print("✅ Imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def run_test():
    print("Running manual help command test...")
    
    mock_db = MagicMock()
    
    parsed = ParsedCommand(
        command_type=CommandType.HELP,
        action=None,
        args=[],
        raw_text="help"
    )
    
    # handle_help_command signature: (parsed, user_id, user_name, channel_id, db)
    response = handle_help_command(parsed, "user1", "User 1", "C123", mock_db)
    
    print(f"Response text length: {len(response['text'])}")
    print("-" * 20)
    print(response['text'])
    print("-" * 20)
    
    if "Decision Agent Help Guide" in response["text"]:
        print("✅ Test Passed: Help text contains expected title")
    else:
        print("❌ Test Failed: Help text missing title")

if __name__ == "__main__":
    run_test()
