# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # ... other settings (Slack, etc.)

    # Database
    db_host: str = Field("localhost")
    db_port: int = Field(5432)
    db_name: str = Field("decision_agent")
    db_user: str = Field("agent_user")
    db_password: str = Field(...)

    @property
    def database_url(self) -> str:
        """Constructs the database URL with connection pooling."""
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
            f"?pool_size=5&max_overflow=10"
        )

settings = Settings()