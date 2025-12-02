"""
App package initialization.

Configure basic logging early so modules that initialize on import
(e.g. the AI client) emit visible logs during application startup.
"""
import logging

# Configure minimal logging as early as possible
logging.basicConfig(
	level=logging.INFO,
	format='[%(asctime)s] %(levelname)s - %(message)s',
	datefmt='%Y-%m-%d %H:%M:%S'
)
