
"""
Test Slack webhook endpoint locally
"""
import requests
import json
import hmac
import hashlib
import time

BASE_URL = "http://localhost:8000"
SIGNING_SECRET = "a342f7f89f58291a6445976266db1cdd"  # Get from .env

def create_slack_signature(body: str, timestamp: str) -> str:
    """Create valid Slack signature"""
    sig_basestring = f"v0:{timestamp}:{body}"
    signature = 'v0=' + hmac.new(
        SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature

def test_slash_command():
    """Test slash command webhook"""
    print("\n" + "="*60)
    print("Testing Slash Command Webhook")
    print("="*60)
    
    timestamp = str(int(time.time()))
    body = "command=/decision&text=propose \"Test decision\"&user_id=U123&user_name=TestUser&channel_id=C123&channel_name=general"
    signature = create