"""
Shim module for backwards compatibility.
Redirects to app.config.logging
"""
from app.config.logging import configure_logging, get_context_logger

__all__ = ['configure_logging', 'get_context_logger']
