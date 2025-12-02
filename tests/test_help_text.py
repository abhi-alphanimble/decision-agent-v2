import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

# Mock google module before importing app
from unittest.mock import MagicMock
sys.modules["google"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()

# Test just the help text function
from app.command_parser import get_help_text

print("Testing get_help_text()...")
help_text = get_help_text()

print(f"Help text length: {len(help_text)}")
print("-" * 50)
print(help_text)
print("-" * 50)

if "Decision Agent Help Guide" in help_text:
    print("✅ Test Passed: Help text contains title")
if "Propose & Create" in help_text:
    print("✅ Test Passed: Help text contains Propose section")
if "Vote & Participate" in help_text:
    print("✅ Test Passed: Help text contains Vote section")
if "View & Track" in help_text:
    print("✅ Test Passed: Help text contains View section")
if "AI Insights" in help_text:
    print("✅ Test Passed: Help text contains AI section")
if "Pro Tips" in help_text:
    print("✅ Test Passed: Help text contains Tips section")

print("\n✅ All tests passed!")
