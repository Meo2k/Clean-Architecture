import os
import json
from typing import Any, List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_CONFIG_PATH = os.path.join(ROOT_PATH, ".env")


class Settings(BaseSettings):
    """
    Centralized application settings using Pydantic Settings.
    Loads configuration from environment variables and the .env file.
    """
    model_config = SettingsConfigDict(
        env_file=ENV_CONFIG_PATH,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application Information
    SYS_NAME: str = "Clean Arch"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "DEVELOPMENT"

    # CORS & Security
    FE_URL: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    IS_HTTPS: bool = False
    SAME_SITE: str = "lax"

    # JWT Configuration
    ACCESS_TOKEN_KEY: str
    REFRESH_TOKEN_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 20
    REFRESH_TOKEN_EXPIRE_DAYS: int = 15
    ALGORITHM_HASH: str = "HS256"

    # User Business Rules
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    LOCK_DURATION_MINUTES: int = 30

    # Email Service
    EMAIL_USER: Optional[str] = None
    EMAIL_PASSWORD: Optional[str] = None

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    SYS_LOG_PATH: str = "./logs"

    # Database Configuration
    DATABASE_URL: str

    @field_validator("FE_URL", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, set, tuple)):
            return [str(i).strip() for i in v if i]
        raise ValueError(f"Configuration must be a list, got {type(v).__name__}")


# Initialize singleton instance
settings = Settings()

__all__ = ["Settings", "settings", "ROOT_PATH"]
