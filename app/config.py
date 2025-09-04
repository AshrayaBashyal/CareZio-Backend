from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional

ENV_PATH = Path(__file__).parent.parent / ".env"

class Settings(BaseSettings):
    # prefer DATABASE_URL if present
    database_url: Optional[str] = None

    # optional split parts (used locally only)
    database_hostname: Optional[str] = None
    database_port: Optional[int] = None
    database_username: Optional[str] = None
    database_password: Optional[str] = None
    database_name: Optional[str] = None

    # required for both local & render
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")

    @property
    def assembled_db_url(self) -> str:
        if self.database_url:
            return self.database_url
        # fallback if local dev
        return (
            f"postgresql://{self.database_username}:{self.database_password}"
            f"@{self.database_hostname}:{self.database_port}/{self.database_name}"
        )

settings = Settings()
