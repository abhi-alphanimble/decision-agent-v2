"""
Slack integration package for multi-workspace apps.
"""
from .client import (
    slack_client,
    SlackClient,
    WorkspaceSlackClient,
    get_client_for_team,
    get_raw_client_for_team,
)

# Lazy load oauth to avoid circular imports
def slack_install():
    from .oauth import slack_install as _slack_install
    return _slack_install()

def slack_callback(*args, **kwargs):
    from .oauth import slack_callback as _slack_callback
    return _slack_callback(*args, **kwargs)

__all__ = [
    'slack_client',
    'SlackClient',
    'WorkspaceSlackClient',
    'get_client_for_team',
    'get_raw_client_for_team',
    'slack_install',
    'slack_callback',
]

