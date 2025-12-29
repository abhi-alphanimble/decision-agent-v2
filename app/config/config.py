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
    
    # Database
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD')  # Required
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'decision_agent')
    
    # Slack - OAuth credentials (tokens are stored per-workspace in DB)
    SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')  # Required
    SLACK_APP_ID = os.getenv('SLACK_APP_ID', '')
    SLACK_CLIENT_ID = os.getenv('SLACK_CLIENT_ID')  # Required
    SLACK_CLIENT_SECRET = os.getenv('SLACK_CLIENT_SECRET')  # Required
    
    # Token encryption for secure storage
    TOKEN_ENCRYPTION_KEY = os.getenv('TOKEN_ENCRYPTION_KEY')  # Required - Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    
    # AI - Optional (LiteLLM with OpenRouter)
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
    
    # Zoho OAuth - Optional (for multi-tenant CRM integration)
    ZOHO_CLIENT_ID = os.getenv('ZOHO_CLIENT_ID', '')
    ZOHO_CLIENT_SECRET = os.getenv('ZOHO_CLIENT_SECRET', '')
    ZOHO_ACCOUNTS_URL = os.getenv('ZOHO_ACCOUNTS_URL', 'https://accounts.zoho.com')
    ZOHO_API_DOMAIN = os.getenv('ZOHO_API_DOMAIN', 'https://www.zohoapis.com')
    
    # Server
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = int(os.getenv('SERVER_PORT', '8000'))
    
    # App Base URL for OAuth redirects and links
    APP_BASE_URL = os.getenv('APP_BASE_URL', 'http://localhost:8000')
    
    @property
    def DATABASE_URL(self) -> str:
        """Build PostgreSQL connection URL."""
        if not self.DB_PASSWORD:
            raise ConfigurationError("DB_PASSWORD environment variable is required")
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    def validate_required_config(self) -> None:
        """
        Validate that all required configuration is present.
        Call this at startup to fail fast if configuration is missing.
        """
        errors = []
        
        if not self.DB_PASSWORD:
            errors.append("DB_PASSWORD is required")
        if not self.SLACK_SIGNING_SECRET:
            errors.append("SLACK_SIGNING_SECRET is required")
        if not self.SLACK_CLIENT_SECRET:
            errors.append("SLACK_CLIENT_SECRET is required")
        if not self.SLACK_CLIENT_ID:
            errors.append("SLACK_CLIENT_ID is required")
        if not self.TOKEN_ENCRYPTION_KEY:
            errors.append("TOKEN_ENCRYPTION_KEY is required")
        
        if errors:
            raise ConfigurationError(
                "Missing required configuration:\n" + "\n".join(f"  - {e}" for e in errors)
            )
    
    def validate_slack_config(self) -> bool:
        """Validate that Slack OAuth configuration is present."""
        if not self.SLACK_SIGNING_SECRET:
            raise ConfigurationError("SLACK_SIGNING_SECRET not set in environment")
        if not self.SLACK_CLIENT_ID:
            raise ConfigurationError("SLACK_CLIENT_ID not set in environment")
        if not self.SLACK_CLIENT_SECRET:
            raise ConfigurationError("SLACK_CLIENT_SECRET not set in environment")
        return True
    
    @property
    def is_test_mode(self) -> bool:
        """Check if running in test mode."""
        return bool(os.getenv('PYTEST_CURRENT_TEST') or os.getenv('TESTING'))


# Global config instance
config = Config()

