from typing import Any# Stub package for slack_sdk













    def reactions_remove(self, channel: str, timestamp: str, name: str) -> dict[str, Any]: ...    def chat_update(self, channel: str, ts: str, text: str = ..., blocks: list[dict[str, Any]] = ...) -> dict[str, Any]: ...    def chat_postMessage(self, channel: str, text: str = ..., blocks: list[dict[str, Any]] = ...) -> dict[str, Any]: ...    def reactions_get(self, channel: str, timestamp: str) -> dict[str, Any]: ...    def reactions_add(self, channel: str, timestamp: str, name: str) -> dict[str, Any]: ...    def users_info(self, user: str) -> dict[str, Any]: ...    def conversations_info(self, channel: str) -> dict[str, Any]: ...    def conversations_members(self, channel: str) -> dict[str, Any]: ...    def auth_test(self) -> dict[str, Any]: ...    def __init__(self, token: str = ...) -> None: ...class WebClient: