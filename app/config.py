from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional

ENV_PATH = Path(__file__).parent.parent / ".env"

class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables.
    """
    # Database (can provide assembled DB url or parts)
    database_url: Optional[str] = None
    database_hostname: Optional[str] = None
    database_port: Optional[int] = None
    database_username: Optional[str] = None
    database_password: Optional[str] = None
    database_name: Optional[str] = None

    # Security
    secret_key: str = "dev-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Firebase (optional): either full JSON string or local path
    firebase_credentials: Optional[str] = None

    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")

    @property
    def assembled_db_url(self) -> str:
        """
        Build the database URL from parts or use full URL if provided.
        """
        if self.database_url:
            return self.database_url
        return (
            f"postgresql://{self.database_username or 'postgres'}:"
            f"{self.database_password or 'postgres'}@"
            f"{self.database_hostname or '127.0.0.1'}:"
            f"{self.database_port or 5432}/"
            f"{self.database_name or 'carezio_db'}"
        )

settings = Settings()
