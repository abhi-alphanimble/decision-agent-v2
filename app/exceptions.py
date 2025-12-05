class AppError(Exception):
    """Base class for application-specific errors."""

class DatabaseError(AppError):
    """Errors raised when DB operations fail in a predictable way."""

class AIError(AppError):
    """Errors related to AI provider interactions."""

class SlackError(AppError):
    """Errors related to Slack API operations."""

class ValidationError(AppError):
    """Input validation errors."""
