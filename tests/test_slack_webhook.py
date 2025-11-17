
"""
Test Slack webhook endpoint locally.
"""
import pytest
import requests
import hmac
import hashlib
import time

BASE_URL = "http://localhost:8000"
SIGNING_SECRET = "a342f7f89f58291a6445976266db1cdd"  # Get from .env

pytest.skip("Manual Slack webhook smoke test; skipped during automated pytest runs.", allow_module_level=True)


def create_slack_signature(body: str, timestamp: str) -> str:
    """Create valid Slack signature."""
    sig_basestring = f"v0:{timestamp}:{body}"
    signature = "v0=" + hmac.new(
        SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256,
    ).hexdigest()
    return signature


def run_slash_command_test():
    """Manually exercise the slash command webhook against a running server."""
    print("\n" + "=" * 60)
    print("Testing Slash Command Webhook")
    print("=" * 60)

    timestamp = str(int(time.time()))
    body = 'command=/decision&text=propose "Test decision"&user_id=U123&user_name=TestUser&channel_id=C123&channel_name=general'
    signature = create_slack_signature(body, timestamp)

    headers = {
        "X-Slack-Signature": signature,
        "X-Slack-Request-Timestamp": timestamp,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post(f"{BASE_URL}/slack/slash", data=body, headers=headers, timeout=10)

    print(f"Status: {response.status_code}")
    try:
        print("Response JSON:", response.json())
    except ValueError:
        print("Response Text:", response.text)


if __name__ == "__main__":
    run_slash_command_test()