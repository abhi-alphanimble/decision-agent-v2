import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.logging_config import configure_logging, get_context_logger

configure_logging(env=os.getenv('ENV','development'))
logger = get_context_logger(__name__, user_id='Utest', channel_id='Ctest')

logger.info('Test log entry from emit_log')
print('Wrote test log')
