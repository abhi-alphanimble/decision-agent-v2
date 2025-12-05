"""
Shim module for backwards compatibility.
Redirects to app.slack.client
"""
from app.slack.client import slack_client, SlackClient, get_client_for_team

__all__ = ['slack_client', 'SlackClient', 'get_client_for_team']
