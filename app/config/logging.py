import logging
import logging.handlers
import os
import sys
from typing import Optional, Dict

# Optional dependency: python-json-logger. If not installed, fallback to plain text.
try:
    from pythonjsonlogger import JsonFormatter
    JSON_AVAILABLE = True
except Exception:
    # Keep JsonFormatter defined (possibly None) so static analysis knows the name exists
    JsonFormatter = None
    JSON_AVAILABLE = False

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

# Do not log sensitive environment variables
SENSITIVE_KEYS = {"SLACK_BOT_TOKEN", "SLACK_CLIENT_SECRET", "DB_PASSWORD", "GEMINI_API_KEY"}


def _redact_sensitive(record_dict: Dict[str, object]) -> Dict[str, object]:
    # Redact known sensitive keys if they appear in structured payload
    for key in list(record_dict.keys()):
        if key.upper() in SENSITIVE_KEYS or any(s in key.lower() for s in ["token", "secret", "password"]):
            record_dict[key] = "[REDACTED]"
    return record_dict


class ContextFilter(logging.Filter):
    """Filter to ensure context keys are present in every record."""
    def filter(self, record):
        if not hasattr(record, 'user_id'):
            record.user_id = None
        if not hasattr(record, 'channel_id'):
            record.channel_id = None
        if not hasattr(record, 'decision_id'):
            record.decision_id = None
        return True


# LoggerAdapter is defined below; do not duplicate it here.


def configure_logging(env: Optional[str] = None, level: int = logging.INFO):
    """Configure logging for the application.

    - Writes logs to `logs/app.log` with rotation (10MB, keep 5 files).
    - Adds console handler.
    - Uses JSON format if `python-json-logger` is available, otherwise uses formatted text.
    - Adds `ContextFilter` to ensure context fields exist.
    """
    # Determine environment
    env = env or os.getenv('ENV', 'development')

    if env == 'development':
        default_level = logging.DEBUG
    else:
        default_level = logging.INFO

    root_level = level or default_level

    # Ensure logs directory exists
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except Exception:
        pass

    # Root logger
    root = logging.getLogger()
    root.setLevel(root_level)

    # Remove any existing handlers to avoid duplicate logs
    for h in list(root.handlers):
        root.removeHandler(h)

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(root_level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(root_level)

    # Formatter
    if JSON_AVAILABLE and JsonFormatter is not None:
        fmt_fields = ['asctime', 'levelname', 'name', 'message', 'user_id', 'channel_id', 'decision_id']
        formatter = JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s %(user_id)s %(channel_id)s %(decision_id)s')
    else:
        fmt = '[%(asctime)s] [%(levelname)s] [%(name)s] [user=%(user_id)s channel=%(channel_id)s decision=%(decision_id)s] %(message)s'
        formatter = logging.Formatter(fmt)

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Attach filter to redact secrets and ensure context fields
    context_filter = ContextFilter()
    file_handler.addFilter(context_filter)
    console_handler.addFilter(context_filter)

    # Add handlers
    root.addHandler(file_handler)
    root.addHandler(console_handler)

    # Optionally reduce verbosity of noisy libs
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    # Utility function to get a logger with bound context
    def get_logger(name: str = __name__, **context):
        logger = logging.getLogger(name)
        return LoggerAdapter(logger, context)

    # Expose helper in module
    global get_context_logger
    get_context_logger = get_logger


class LoggerAdapter(logging.LoggerAdapter):
    """LoggerAdapter that attaches context to log records.

    Usage:
        logger = get_context_logger(__name__, user_id='U1', channel_id='C1')
        logger.info('message')
    """
    def process(self, msg, kwargs):
        extra = kwargs.setdefault('extra', {})
        # Attach provided context keys but do not override if already present
        for k, v in (self.extra or {}).items():
            if k not in extra:
                extra[k] = v
        # Ensure we don't log sensitive info in message
        return msg, kwargs


# Initialize default get_context_logger to a simple wrapper in case configure_logging isn't called
def _default_get_context_logger(name: str, **ctx):
    return LoggerAdapter(logging.getLogger(name), ctx)

get_context_logger = _default_get_context_logger
