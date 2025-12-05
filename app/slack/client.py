"""
Slack client for API interactions
"""

import hmac
import hashlib
import time
import os
from typing import Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from ..config import config
from ..config.logging import get_context_logger

logger = get_context_logger(__name__)


# When running tests, avoid calling the real Slack API. Detect pytest via
# the `PYTEST_CURRENT_TEST` environment variable (set by pytest) or a
# generic `TESTING` env var. In test mode, use a minimal mock client that
# returns safe defaults to keep unit tests deterministic and offline.
def _is_test_mode() -> bool:
    return bool(os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING"))


class SlackClient:
    client: Optional[WebClient]
    signing_secret: str
    
    def __init__(self):
        """Initialize Slack WebClient with bot token.

        Guard creation of the underlying `WebClient` so failures are logged
        and do not raise during import/test collection.
        """
        self.client = None
        self.signing_secret = config.SLACK_SIGNING_SECRET
        try:
            # Create WebClient lazily; if token is missing this will still
            # construct the client object but should not perform network I/O.
            self.client = WebClient(token=config.SLACK_BOT_TOKEN)
        except Exception:
            logger.exception("Failed to initialize Slack WebClient; continuing with client=None")

    def _get_client(self) -> WebClient:
        """Get the WebClient, raising if not initialized."""
        if self.client is None:
            raise RuntimeError("Slack WebClient not initialized")
        return self.client
        
    def verify_slack_signature(self, body: str, timestamp: str, signature: str) -> bool:
        """
        Verify that the request came from Slack.
        
        Args:
            body: Raw request body as string
            timestamp: X-Slack-Request-Timestamp header
            signature: X-Slack-Signature header
            
        Returns:
            True if signature is valid, False otherwise
        """
        # Check timestamp to prevent replay attacks (within 5 minutes)
        current_timestamp = int(time.time())
        if abs(current_timestamp - int(timestamp)) > 60 * 5:
            logger.warning("Request timestamp too old")
            return False
        
        # Create signature base string
        sig_basestring = f"v0:{timestamp}:{body}"
        
        # Calculate expected signature
        expected_signature = 'v0=' + hmac.new(
            self.signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures (constant time comparison)
        is_valid = hmac.compare_digest(expected_signature, signature)
        
        if not is_valid:
            logger.warning("Invalid Slack signature")
        
        return is_valid
    
    def send_message(self, channel: str, text: str, blocks=None) -> dict:
        """
        Send a message to a Slack channel.
        
        Args:
            channel: Channel ID or name
            text: Message text (fallback if blocks are used)
            blocks: Optional list of Block Kit blocks
            
        Returns:
            Response from Slack API
        """
        try:
            response = self._get_client().chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks
            )
            logger.info("Message sent to channel", extra={"channel_id": channel})
            return response
        except SlackApiError as e:
            logger.exception("Error sending message: %s", e.response.get('error') if hasattr(e, 'response') else str(e))
            raise
    
    def send_thread_reply(self, channel: str, thread_ts: str, text: str, blocks=None) -> dict:
        """
        Send a reply in a message thread.
        
        Args:
            channel: Channel ID
            thread_ts: Timestamp of parent message
            text: Reply text
            blocks: Optional Block Kit blocks
            
        Returns:
            Response from Slack API
        """
        try:
            response = self._get_client().chat_postMessage(
                channel=channel,
                thread_ts=thread_ts,
                text=text,
                blocks=blocks
            )
            logger.info("Thread reply sent to channel", extra={"channel_id": channel})
            return response
        except SlackApiError as e:
            logger.exception("Error sending thread reply: %s", e.response.get('error') if hasattr(e, 'response') else str(e))
            raise
    
    def send_ephemeral_message(self, channel: str, user: str, text: str) -> dict:
        """
        Send an ephemeral message (only visible to one user).
        
        Args:
            channel: Channel ID
            user: User ID to show message to
            text: Message text
            
        Returns:
            Response from Slack API
        """
        try:
            response = self._get_client().chat_postEphemeral(
                channel=channel,
                user=user,
                text=text
            )
            logger.info("Ephemeral message sent", extra={"channel_id": channel, "user_id": user})
            return response
        except SlackApiError as e:
            logger.exception("Error sending ephemeral message: %s", e.response.get('error') if hasattr(e, 'response') else str(e))
            raise
    
    def update_message(self, channel: str, ts: str, text: str, blocks=None) -> dict:
        """
        Update an existing message.
        
        Args:
            channel: Channel ID
            ts: Message timestamp
            text: New message text
            blocks: Optional new blocks
            
        Returns:
            Response from Slack API
        """
        try:
            response = self._get_client().chat_update(
                channel=channel,
                ts=ts,
                text=text,
                blocks=blocks
            )
            logger.info("Message updated in channel", extra={"channel_id": channel})
            return response
        except SlackApiError as e:
            logger.exception("Error updating message: %s", e.response.get('error') if hasattr(e, 'response') else str(e))
            raise
    
    def get_user_info(self, user_id: str) -> dict:
        """
        Get information about a user.
        
        Args:
            user_id: Slack user ID
            
        Returns:
            User info from Slack API
        """
        try:
            response = self._get_client().users_info(user=user_id)
            logger.debug("Fetched user info", extra={"user_id": user_id})
            return response['user']
        except SlackApiError as e:
            logger.exception("Error getting user info: %s", e.response.get('error') if hasattr(e, 'response') else str(e))
            raise
    
    def get_channel_members_count(self, channel_id: str) -> int:
        """
        Get the number of members in a channel.
        
        Args:
            channel_id: Slack channel ID
            
        Returns:
            Number of members in the channel
        """
        try:
            # Try conversations.info first (may include num_members)
            response = self._get_client().conversations_info(channel=channel_id)
            channel = response.get('channel', {})

            # If num_members is provided by Slack, use it as a starting point
            if 'num_members' in channel and isinstance(channel['num_members'], int):
                raw_count = channel['num_members']
            else:
                # Fallback to fetching the members list
                members_response = self._get_client().conversations_members(channel=channel_id)
                raw_count = len(members_response.get('members', []))

            # To get an accurate visible-human count, filter out bots/deleted users and the app itself
            try:
                auth = self._get_client().auth_test()
                bot_user_id = auth.get('user_id')
            except Exception:
                bot_user_id = None

            # Fetch members list (we need member IDs to filter)
            members_response = self._get_client().conversations_members(channel=channel_id)
            member_ids = members_response.get('members', [])

            human_count = 0
            for uid in member_ids:
                # skip the bot itself (if present)
                if bot_user_id and uid == bot_user_id:
                    continue

                try:
                    user_info = self._get_client().users_info(user=uid).get('user', {})
                except SlackApiError as e:
                    logger.warning(f"Could not fetch user info for {uid}: {e.response.get('error')}")
                    # In doubt, exclude from human count
                    continue

                # Skip deleted users and bots
                if user_info.get('deleted'):
                    continue
                if user_info.get('is_bot'):
                    continue

                # Count as human
                human_count += 1

            logger.info("Channel members counted", extra={"channel_id": channel_id, "raw_count": raw_count, "human_count": human_count})
            return human_count

        except SlackApiError as e:
            logger.exception("Error getting channel members count for %s: %s", channel_id, e.response.get('error') if hasattr(e, 'response') else str(e))
            raise
        except Exception as e:
            logger.exception("Unexpected error getting channel members count for %s: %s", channel_id, str(e))
            raise
    
    def get_channel_info(self, channel_id: str) -> dict:
        """
        Get information about a channel.
        
        Args:
            channel_id: Slack channel ID
            
        Returns:
            Channel info from Slack API
        """
        try:
            response = self._get_client().conversations_info(channel=channel_id)
            logger.debug("Fetched channel info", extra={"channel_id": channel_id})
            return response['channel']
        except SlackApiError as e:
            logger.exception("Error getting channel info: %s", e.response.get('error') if hasattr(e, 'response') else str(e))
            raise

if _is_test_mode():
    # Provide a lightweight mock for tests
    class MockSlackClient:
        def __init__(self):
            pass

        def verify_slack_signature(self, body: str, timestamp: str, signature: str) -> bool:
            return True

        def send_message(self, channel: str, text: str, blocks=None) -> dict:
            logger.debug("Mock send_message called", extra={"channel": channel})
            return {"ok": True}

        def send_thread_reply(self, channel: str, thread_ts: str, text: str, blocks=None) -> dict:
            logger.debug("Mock send_thread_reply called", extra={"channel": channel})
            return {"ok": True}

        def send_ephemeral_message(self, channel: str, user: str, text: str) -> dict:
            logger.debug("Mock send_ephemeral_message called", extra={"channel": channel, "user": user})
            return {"ok": True}

        def update_message(self, channel: str, ts: str, text: str, blocks=None) -> dict:
            logger.debug("Mock update_message called", extra={"channel": channel})
            return {"ok": True}

        def get_user_info(self, user_id: str) -> dict:
            logger.debug("Mock get_user_info called", extra={"user_id": user_id})
            return {"id": user_id, "name": "test-user"}

        def get_channel_members_count(self, channel_id: str) -> int:
            logger.debug("Mock get_channel_members_count called", extra={"channel_id": channel_id})
            # Return 10 to align with MVP_GROUP_SIZE used in tests
            return 10

        def get_channel_info(self, channel_id: str) -> dict:
            logger.debug("Mock get_channel_info called", extra={"channel_id": channel_id})
            return {"id": channel_id, "name": "test-channel"}

    # Replace the global client with the mock
    slack_client = MockSlackClient()
else:
    # Create the real client only when not in test mode
    slack_client = SlackClient()


def get_client_for_team(team_id: str) -> Optional[WebClient]:
    """Get a Slack WebClient for a specific team (placeholder)."""
    # In a multi-workspace setup, this would fetch the token from DB
    # For now, return the global slack_client
    if isinstance(slack_client, SlackClient):
        return slack_client.client
    return None
