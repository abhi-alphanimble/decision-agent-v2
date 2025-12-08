"""
Application Configuration

Loads configuration from environment variables with validation.
Sensitive values have no defaults and will fail fast if not provided.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class ConfigurationError(Exception):
    """Raised when required configuration is missing."""
    pass


class Config:
    """Application configuration loaded from environment variables."""
    
    # Database - DB_PASSWORD has no default for security
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD')  # No default - must be set
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'decision_agent')
    
    # Slack - All sensitive values have no defaults
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')  # No default - must be set
    SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')  # No default - must be set
    SLACK_APP_ID = os.getenv('SLACK_APP_ID', '')
    SLACK_CLIENT_ID = os.getenv('SLACK_CLIENT_ID', '')
    SLACK_CLIENT_SECRET = os.getenv('SLACK_CLIENT_SECRET')  # No default - must be set
    
    # AI - Optional, empty string is acceptable
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Auto-close settings
    DECISION_TIMEOUT_HOURS = int(os.getenv('DECISION_TIMEOUT_HOURS', '48'))
    
    # Server
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = int(os.getenv('SERVER_PORT', '8000'))
    
    # Environment
    ENV = os.getenv('ENV', 'development')
    
    @property
    def DATABASE_URL(self) -> str:
        """Build PostgreSQL connection URL."""
        if not self.DB_PASSWORD:
            if self.ENV == 'development':
                # Allow empty password in development for local postgres
                return f"postgresql://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            raise ConfigurationError("DB_PASSWORD environment variable is required")
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    def validate_required_config(self) -> None:
        """
        Validate that all required configuration is present.
        Call this at startup to fail fast if configuration is missing.
        """
        errors = []
        
        # In production, require all sensitive values
        if self.ENV == 'production':
            if not self.DB_PASSWORD:
                errors.append("DB_PASSWORD is required in production")
            if not self.SLACK_BOT_TOKEN:
                errors.append("SLACK_BOT_TOKEN is required")
            if not self.SLACK_SIGNING_SECRET:
                errors.append("SLACK_SIGNING_SECRET is required")
            if not self.SLACK_CLIENT_SECRET:
                errors.append("SLACK_CLIENT_SECRET is required")
        
        if errors:
            raise ConfigurationError(
                "Missing required configuration:\n" + "\n".join(f"  - {e}" for e in errors)
            )
    
    def validate_slack_config(self) -> bool:
        """Validate that Slack configuration is present for API calls."""
        if not self.SLACK_BOT_TOKEN:
            raise ConfigurationError("SLACK_BOT_TOKEN not set in environment")
        if not self.SLACK_SIGNING_SECRET:
            raise ConfigurationError("SLACK_SIGNING_SECRET not set in environment")
        return True
    
    @property
    def is_test_mode(self) -> bool:
        """Check if running in test mode."""
        return bool(os.getenv('PYTEST_CURRENT_TEST') or os.getenv('TESTING'))


# Global config instance
config = Config()
