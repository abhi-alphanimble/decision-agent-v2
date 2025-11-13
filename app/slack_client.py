
import hmac
import hashlib
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from app.config import config
import logging

logger = logging.getLogger(__name__)

class SlackClient:
    def __init__(self):
        """Initialize Slack WebClient with bot token"""
        self.client = WebClient(token=config.SLACK_BOT_TOKEN)
        self.signing_secret = config.SLACK_SIGNING_SECRET
        
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
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks
            )
            logger.info(f"Message sent to channel {channel}")
            return response
        except SlackApiError as e:
            logger.error(f"Error sending message: {e.response['error']}")
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
            response = self.client.chat_postMessage(
                channel=channel,
                thread_ts=thread_ts,
                text=text,
                blocks=blocks
            )
            logger.info(f"Thread reply sent to channel {channel}")
            return response
        except SlackApiError as e:
            logger.error(f"Error sending thread reply: {e.response['error']}")
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
            response = self.client.chat_postEphemeral(
                channel=channel,
                user=user,
                text=text
            )
            logger.info(f"Ephemeral message sent to user {user}")
            return response
        except SlackApiError as e:
            logger.error(f"Error sending ephemeral message: {e.response['error']}")
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
            response = self.client.chat_update(
                channel=channel,
                ts=ts,
                text=text,
                blocks=blocks
            )
            logger.info(f"Message updated in channel {channel}")
            return response
        except SlackApiError as e:
            logger.error(f"Error updating message: {e.response['error']}")
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
            response = self.client.users_info(user=user_id)
            return response['user']
        except SlackApiError as e:
            logger.error(f"Error getting user info: {e.response['error']}")
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
            response = self.client.conversations_info(channel=channel_id)
            return response['channel']
        except SlackApiError as e:
            logger.error(f"Error getting channel info: {e.response['error']}")
            raise

# Global Slack client instance
slack_client = SlackClient()
