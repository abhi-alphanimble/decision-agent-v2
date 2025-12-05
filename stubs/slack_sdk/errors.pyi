# Stub for slack_sdk.errors
from typing import Any

class SlackApiError(Exception):
    def __init__(self, message: str, response: dict[str, Any]) -> None: ...
    response: dict[str, Any]
