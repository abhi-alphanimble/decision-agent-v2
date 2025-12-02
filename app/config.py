
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '1234')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'decision_agent')
    
    # Slack
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN', '')
    SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET', '')
    SLACK_APP_ID = os.getenv('SLACK_APP_ID', '')
    SLACK_CLIENT_ID = os.getenv('SLACK_CLIENT_ID', '')
    SLACK_CLIENT_SECRET = os.getenv('SLACK_CLIENT_SECRET', '')
    
    # AI
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Auto-close settings
    DECISION_TIMEOUT_HOURS = int(os.getenv('DECISION_TIMEOUT_HOURS', '48'))
    
    # Server
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = int(os.getenv('SERVER_PORT', '8000'))
    
    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    def validate_slack_config(self):
        """Validate that Slack configuration is present"""
        if not self.SLACK_BOT_TOKEN:
            raise ValueError("SLACK_BOT_TOKEN not set in environment")
        if not self.SLACK_SIGNING_SECRET:
            raise ValueError("SLACK_SIGNING_SECRET not set in environment")
        return True

config = Config()
