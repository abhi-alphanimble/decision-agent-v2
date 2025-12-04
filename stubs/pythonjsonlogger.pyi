# Stub for pythonjsonlogger
from typing import Any
import logging

class JsonFormatter(logging.Formatter):
    def __init__(self, fmt: str = ...) -> None: ...
    def format(self, record: logging.LogRecord) -> str: ...
