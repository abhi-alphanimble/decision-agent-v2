"""
Slack client for API interactions with multi-workspace support.

In a distributed app, each workspace has its own bot token stored in the database.
This module provides utilities to get workspace-specific clients.
"""

import hmac
import hashlib
import time
import os
from typing import Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from sqlalchemy.orm import Session
from ..config import config
from ..config.logging import get_context_logger
from ..utils.encryption import decrypt_token

logger = get_context_logger(__name__)


# When running tests, avoid calling the real Slack API
def _is_test_mode() -> bool:
    return bool(os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING"))


class SlackClient:
    """
    Slack client wrapper with signature verification.
    
    For multi-workspace apps, use get_client_for_team() to get a workspace-specific
    WebClient instead of using this global instance.
    """
    client: Optional[WebClient]
    signing_secret: str
    
    def __init__(self):
        """Initialize Slack client for signature verification.
        
        Note: In multi-workspace mode, we don't create a default WebClient.
        Use get_client_for_team() to get workspace-specific clients.
        """
        self.client = None
        self.signing_secret = config.SLACK_SIGNING_SECRET or ""
        
    def _get_client(self) -> WebClient:
        """Get the WebClient, raising if not initialized."""
        if self.client is None:
            raise RuntimeError(
                "Slack WebClient not initialized. "
                "For multi-workspace apps, use get_client_for_team(team_id, db) instead."
            )
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
        if not self.signing_secret:
            logger.warning("No signing secret configured - skipping signature verification")
            return True
            
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


class WorkspaceSlackClient:
    """
    Slack client for a specific workspace.
    
    Wraps WebClient with helper methods for common operations.
    """
    
    def __init__(self, token: str, team_id: str):
        """Initialize with workspace-specific token."""
        self.client = WebClient(token=token)
        self.team_id = team_id
        self.logger = get_context_logger(__name__, team_id=team_id)
    
    def send_message(self, channel: str, text: str, blocks=None) -> dict:
        """Send a message to a Slack channel."""
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks
            )
            self.logger.info("Message sent to channel", extra={"channel_id": channel})
            return response
        except SlackApiError as e:
            self.logger.exception("Error sending message: %s", e.response.get('error') if hasattr(e, 'response') else str(e))
            raise
    
    def send_thread_reply(self, channel: str, thread_ts: str, text: str, blocks=None) -> dict:
        """Send a reply in a message thread."""
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                thread_ts=thread_ts,
                text=text,
                blocks=blocks
            )
            self.logger.info("Thread reply sent to channel", extra={"channel_id": channel})
            return response
        except SlackApiError as e:
            self.logger.exception("Error sending thread reply: %s", e.response.get('error') if hasattr(e, 'response') else str(e))
            raise
    
    def send_ephemeral_message(self, channel: str, user: str, text: str) -> dict:
        """Send an ephemeral message (only visible to one user)."""
        try:
            response = self.client.chat_postEphemeral(
                channel=channel,
                user=user,
                text=text
            )
            self.logger.info("Ephemeral message sent", extra={"channel_id": channel, "user_id": user})
            return response
        except SlackApiError as e:
            self.logger.exception("Error sending ephemeral message: %s", e.response.get('error') if hasattr(e, 'response') else str(e))
            raise
    
    def update_message(self, channel: str, ts: str, text: str, blocks=None) -> dict:
        """Update an existing message."""
        try:
            response = self.client.chat_update(
                channel=channel,
                ts=ts,
                text=text,
                blocks=blocks
            )
            self.logger.info("Message updated in channel", extra={"channel_id": channel})
            return response
        except SlackApiError as e:
            self.logger.exception("Error updating message: %s", e.response.get('error') if hasattr(e, 'response') else str(e))
            raise
    
    def get_user_info(self, user_id: str) -> dict:
        """Get information about a user."""
        try:
            response = self.client.users_info(user=user_id)
            self.logger.debug("Fetched user info", extra={"user_id": user_id})
            return response['user']
        except SlackApiError as e:
            self.logger.exception("Error getting user info: %s", e.response.get('error') if hasattr(e, 'response') else str(e))
            raise
    
    def get_channel_members_count(self, channel_id: str) -> int:
        """
        Get the number of HUMAN members in a channel (excluding bots).
        """
        try:
            response = self.client.conversations_info(
                channel=channel_id, 
                include_num_members=True
            )
            channel = response.get('channel', {})
            total_members = channel.get('num_members', 0)
            
            if total_members == 0:
                self.logger.warning(f"num_members not available, fetching members list for {channel_id}")
                members_response = self.client.conversations_members(
                    channel=channel_id, 
                    limit=1000
                )
                total_members = len(members_response.get('members', []))
            
            # Subtract 1 for the bot itself
            human_count = max(1, total_members - 1)
            
            self.logger.info("Channel members counted", extra={
                "channel_id": channel_id, 
                "total_members": total_members,
                "human_count": human_count,
            })
            return human_count

        except SlackApiError as e:
            self.logger.exception("Error getting channel members count: %s", e.response.get('error') if hasattr(e, 'response') else str(e))
            raise
    
    def get_channel_info(self, channel_id: str) -> dict:
        """Get information about a channel."""
        try:
            response = self.client.conversations_info(channel=channel_id)
            self.logger.debug("Fetched channel info", extra={"channel_id": channel_id})
            return response['channel']
        except SlackApiError as e:
            self.logger.exception("Error getting channel info: %s", e.response.get('error') if hasattr(e, 'response') else str(e))
            raise
    
    def is_bot_member_of_channel(self, channel_id: str) -> bool:
        """
        Check if this bot is a member of the specified channel.
        
        Args:
            channel_id: The Slack channel ID to check
            
        Returns:
            True if the bot is a member of the channel, False otherwise
        """
        try:
            # Get the bot's user ID
            auth_response = self.client.auth_test()
            bot_user_id = auth_response.get('user_id')
            
            if not bot_user_id:
                self.logger.warning("Could not determine bot user ID")
                return False
            
            # Get channel members (paginated, but we just need to check membership)
            # Use a cursor-based loop to handle large channels
            cursor = None
            while True:
                response = self.client.conversations_members(
                    channel=channel_id,
                    cursor=cursor,
                    limit=200
                )
                
                members = response.get('members', [])
                if bot_user_id in members:
                    self.logger.debug("Bot is a member of channel", extra={"channel_id": channel_id, "bot_user_id": bot_user_id})
                    return True
                
                # Check if there are more pages
                cursor = response.get('response_metadata', {}).get('next_cursor')
                if not cursor:
                    break
            
            self.logger.debug("Bot is NOT a member of channel", extra={"channel_id": channel_id, "bot_user_id": bot_user_id})
            return False
            
        except SlackApiError as e:
            error_code = e.response.get('error') if hasattr(e, 'response') else str(e)
            # 'not_in_channel' or 'channel_not_found' means bot is not in the channel
            if error_code in ['not_in_channel', 'channel_not_found']:
                self.logger.debug("Bot is not in channel (error: %s)", error_code, extra={"channel_id": channel_id})
                return False
            self.logger.exception("Error checking bot channel membership: %s", error_code)
            raise

    def revoke_token(self) -> bool:
        """Revoke the bot token for this workspace."""
        try:
            response = self.client.auth_revoke()
            self.logger.info("Bot token revoked successfully")
            return response.get('ok', False)
        except SlackApiError as e:
            self.logger.warning("Error revoking bot token: %s", e.response.get('error') if hasattr(e, 'response') else str(e))
            return False
        except Exception as e:
            self.logger.error("Unexpected error revoking bot token: %s", str(e))
            return False


def get_client_for_team(team_id: str, db: Session) -> Optional[WorkspaceSlackClient]:
    """
    Get a Slack client for a specific team/workspace.
    
    Fetches the bot token from the database and creates a workspace-specific client.
    
    Args:
        team_id: Slack team/workspace ID
        db: Database session
        
    Returns:
        WorkspaceSlackClient for the team, or None if not found/installed
    """
    from ..models import SlackInstallation
    
    try:
        installation = db.query(SlackInstallation).filter(
            SlackInstallation.team_id == team_id
        ).first()
        
        if not installation:
            logger.warning(f"No installation found for team {team_id}")
            return None
        
        # Decrypt the token if it's encrypted
        token = decrypt_token(installation.access_token)
        
        if not token:
            logger.error(f"Failed to get token for team {team_id}")
            return None
        
        return WorkspaceSlackClient(token=token, team_id=team_id)
        
    except Exception as e:
        logger.error(f"Error getting client for team {team_id}: {e}")
        return None


def get_raw_client_for_team(team_id: str, db: Session) -> Optional[WebClient]:
    """
    Get a raw Slack WebClient for a specific team.
    
    Use this when you need the raw WebClient instead of the wrapper.
    
    Args:
        team_id: Slack team/workspace ID
        db: Database session
        
    Returns:
        WebClient for the team, or None if not found
    """
    workspace_client = get_client_for_team(team_id, db)
    if workspace_client:
        return workspace_client.client
    return None


# Global instance for signature verification only
# For sending messages, use get_client_for_team()
if _is_test_mode():
    # Provide a lightweight mock for tests
    class MockSlackClient:
        def __init__(self):
            self.signing_secret = "test_secret"

        def verify_slack_signature(self, body: str, timestamp: str, signature: str) -> bool:
            return True

    class MockWorkspaceClient:
        def __init__(self):
            pass

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
            return {"id": user_id, "name": "test-user", "real_name": "Test User"}

        def get_channel_members_count(self, channel_id: str) -> int:
            logger.debug("Mock get_channel_members_count called", extra={"channel_id": channel_id})
            return 10

        def get_channel_info(self, channel_id: str) -> dict:
            logger.debug("Mock get_channel_info called", extra={"channel_id": channel_id})
            return {"id": channel_id, "name": "test-channel"}

        def is_bot_member_of_channel(self, channel_id: str) -> bool:
            logger.debug("Mock is_bot_member_of_channel called", extra={"channel_id": channel_id})
            return True  # Default to True for tests

    slack_client = MockSlackClient()
    
    def get_client_for_team(team_id: str, db: Session = None) -> MockWorkspaceClient:
        """Mock version for tests."""
        return MockWorkspaceClient()
else:
    slack_client = SlackClient()
