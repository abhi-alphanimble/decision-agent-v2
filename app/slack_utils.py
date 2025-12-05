"""
Shim module for backwards compatibility.
Redirects to app.utils.slack_parsing
"""
from app.utils.slack_parsing import parse_slash_command, parse_event_message

__all__ = ['parse_slash_command', 'parse_event_message']
