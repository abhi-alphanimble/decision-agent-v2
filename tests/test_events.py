"""
Test script to verify events endpoint works
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Test URL verification
response = client.post(
    "/slack/events",
    json={
        "type": "url_verification",
        "challenge": "test_challenge_123"
    }
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code == 200 and response.json().get("challenge") == "test_challenge_123":
    print("✅ Events endpoint working correctly!")
else:
    print("❌ Events endpoint not working!")
    print(f"Expected: {{'challenge': 'test_challenge_123'}}")
    print(f"Got: {response.json()}")